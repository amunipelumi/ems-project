###
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

###
from .api.v1 import auth, users, events
from .db.database import Engine
from .db import models



models.Base.metadata.create_all(bind=Engine)

origins = [
    '*',
]

app = FastAPI()
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(events.router)


@app.get("/home")
def homepage():
    return {"message": "Hello! Welcome to the homepage..."}



# Testing #
# @app.get("/")
# def read_root():
#     return {"Hello": "World"}


# @app.post('/posts')
# def print_posts(data: dict=Body()):
#     print(data)
#     return {'message': 'success'}