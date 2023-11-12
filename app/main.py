import openai
from fastapi import FastAPI, Response, status, HTTPException
from pydantic import BaseModel
from typing import Optional

from dotenv import load_dotenv, find_dotenv
import os
import psycopg2

from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, validators
import secrets

app = FastAPI()

_ = load_dotenv(find_dotenv())

openai.api_key = os.environ['OPENAI_API_KEY']
# Generate a random secret key
secret_key = secrets.token_hex(199)
# Set it as the Flask application's secret key
app.secret_key = secret_key

# Initialize an empty conversation chain
llm = ChatOpenAI(temperature=0.0, model="gpt-3.5-turbo-0301")  # Set your desired LLM model here
memory = ConversationBufferMemory()
conversation = ConversationChain(llm=llm, memory=memory, verbose=False)


# Define a Flask form
class TextAreaForm(FlaskForm):
    writing_text = TextAreaField('Start Writing', [validators.InputRequired(message="Please enter text.")])
    submit = SubmitField()


class Memory(BaseModel):
    user_message: str
    llm_response: str
    conversations_summary: str
    published: bool = True
    rating: Optional[int] = None
    created_at: str


# Heroku provides the DATABASE_URL environment variable
DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = conn.cursor()

# Create OMR table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS OMR (
        id SERIAL PRIMARY KEY,
        user_message TEXT,
        llm_response TEXT,
        conversations_summary TEXT,
        published BOOLEAN,
        rating INTEGER,
        created_at TIMESTAMP
    )
""")
conn.commit()

# Creating the SQL command to fetch all data from the OMR table
memory_db = "SELECT * FROM OMR"

# Executing the query and fetching all the data
cursor.execute(memory_db)
conversations_datas = cursor.fetchall()


def find_conversation_by_id(id):
    for converse in conversations_datas:
        if converse[0] == id:  # Assuming 'id' is the first column in the OMR table
            print(f'conversation by id: {converse}')
            return converse


def find_index_converse(id):
    for i, conv in enumerate(conversations_datas):
        if isinstance(conv, dict) and conv.get('id') == id:
            return i
        elif isinstance(conv, tuple) and conv[0] == id:  # Assuming the ID is the first element in the tuple
            return i
    return None


@app.get("/", status_code=status.HTTP_201_CREATED)
async def root():
    print(f'Be Good\nDoing Good\nBy Acting Good ¡!¡:')
    return {"message": f"Be Good Doing Good By Acting Good ¡!¡\n{conversations_datas}\n¡!¡"}


# Function to generate LLM response
def generate_llm_response(user_message):
    # Assuming 'conversation' is initialized as a ChatOpenAI object
    return conversation.predict(input=user_message)


@app.post("/conversation", status_code=status.HTTP_201_CREATED)
def start_conversation(omr: Memory):
    user_message = omr.user_message

    # Use the LLM model to generate a response
    llm_response = generate_llm_response(user_message)

    memory_load = memory.load_memory_variables({})

    memory.save_context({"input": f"Summarize the whole {conversations_datas}:"}, {"output": f"{memory_load}"})

    # Log the conversation to the database
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO OMR (user_message, llm_response, conversations_summary, created_at) VALUES (%s, %s, %s, now())
        """,
        (user_message, llm_response, conversations_datas)
    )
    conn.commit()

    # Fetch the conversation ID and timestamp
    cursor.execute("SELECT id, created_at FROM OMR ORDER BY id DESC LIMIT 1")
    last_entry = cursor.fetchone()
    conversation_id, created_at = last_entry if last_entry else (None, None)

    # Format and return the conversation details
    conversation_dict = {
        "user_message": user_message,
        "llm_response": llm_response,
        "conversations_summary": conversations_datas,
        "published": True,
        "created_at": created_at.strftime('%Y-%m-%d %H:%M:%S') if created_at else None,
        "id": conversation_id
    }

    return {"conversation": conversation_dict}


@app.get("/conversation-summary", status_code=status.HTTP_201_CREATED)
def get_conversation_summary():
    print(f'conversation_summary:\n{conversations_datas}')
    return {f"conversation_summary": conversations_datas}


@app.get("/conversation_by_id/{id}", status_code=status.HTTP_201_CREATED)
def get_conversation_by_id(id: int, response: Response):
    converse = find_conversation_by_id(id)
    if not converse:
        print(f'conversations_by_id: "{id}" was not found')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"conversations_by_id: '{id}' was not found'")
    return {"conversations_by_id:" f"{converse}"}


@app.put("/update-conversation/{id}")
def upd_conversation(id: int, memory: Memory, response: Response):
    index = find_index_converse(id)
    if index is None:
        print(f'Conversation with ID: {id} does not exist')
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID: {id} does not exist"
        )

    # Update the conversation details in the list
    conversations_datas[index] = (
        memory.user_message,
        memory.llm_response,
        memory.conversations_summary,
        memory.published,
        memory.rating,
        memory.created_at
    )

    # Logging the conversation update
    print(f'Conversation with ID: {id} updated:\n{conversations_datas[index]}')
    return {"message": f"Conversation with ID: {id} has been updated:\n{conversations_datas[index]}"}


@app.delete("/delete-conversation/{id}", status_code=status.HTTP_204_NO_CONTENT)
def del_conversation(id: int):
    index = find_index_converse(id)
    if index == None:
        print(f'conversations_by_id: "{id}" does not exist')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"conversation with id: '{id}' does not exist")
    conversations_datas.pop(index)
    print(f'"message": "conversation was successfully deleted"')
    return Response(status_code=status.HTTP_204_NO_CONTENT)
