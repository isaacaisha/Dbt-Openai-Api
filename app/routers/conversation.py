from fastapi import Response, status, HTTPException, Depends, APIRouter
# from fastapi.responses import RedirectResponse
from typing import List, Optional
from sqlalchemy.orm import Session
# from sqlalchemy import func
import json
# import os
from ..models import Memory, joinedload
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


# @router.get("/", status_code=status.HTTP_201_CREATED)
# async def root():
#     try:
#         # Assuming you want to redirect to the URL fetched from the environment variable
#         redirect_url = os.environ['REDIRECT_URL_FASTAPI']
#         return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)
#     except KeyError:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                             detail="Redirect URL not found in environment variables")


@router.get("/all", status_code=status.HTTP_201_CREATED, response_model=List[schemas.MemoryResponse])
def get_all_conversations(db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user),
                          limit: int = 3, skip: int = 0, search: Optional[str] = ""):
    # cursor.execute("""SELECT * FROM memories""")
    # posts = cursor.fetchall()(db: Session = Depends(get_db)):

    # public:
    histories = db.query(models.Memory).filter(models.Memory.user_message.contains(search)).limit(limit).offset(skip).all()

    # Generate MemoryResponse objects with conversation_id properly set (return "conversation_id" intsead of just "id")
    memory_responses = [
        schemas.MemoryResponse(**{
            **history.__dict__,
            'conversation_id': history.id,
            'owner': history.owner
        }) for history in histories
    ]

    print(f'all conversation:\n{memory_responses} 👌🏿\n')

    return memory_responses


@router.get("/private", status_code=status.HTTP_201_CREATED, response_model=List[schemas.MemoryResponse])
def get_private_conversations(db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user),
                          limit: int = 3, skip: int = 0, search: Optional[str] = ""):

    # private:
    owner_id = current_user.id
    histories = db.query(models.Memory).filter(models.Memory.user_message.contains(search)).filter_by(owner_id=owner_id).limit(limit).offset(skip).all()

    # Generate MemoryResponse objects with conversation_id properly set (return "conversation_id" intsead of just "id")
    memory_responses = [
        schemas.MemoryResponse(**{
            **history.__dict__,
            'conversation_id': history.id,
            'owner': history.owner
        }) for history in histories
    ]

    print(f'private conversation:\n{memory_responses} 👌🏿\n')

    return memory_responses


@router.get("/summary", status_code=status.HTTP_201_CREATED)
def get_conversation_summary(db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user),
                          limit: int = 3, skip: int = 0, search: Optional[str] = ""):
    
    owner_id = current_user.id
    conversation_summaries_all = [summary.conversations_summary for summary in
                                  db.query(models.Memory).filter(models.Memory.user_message.contains(search)).filter_by(owner_id=owner_id).limit(limit).offset(skip).all()]

    head_summaries = conversation_summaries_all[:3]
    tail_summaries = conversation_summaries_all[-3:]

    print(f'Conversation Summary Head:\n{head_summaries}\n\n'
          f'Conversation Summary Tail:\n{tail_summaries} 👌🏿\n')

    return {"Conversation Summary Head": head_summaries, "Conversation Summary Tail": tail_summaries}


