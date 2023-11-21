from sqlalchemy import func
from sqlalchemy.orm import Session

from .models import Memory
from . import models, schemas
from .database import engine, get_db

import openai
import uvicorn
from fastapi import FastAPI, Response, status, HTTPException, Depends
from typing import List
import time

from dotenv import load_dotenv, find_dotenv
import json
import os
import psycopg2

from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory, ConversationSummaryBufferMemory

import secrets

_ = load_dotenv(find_dotenv())

models.Base.metadata.create_all(bind=engine)

app = FastAPI(debug=True)

openai.api_key = os.environ['OPENAI_API_KEY']
# Generate a random secret key
secret_key = secrets.token_hex(199)
# Set it as the Flask application's secret key
app.secret_key = secret_key

# Heroku provides the DATABASE_URL environment variable
DATABASE_URL = os.environ['DATABASE_URL']

# Initialize an empty conversation chain
llm = ChatOpenAI(temperature=0.0, model="gpt-3.5-turbo-0301")  # Set your desired LLM model here
memory = ConversationBufferMemory()
conversation = ConversationChain(llm=llm, memory=memory, verbose=False)
memory_summary = ConversationSummaryBufferMemory(llm=llm, max_token_limit=19)


while True:
    try:
        conn = psycopg2.connect(
            f"postgresql://{os.environ['user']}:{os.environ['password']}@"
            f"{os.environ['host']}:{os.environ['port']}/{os.environ['database']}"
        )
        cursor = conn.cursor()
        print(f'Database connection was successful 😎\n')
        break
    except Exception as error:
        print(f'Connecting to database failed:\nError: {error} 😭\n')
        time.sleep(3)

## Create OMR table
#cursor.execute("""
#    CREATE TABLE IF NOT EXISTS omr (
#        id SERIAL PRIMARY KEY,
#        user_message TEXT,
#        llm_response TEXT,
#        conversations_summary TEXT,
#        published BOOLEAN,
#        rating INTEGER,
#        created_at TIMESTAMP
#    )
#""")
#conn.commit()

# Creating the SQL command to fetch all data from the OMR table
memory_db = "SELECT * FROM omr"
# Executing the query and fetching all the data
cursor.execute(memory_db)
conversations_datas = cursor.fetchall()
#print(f'conversations_datas:\n{conversations_datas[9]}\n')


def find_conversation_by_id(id):
    for converse in conversations_datas:
        if converse[0] == id:  # Assuming 'id' is the first column in the OMR table
            print(f'conversation by id: {converse}')
            return converse


def find_index_converse(id):
    for i, conv in enumerate(conversations_datas):
        if isinstance(conv, dict) and conv.get('id') == id:
            return i
        elif isinstance(conv, tuple) and conv[0] == id:
            return i
    return None


# Function to generate LLM response
def generate_llm_response(user_message):
    # Assuming 'conversation' is initialized as a ChatOpenAI object
    return conversation.predict(input=user_message)


@app.get("/", status_code=status.HTTP_201_CREATED)
async def root():
    return {"message: Be Good Doing Good By Acting Good ¡!¡": "Siisi Chacal 🔥👌🏿😇💪🏿🔥"}


@app.get("/all-conversation", status_code=status.HTTP_201_CREATED, response_model=List[schemas.MemoryResponse])
def get_posts(db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM memories""")
    # posts = cursor.fetchall()(db: Session = Depends(get_db)):
    histories = db.query(models.Memory).all()
    print(f'all-conversation:\n{histories} 👌🏿\n')
    return histories


@app.get("/conversation-summary", status_code=status.HTTP_201_CREATED)
def get_conversation_summary(db: Session = Depends(get_db)):

    conversation_summaries_all = [summary.conversations_summary for summary in db.query(models.Memory).all()]
    head_summaries = conversation_summaries_all[:3]
    tail_summaries = conversation_summaries_all[-3:]

    print(f'conversation_summaries_head:\n{head_summaries}\n\n'
          f'conversation_summaries_tail:\n{tail_summaries} 👌🏿\n')

    return {"conversation_summary_head": head_summaries, "conversation_summary_tail": tail_summaries}


@app.post("/start-conversation", status_code=status.HTTP_201_CREATED, response_model=schemas.MemoryCreate)
def start_conversation(omr: schemas.MemoryCreate, db: Session = Depends(get_db)):
    try:
        # Use SQLAlchemy ORM to insert a new record
        new_memo = Memory(**omr.model_dump())

        # Get LLM response using the user's message
        llm_response = generate_llm_response(omr.user_message)

        # Update the new_memo with the LLM response
        new_memo.llm_response = llm_response

        # Save the conversation context
        memory_summary.save_context({"input": omr.user_message}, {"output": llm_response})

        # Load the conversation context
        conversations_summary = memory_summary.load_memory_variables({})

        # Convert the dictionary to a JSON-formatted string
        conversations_summary_json = json.dumps(conversations_summary)

        print(f'omr.user_message:\n{omr.user_message}\n')
        print(f'llm_response:\n{llm_response}\n')
        print(f'conversations_summary:\n{conversations_summary_json}\n')

        # Set the conversation summary in the new_memo
        new_memo.conversations_summary = conversations_summary_json

        # Set the timestamp using the database server's time
        new_memo.created_at = func.now()

        db.add(new_memo)
        db.commit()
        db.refresh(new_memo)

        return new_memo
    except Exception as e:
        # Log the exception or print it for debugging
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/audio", status_code=status.HTTP_201_CREATED)
async def audio_response():
    return {"message: Be Good Doing Good By Acting Good ¡!¡": conversations_datas[-1:]}


@app.get("/conversation_by_id/{id}", status_code=status.HTTP_201_CREATED, response_model=schemas.MemoryResponse)
def get_conversation_by_id(id: int, db: Session = Depends(get_db)):

    converse = db.query(models.Memory).filter(models.Memory.id == id).first()
    if not converse:
        print(f'conversations_by_id: "{id}" was not found')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"conversations_by_id: '{id}' was not found'")

    # Use Pydantic's model.dict() to convert the SQLAlchemy model to a dictionary
    converse_dict = schemas.MemoryResponse(**converse.__dict__).model_dump()

    return converse_dict


@app.put("/update-conversation/{id}", response_model=schemas.MemoryResponse)
def upd_conversation(id: int, db: Session = Depends(get_db)):
    # Check if the conversation exists in the database
    existing_memory_query = db.query(models.Memory).filter(models.Memory.id == id)
    existing_memory = existing_memory_query.first()

    if existing_memory is None:
        print(f'Conversation with ID: {id} does not exist')
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID: {id} does not exist"
        )

    # Use Pydantic's model.dict() to convert the SQLAlchemy model to a dictionary
    memory_dict = schemas.MemoryResponse(**existing_memory.__dict__).model_dump()
    db.commit()

    # Logging the conversation update
    print(f'Conversation with ID: {id} updated:\n{memory_dict}')
    return memory_dict


@app.delete("/delete-conversation/{id}", status_code=status.HTTP_204_NO_CONTENT)
def del_conversation(id: int, db: Session = Depends(get_db)):
    del_converse = db.query(models.Memory).filter(models.Memory.id == id)

    if del_converse.first() is None:
        print(f'conversations_by_id: "{id}" does not exist')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"conversation with id: '{id}' does not exist")
    del_converse.delete(synchronize_session=False)
    db.commit()
    print(f'"message": "conversation was successfully deleted"')
    return Response(status_code=status.HTTP_204_NO_CONTENT)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
