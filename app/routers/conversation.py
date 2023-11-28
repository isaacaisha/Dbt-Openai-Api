import json
import io

from fastapi import Response, status, HTTPException, Depends, APIRouter
from typing import List, Optional
from fastapi.responses import StreamingResponse
from gtts import gTTS
from sqlalchemy import func
from sqlalchemy.orm import Session

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


def convert_llm_response_to_audio(llm_response_text):
    # Create a gTTS object with the text
    tts = gTTS(text=llm_response_text, lang='en')

    # Save the audio to an in-memory file
    audio_file = io.BytesIO()
    tts.write_to_fp(audio_file)

    # Seek to the beginning of the file
    audio_file.seek(0)

    return audio_file


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
    
    # Perform the join with Vote and count the number of votes for each Memory
    results = db.query(models.Memory, func.count(models.Vote.post_id).label("likes")) \
        .outerjoin(models.Vote, models.Vote.post_id == models.Memory.id) \
        .group_by(models.Memory.id) \
        .limit(limit) \
        .offset(skip) \
        .all()

    memory_responses = []
    for history, likes_count in results:
        owner = schemas.UserOut(id=history.owner.id, email=history.owner.email, created_at=history.owner.created_at)

        # Create a MemoryResponse instance for the current memory
        memory_response = schemas.MemoryResponse(
            conversation_id=history.id,  # id is the conversation_id
            user_message=history.user_message,
            llm_response=history.llm_response,
            conversations_summary=history.conversations_summary,
            owner=owner,
            likes=likes_count
        )

        # Append the MemoryResponse instance to the list
        memory_responses.append(memory_response)

    return memory_responses


@router.get("/private", status_code=status.HTTP_201_CREATED, response_model=List[schemas.MemoryResponse])
def get_private_conversations(db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user),
                              limit: int = 3, skip: int = 0, search: Optional[str] = ""):

    # private:
    owner_id = current_user.id
    results = db.query(models.Memory, func.count(models.Vote.post_id).label("likes")) \
        .outerjoin(models.Vote, models.Vote.post_id == models.Memory.id) \
        .filter(models.Memory.user_message.contains(search)) \
        .filter(models.Memory.owner_id == owner_id) \
        .group_by(models.Memory.id) \
        .limit(limit) \
        .offset(skip) \
        .all()

    memory_responses = []
    for history, likes_count in results:
        owner = schemas.UserOut(id=history.owner.id, email=history.owner.email, created_at=history.owner.created_at)

        # Create a MemoryResponse instance for the current memory
        memory_response = schemas.MemoryResponse(
            conversation_id=history.id,  # id is the conversation_id
            user_message=history.user_message,
            llm_response=history.llm_response,
            conversations_summary=history.conversations_summary,
            owner=owner,
            likes=likes_count
        )

        # Append the MemoryResponse instance to the list
        memory_responses.append(memory_response)

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

    # private:
    owner_id = current_user.id
    results = db.query(models.Memory, func.count(models.Vote.post_id).label("likes")) \
        .outerjoin(models.Vote, models.Vote.post_id == models.Memory.id) \
        .filter(models.Memory.owner_id == owner_id) \
        .group_by(models.Memory.id) \
        .all()

    audio_responses = []
    for history, likes_count in results:
        owner = schemas.UserOut(id=history.owner.id, email=history.owner.email, created_at=history.owner.created_at)

        # Create a MemoryResponse instance for the current memory
        memory_response = schemas.MemoryResponse(
            conversation_id=history.id,  # id is the conversation_id
            user_message=history.user_message,
            llm_response=history.llm_response,
            conversations_summary=history.conversations_summary,
            owner=owner,
            likes=likes_count
        )

        # Append the MemoryResponse instance to the list
        audio_responses.append(memory_response)

    print(f'audio response:\n{audio_responses[-1:]}\n')

    return audio_responses[-1:]


@router.get("/play-audio-public/{audio_record_id}", status_code=status.HTTP_201_CREATED, response_model=List[schemas.MemoryResponse])
async def play_audio_by_id(audio_record_id: int, db: Session = Depends(get_db)):
    
    # Retrieve the audio record by its ID from the database
    audio_record = db.query(models.Memory).filter(models.Memory.id == audio_record_id).first()

    if not audio_record or not audio_record.llm_response:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"LLM response {audio_record} not found")

    # Convert the llm_response to an audio file
    audio_data = convert_llm_response_to_audio(audio_record.llm_response)
    
    # Extract owner information
    owner_info = audio_record.owner

    # Convert the datetime object to string
    created_at_str = owner_info.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    # Construct the response JSON containing the audio data and audio record information
    response_data = {
        "audio_record": {
            "id": audio_record.id,
            "user_message": audio_record.user_message,
            "llm_response": audio_record.llm_response,
            "conversations_summary": audio_record.conversations_summary,
            "owner": {
                "id": owner_info.id,
                "email": owner_info.email,
                "created_at": created_at_str,  # Convert datetime to string
            }
        }
    }

    # Print the indented JSON response
    print(f'audio_data:\n{json.dumps(response_data, indent=4)}')

    # Return the audio file as a streaming response along with the audio record information
    return StreamingResponse(audio_data, media_type="audio/mpeg", headers={"X-Audio-Record": json.dumps(response_data["audio_record"])})