@router.post("/start", status_code=status.HTTP_201_CREATED, response_model=schemas.MemoryCreate)
def start_conversation(memory_: schemas.MemoryCreate, db: Session = Depends(get_db),
                       current_user=Depends(oauth2.get_current_user)):
    try:
        # Use SQLAlchemy ORM to insert a new record
        new_memo = Memory(user_message=memory_.user_message, llm_response=memory_.llm_response,
                          conversations_summary=memory_.conversations_summary)

        # Set the owner_id to the ID of the current user
        new_memo.owner_id = current_user.id

        # Get LLM response using the user's message
        llm_response = generate_llm_response(memory_.user_message)

        # Update the new_memo with the LLM response
        new_memo.llm_response = llm_response

        # Save the conversation context
        memory_summary.save_context({"input": memory_.user_message}, {"output": llm_response})

        # Load the conversation context
        conversations_summary = memory_summary.load_memory_variables({})

        # Convert the dictionary to a JSON-formatted string
        conversations_summary_json = json.dumps(conversations_summary)

        # Set the conversation summary in the new_memo
        new_memo.conversations_summary = conversations_summary_json

        print(f'omr.user_message:\n{memory_.user_message}\n')
        print(f'llm_response:\n{llm_response}\n')
        print(f'conversations_summary:\n{conversations_summary_json}\n')

        print(f'current_user.id: {current_user.id}\n')
        print(f'current_user.email: {current_user.email}\n')

        db.add(new_memo)
        db.commit()
        db.refresh(new_memo)

        return new_memo

    except Exception as e:
        # Log the exception or print it for debugging
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/audio", status_code=status.HTTP_201_CREATED, response_model=List[schemas.MemoryResponse])
async def audio_response(db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    # # public
    # audio = db.query(models.Memory).all()

    # private:
    owner_id = current_user.id
    audio = db.query(models.Memory).filter_by(owner_id=owner_id).all()

    # Generate MemoryResponse objects with conversation_id properly set (return "conversation_id" intsead of just "id")
    audio_responses = [
        schemas.MemoryResponse(**{
            **history.__dict__,
            'conversation_id': history.id,
            'owner': history.owner
        }) for history in audio
    ]

    print(f'audio response:\n{audio[-1:]}\n')

    # return {"message: Be Good Doing Good By Acting Good ¡!¡": audio_responses[-1:]}
    return audio_responses[-1:]


@router.get("/get-public/{id}", status_code=status.HTTP_201_CREATED, response_model=schemas.MemoryResponse)
def get_conversation_by_id(id: int, db: Session = Depends(get_db),
                           current_user: int = Depends(oauth2.get_current_user)):
    converse = db.query(models.Memory).filter(models.Memory.id == id).options(joinedload(models.Memory.owner)).first()

    if not converse:
        print(f'conversations with ID: "{id}" was not found')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"conversations with ID: '{id}' was not found'")

    # Use Pydantic's model.dict() to convert the SQLAlchemy model to a dictionary
    converse_dict = schemas.MemoryResponse(**converse.__dict__).model_dump()

    # Set conversation_id to the actual ID of the conversation
    converse_dict['conversation_id'] = converse.id
    
    print(f'get conversation with ID:\n{converse_dict}\n')

    return converse_dict


@router.get("/get-private/{id}", status_code=status.HTTP_201_CREATED, response_model=schemas.MemoryResponse)
def get_conversation_by_id(id: int, db: Session = Depends(get_db),
                           current_user=Depends(oauth2.get_current_user)):
    converse = db.query(models.Memory).filter(models.Memory.id == id).options(joinedload(models.Memory.owner)).first()

    if not converse:
        print(f'conversations with ID: "{id}" was not found')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"conversations with ID: '{id}' was not found'")

    if converse.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'The id: {id} doesn\'t remain to one of your previous conversations 😇 ¡!¡')

    # Use Pydantic's model.dict() to convert the SQLAlchemy model to a dictionary
    converse_dict = schemas.MemoryResponse(**converse.__dict__).model_dump()

    # Set conversation_id to the actual ID of the conversation
    converse_dict['conversation_id'] = converse.id

    print(f'get conversation with ID:\n{converse_dict}\n')

    return converse_dict


@router.put("/update/{id}", response_model=schemas.MemoryUpdate)
def upd_conversation(id: int, updated_memory: schemas.MemoryUpdate, db: Session = Depends(get_db),
                     current_user=Depends(oauth2.get_current_user)):
    # Check if the conversation exists in the database
    existing_memory_query = db.query(models.Memory).filter(models.Memory.id == id)
    existing_memory = existing_memory_query.first()

    if existing_memory is None:
        print(f'Conversation with ID: {id} does not exist')
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID: {id} does not exist"
        )

    if existing_memory.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'Not authorized to perform requested action 😝 ¡!¡')

    # Set the owner_id to the current_user.id
    updated_memory.owner_id = current_user.id

    # Update the existing_memory with the values from updated_memory
    existing_memory_query.update(updated_memory.model_dump(exclude_unset=True))

    db.commit()

    # Use Pydantic's model.dict() to convert the SQLAlchemy model to a dictionary
    memory_dict = schemas.MemoryResponse(**updated_memory.__dict__).model_dump()

    # Logging the conversation update
    print(f'Conversation with ID: {id} updated:\n{memory_dict}')

    return memory_dict


@router.delete("/delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
def del_conversation(id: int, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    del_converse_query = db.query(models.Memory).filter(models.Memory.id == id)

    del_converse = del_converse_query.first()

    if del_converse is None:
        print(f'conversations with ID: "{id}" does not exist')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"conversation with ID: '{id}' does not exist")

    if del_converse.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'Not authorized to perform requested action 😝 ¡!¡')

    del_converse_query.delete(synchronize_session=False)
    db.commit()
    print(f'"message": "conversation was successfully deleted"')

    return Response(status_code=status.HTTP_204_NO_CONTENT)
