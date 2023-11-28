from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func
import json
from ..models import Memory
from .. import models, schemas, oauth2
from ..database import get_db
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory, ConversationSummaryBufferMemory


router = APIRouter(
    prefix="/conversation",
    tags=['Conversations']
)

# Initialize an empty conversation chain
llm = ChatOpenAI(temperature=0.0, model="gpt-3.5-turbo-0301")  # Set your desired LLM model here
memory = ConversationBufferMemory()
conversation = ConversationChain(llm=llm, memory=memory, verbose=False)
memory_summary = ConversationSummaryBufferMemory(llm=llm, max_token_limit=19)


# Function to generate LLM response
def generate_llm_response(user_message):
    # Assuming 'conversation' is initialized as a ChatOpenAI object
    return conversation.predict(input=user_message)


@router.get("/", status_code=status.HTTP_201_CREATED)
async def home():

    return {"Be Good Doing Good By Acting Good ¡!¡": "Siisi Chacal 🔥👌🏿😇💪🏿🔥"}


@router.get("/all", status_code=status.HTTP_201_CREATED)
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""SELECT * FROM memories""")
    # posts = cursor.fetchall()(db: Session = Depends(get_db)):
    histories = db.query(models.Memory).all()
    print(f'all conversation:\n{histories} 👌🏿\n')

    return histories


@router.get("/summary", status_code=status.HTTP_201_CREATED)
def get_conversation_summary(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    conversation_summaries_all = [summary.conversations_summary for summary in db.query(models.Memory).all()]
    head_summaries = conversation_summaries_all[:3]
    tail_summaries = conversation_summaries_all[-3:]

    print(f'Conversation Summary Head:\n{head_summaries}\n\n'
          f'Conversation Summary Tail:\n{tail_summaries} 👌🏿\n')

    return {"Conversation Summary Head": head_summaries, "Conversation Summary Tail": tail_summaries}


@router.post("/start", status_code=status.HTTP_201_CREATED, response_model=schemas.MemoryCreate)
def start_conversation(omr: schemas.MemoryCreate, db: Session = Depends(get_db),
                       current_user=Depends(oauth2.get_current_user)):
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

        print(f'current_user: {current_user.email}')

        db.add(new_memo)
        db.commit()
        db.refresh(new_memo)

        return new_memo

    except Exception as e:
        # Log the exception or print it for debugging
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/audio", status_code=status.HTTP_201_CREATED)
async def audio_response(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    audio = db.query(models.Memory).all()
    print(f'audio response:\n{audio[-1:]}\n')

    return {"message: Be Good Doing Good By Acting Good ¡!¡": audio[-1:]}


@router.get("/get/{id}", status_code=status.HTTP_201_CREATED, response_model=schemas.MemoryResponse)
def get_conversation_by_id(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    converse = db.query(models.Memory).filter(models.Memory.id == id).first()
    if not converse:
        print(f'conversations with ID: "{id}" was not found')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"conversations with ID: '{id}' was not found'")

    # Use Pydantic's model.dict() to convert the SQLAlchemy model to a dictionary
    converse_dict = schemas.MemoryResponse(**converse.__dict__).model_dump()
    print(f'get conversation with ID:\n{converse_dict}\n')

    return converse_dict


@router.put("/update/{id}", response_model=schemas.MemoryResponse)
def upd_conversation(id: int, updated_memory: schemas.MemoryResponse, db: Session = Depends(get_db),
                     current_user: int = Depends(oauth2.get_current_user)):
    # Check if the conversation exists in the database
    existing_memory_query = db.query(models.Memory).filter(models.Memory.id == id)
    existing_memory = existing_memory_query.first()

    if existing_memory is None:
        print(f'Conversation with ID: {id} does not exist')
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID: {id} does not exist"
        )

    # Update the existing_memory with the values from updated_memory
    for field in updated_memory.model_dump().keys():
        if hasattr(existing_memory, field):
            setattr(existing_memory, field, getattr(updated_memory, field))

    db.commit()

    # Use Pydantic's model.dict() to convert the SQLAlchemy model to a dictionary
    memory_dict = schemas.MemoryResponse(**updated_memory.__dict__).model_dump()

    # Logging the conversation update
    print(f'Conversation with ID: {id} updated:\n{memory_dict}')

    return memory_dict


@router.delete("/delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
def del_conversation(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    del_converse = db.query(models.Memory).filter(models.Memory.id == id)

    if del_converse.first() is None:
        print(f'conversations with ID: "{id}" does not exist')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"conversation with ID: '{id}' does not exist")

    del_converse.delete(synchronize_session=False)
    db.commit()
    print(f'"message": "conversation was successfully deleted"')

    return Response(status_code=status.HTTP_204_NO_CONTENT)
