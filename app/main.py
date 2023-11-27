import openai
import uvicorn
import os
import secrets
from fastapi import FastAPI, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from . import models
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

openai_api_key = os.environ.get("OPENAI_API_KEY")
# Generate a random secret key
secret_key = secrets.token_hex(199)
# Set it as the Flask application's secret key
app.secret_key = secret_key

# Heroku provides the DATABASE_URL environment variable
DATABASE_URL = os.environ['DATABASE_URL']

app.include_router(conversation.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)


@app.get("/", status_code=status.HTTP_201_CREATED)
async def root():
    return {"Be Good, Doing Good, By Acting Good": "SiisiChacal 🔥👌🏿😇💪🏿🔥"}


# @app.get("/", status_code=status.HTTP_201_CREATED)
# async def root():
#     return {"Be Good Doing Good By Acting Good ¡!¡": "Siisi Chacal 🔥👌🏿😇💪🏿🔥"}


@app.get("/", status_code=status.HTTP_201_CREATED)
async def root():
    return {"Be Good, Doing Good, By Acting Good": "SiisiChacal 🔥👌🏿😇💪🏿🔥"}


# @app.get("/", status_code=status.HTTP_201_CREATED)
# async def root():
#     return {"Be Good Doing Good By Acting Good ¡!¡": "Siisi Chacal 🔥👌🏿😇💪🏿🔥"}


@app.get("/", status_code=status.HTTP_201_CREATED)
async def root():
    return {"Be Good Doing Good By Acting Good": "Siisi-¡!¡-Chacal 🔥👌🏿😇💪🏿🔥"}


# @app.get("/", status_code=status.HTTP_201_CREATED)
# async def root():
#     return {"Be Good Doing Good By Acting Good ¡!¡": "Siisi Chacal 🔥👌🏿😇💪🏿🔥"}


@app.get("/", status_code=status.HTTP_201_CREATED)
async def root():
    return {"Be Good Doing Good By Acting Good": "Siisi Chacal 🔥👌🏿😇💪🏿🔥"}


# @app.get("/", status_code=status.HTTP_201_CREATED)
# async def root():
#     return {"Be Good Doing Good By Acting Good ¡!¡": "Siisi Chacal 🔥👌🏿😇💪🏿🔥"}


@app.get("/", status_code=status.HTTP_201_CREATED)
async def root():
    return {"Be Good Doing Good By Acting Good": "Siisi Chacal 🔥👌🏿😇💪🏿🔥"}


# @app.get("/", status_code=status.HTTP_201_CREATED)
# async def root():
#     return {"Be Good Doing Good By Acting Good ¡!¡": "Siisi Chacal 🔥👌🏿😇💪🏿🔥"}


@app.get("/", status_code=status.HTTP_201_CREATED)
async def root():
    return {"Be Good Doing Good By Acting Good": "Siisi Chacal 🔥👌🏿😇💪🏿🔥"}


# @app.get("/", status_code=status.HTTP_201_CREATED)
# async def root():
#     return {"Be Good Doing Good By Acting Good ¡!¡": "Siisi Chacal 🔥👌🏿😇💪🏿🔥"}


@app.get("/", status_code=status.HTTP_201_CREATED)
async def root():
    return {"Be Good, Doing Good, By Acting Good": "SiisiChacal 🔥👌🏿😇💪🏿🔥"}


# @app.get("/", status_code=status.HTTP_201_CREATED)
# async def root():
#     return {"Be Good Doing Good By Acting Good ¡!¡": "Siisi Chacal 🔥👌🏿😇💪🏿🔥"}


@app.get("/", status_code=status.HTTP_201_CREATED)
async def root():
    return {"Be Good, Doing Good, By Acting Good": "SiisiChacal 🔥👌🏿😇💪🏿🔥"}


# @app.get("/", status_code=status.HTTP_201_CREATED)
# async def root():
#     return {"Be Good Doing Good By Acting Good ¡!¡": "Siisi Chacal 🔥👌🏿😇💪🏿🔥"}


@app.get("/", status_code=status.HTTP_201_CREATED)
async def root():
    return {"Be Good, Doing Good, By Acting Good": "SiisiChacal 🔥👌🏿😇💪🏿🔥"}


# @app.get("/", status_code=status.HTTP_201_CREATED)
# async def root():
#     return {"Be Good Doing Good By Acting Good ¡!¡": "Siisi Chacal 🔥👌🏿😇💪🏿🔥"}


@app.get("/", status_code=status.HTTP_201_CREATED)
async def root():
    return {"Be Good Doing Good By Acting Good": "Siisi-¡!¡-Chacal 🔥👌🏿😇💪🏿🔥"}


# @app.get("/", status_code=status.HTTP_201_CREATED)
# async def root():
#     return {"Be Good Doing Good By Acting Good ¡!¡": "Siisi Chacal 🔥👌🏿😇💪🏿🔥"}


@app.get("/", status_code=status.HTTP_201_CREATED)
async def root():
    return {"Be Good Doing Good By Acting Good": "Siisi-¡!¡-Chacal 🔥👌🏿😇💪🏿🔥"}


# @app.get("/", status_code=status.HTTP_201_CREATED)
# async def root():
#     return {"Be Good Doing Good By Acting Good ¡!¡": "Siisi Chacal 🔥👌🏿😇💪🏿🔥"}


@app.get("/", status_code=status.HTTP_201_CREATED)
async def root():
    return {"Be Good, Doing Good, By Acting Good": "SiisiChacal 🔥👌🏿😇💪🏿🔥"}


# @app.get("/", status_code=status.HTTP_201_CREATED)
# async def root():
#     return {"Be Good Doing Good By Acting Good ¡!¡": "Siisi Chacal 🔥👌🏿😇💪🏿🔥"}


@app.get("/", status_code=status.HTTP_201_CREATED)
async def root():
    return {"Be Good, Doing Good, By Acting Good": "Siisi-¡!¡-Chacal 🔥👌🏿😇💪🏿🔥"}


# @app.get("/", status_code=status.HTTP_201_CREATED)
# async def root():
#     try:
#         # Assuming you want to redirect to the URL fetched from the environment variable
#         # redirect_url = os.environ['REDIRECT_URL_DBT_OPENAI']
#         redirect_url = os.environ['REDIRECT_URL_FASTAPI']
#         return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)
#     except KeyError:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                             detail="Redirect URL not found in environment variables")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
