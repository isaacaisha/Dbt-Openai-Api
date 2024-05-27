from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .. import schemas, database, models, oauth2

router = APIRouter(
    prefix="/vote",
    tags=['Vote']
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote, db: Session = Depends(database.get_db),
         current_user: int = Depends(oauth2.get_current_user)):
    
    post = db.query(models.Memory).filter(models.Memory.id == vote.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with ID {vote.post_id} does not exist")
    
    vote_query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id,
                                              models.Vote.user_id == current_user.id)
    found_vote = vote_query.first()
    
    try:
        if vote.dir == 1:
            if found_vote:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                    detail=f"user {current_user.id} has already voted on post {vote.post_id}")
            new_vote = models.Vote(post_id=vote.post_id, user_id=current_user.id)
            db.add(new_vote)
            db.commit()
            
            print(f'new_vote: post_id={new_vote.post_id}, user_id={new_vote.user_id}\n')
    
            return {"message": f"successfully added vote to conversation {vote.post_id}"}
        else:
            if not found_vote:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Vote {vote.post_id} does not exist")
            
            vote_query.delete(synchronize_session=False)
            db.commit()

            return {"message": "successfully deleted vote"}

    # Handle the IntegrityError and raise a 404 Not Found
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Vote {vote.post_id} does not exist")
