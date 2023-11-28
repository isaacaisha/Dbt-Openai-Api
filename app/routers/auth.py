from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import database, schemas, models, utils, oauth2

router = APIRouter(tags=["Authentication"])


@router.post("/login")
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()

    if not user:
        print("Invalid Credentials 😝 ¡!¡")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid Credentials 😝 ¡!¡")

    if not utils.verify(user_credentials.password, user.password):
        print("Invalid Credentials 😝 ¡!¡")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid Credentials 😝 ¡!¡")

    # Create a token
    access_token = oauth2.create_access_token(data={"user_id": user.id, "user_email": user.email})
    print(f"'access_token':\n'{access_token}'\n'token_type': 'bearer'")
    return {"access_token": access_token, "token_type": "bearer"}
