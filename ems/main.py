###
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

###
from .api.v1 import auth, users, events, tickets
# from .db.database import Engine
# from .db import models


# This or alembic can be used
# models.Base.metadata.create_all(bind=Engine)

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
# app.include_router(tickets.router)


@app.get("/home")
def homepage():
    return {"message": "Hello! Welcome to the homepage..."}