@router.get("/play-audio-private/{audio_record_id}", status_code=status.HTTP_200_OK)
async def play_audio_by_id(audio_record_id: int, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    
    # Retrieve the audio record by its ID from the database
    audio_record = db.query(models.Memory).filter(models.Memory.id == audio_record_id).first()

    if not audio_record or not audio_record.llm_response:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"LLM response for record {audio_record_id} not found")

    # Check if the authenticated user is the owner of the audio record
    if audio_record.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to access this audio record")

    # Convert the LLM response to an audio file
    audio_data = convert_llm_response_to_audio(audio_record.llm_response)
    
    # Extract owner information
    owner_info = audio_record.owner

    # Convert the datetime object to string
    created_at_str = owner_info.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    # Construct the response JSON containing the audio data and audio record information
    response_data = {
        "audio_record": {
            "id": audio_record.id,
            "user_message": audio_record.user_message,
            "llm_response": audio_record.llm_response,
            "conversations_summary": audio_record.conversations_summary,
            "owner": {
                "id": owner_info.id,
                "email": owner_info.email,
                "created_at": created_at_str,  # Convert datetime to string
            }
        }
    }

    # Log the audio data and response data for debugging
    print(f'audio_data:\n{json.dumps(response_data, indent=4)}')

    # Return the audio file as a streaming response along with the audio record information
    return StreamingResponse(audio_data, media_type="audio/mpeg", headers={"X-Audio-Record": json.dumps(response_data["audio_record"])})


@router.get("/get-public/{id}", status_code=status.HTTP_201_CREATED, response_model=schemas.MemoryResponse)
def get_conversation_by_id(id: int, db: Session = Depends(get_db),
                           current_user: int = Depends(oauth2.get_current_user)):
    # Fetch the conversation by ID along with the owner data and the vote count
    conversation = db.query(models.Memory).filter(models.Memory.id == id).first()

    if not conversation:
        print(f'Conversation with ID: "{id}" was not found')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Conversation with ID: '{id}' was not found")
    
    # Fetch the conversation from the database
    converse = db.query(models.Memory).filter(models.Memory.id == id).first()

    # Check if the conversation exists
    if not converse:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Conversation with ID: '{id}' not found")

    # Fetch the owner data
    owner = db.query(models.User).filter(models.User.id == converse.owner_id).first()

    # Fetch the vote count for the conversation
    vote_count = db.query(func.count(models.Vote.post_id)).filter(models.Vote.post_id == converse.id).scalar()

    # Construct the response dictionary
    conversation_dict = schemas.MemoryResponse(
        user_message=converse.user_message,
        llm_response=converse.llm_response,
        conversations_summary=converse.conversations_summary,
        conversation_id=converse.id,
        owner=schemas.UserOut(id=owner.id, email=owner.email, created_at=owner.created_at),
        likes=vote_count  # Renamed likes to vote_count to match the public route response model
    )

    return conversation_dict


@router.get("/get-private/{id}", status_code=status.HTTP_201_CREATED, response_model=schemas.MemoryResponse)
def get_private_conversation_by_id(id: int, db: Session = Depends(get_db),
                                   current_user=Depends(oauth2.get_current_user)):
    
    # Fetch the conversation from the database
    converse = db.query(models.Memory).filter(models.Memory.id == id).first()

    # Check if the conversation exists
    if not converse:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Conversation with ID: '{id}' not found")

    # Check if the conversation belongs to the current user
    if converse.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Conversation with ID: '{id}' does not belong to the current user")

    # Fetch the owner data
    owner = db.query(models.User).filter(models.User.id == converse.owner_id).first()

    # Fetch the vote count for the conversation
    vote_count = db.query(func.count(models.Vote.post_id)).filter(models.Vote.post_id == converse.id).scalar()

    # Construct the response dictionary
    conversation_dict = schemas.MemoryResponse(
        user_message=converse.user_message,
        llm_response=converse.llm_response,
        conversations_summary=converse.conversations_summary,
        conversation_id=converse.id,
        owner=schemas.UserOut(id=owner.id, email=owner.email, created_at=owner.created_at),
        likes=vote_count  # Renamed likes to vote_count to match the public route response model
    )

    return conversation_dict


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
