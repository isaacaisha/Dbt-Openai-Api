import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import psycopg2
import time
from dotenv import load_dotenv, find_dotenv


_ = load_dotenv(find_dotenv())

# from .config import settings


# # Construct the SQLALCHEMY_DATABASE_URL using the settings
# SQLALCHEMY_DATABASE_URL = (
#     f"postgresql://{settings.user}:{settings.password}@{settings.host}:{settings.port}/{settings.database}"
# )


SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{os.environ['user']}:{os.environ['password']}@"
    f"{os.environ['host']}:{os.environ['port']}/{os.environ['database']}"
)


#SQLALCHEMY_DATABASE_URL = (
#    f"postgresql://{os.environ['USER']}:{os.environ['PASSWORD']}@"
#    f"{os.environ['HOST']}:{os.environ['PORT']}/{os.environ['DATABASE']}"
#)


engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# while True:
#     try:
#         conn = psycopg2.connect(
#             f"postgresql://{os.environ['user']}:{os.environ['password']}@"
#             f"{os.environ['host']}:{os.environ['port']}/{os.environ['database']}"
#         )
#         cursor = conn.cursor()
#         print(f'Database connection was successful 😎\n')
#         break
#     except Exception as error:
#         print(f'Connecting to database failed:\nError: {error} 😭\n')
#         time.sleep(3)
# 
# # Creating the SQL command to fetch all data from the "api_memories" table
# memory_db = "SELECT * FROM api_memories"
# 
# # Executing the query and fetching all the data
# cursor.execute(memory_db)
# 
# conversations_datas = cursor.fetchall()
# # print(f'conversations_datas:\n{conversations_datas[9]}\n')
# 
# 
# def find_conversation_by_id(id):
#     for converse in conversations_datas:
#         if converse[0] == id:  # Assuming 'id' is the first column in the OMR table
#             print(f'conversation by id: {converse}')
#             return converse
# 
# 
# def find_index_converse(id):
#     for i, conv in enumerate(conversations_datas):
#         if isinstance(conv, dict) and conv.get('id') == id:
#             return i
#         elif isinstance(conv, tuple) and conv[0] == id:
#             return i
#     return None
# 