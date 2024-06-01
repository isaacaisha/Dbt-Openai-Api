import uvicorn
import os
import secrets
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from app import models
from .database import engine
from .routers import conversation, user, auth, vote
from dotenv import load_dotenv, find_dotenv


_ = load_dotenv(find_dotenv())

# models.Base.metadata.create_all(bind=engine)

app = FastAPI(debug=True)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
# Generate a random secret key
secret_key = secrets.token_hex(199)
# Set it as the Flask application's secret key
app.secret_key = OPENAI_API_KEY

# Heroku provides the DATABASE_URL environment variable
ADMIN_DATABASE_URL = os.environ['ADMIN_DATABASE_URL']

app.include_router(conversation.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)


@app.get("/", status_code=status.HTTP_200_OK)
async def root():
    return {"Be Good | Doing Good | By Acting Good": " ... Siisi-¡!¡-Chacal ... 🔥👌🏿😇💪🏿🔥 ..."}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
