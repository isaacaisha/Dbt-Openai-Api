import openai
import uvicorn
import os
import psycopg2
import secrets
import time
from fastapi import FastAPI, status, HTTPException
from fastapi.responses import RedirectResponse
from . import models
from .database import engine
from .routers import conversation, user, auth
from dotenv import load_dotenv, find_dotenv


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

# Creating the SQL command to fetch all data from the memories table
memory_db = "SELECT * FROM memories"

# Executing the query and fetching all the data
cursor.execute(memory_db)

conversations_datas = cursor.fetchall()
# print(f'conversations_datas:\n{conversations_datas[9]}\n')


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


app.include_router(conversation.router)
app.include_router(user.router)
app.include_router(auth.router)


# @app.get("/", status_code=status.HTTP_201_CREATED)
# async def root():
#     return {"Be Good Doing Good By Acting Good ¡!¡": "Siisi Chacal 🔥👌🏿😇💪🏿🔥"}


@app.get("/", status_code=status.HTTP_201_CREATED)
async def root():
    try:
        # Assuming you want to redirect to the URL fetched from the environment variable
        # redirect_url = os.environ['REDIRECT_URL_DBT_OPENAI']
        redirect_url = os.environ['REDIRECT_URL_FASTAPI']
        return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Redirect URL not found in environment variables")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
