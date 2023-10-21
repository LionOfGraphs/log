from typing import Annotated
from pydantic import BaseModel

import grpc
import uvicorn
import user_pb2_grpc, user_pb2
from decouple import config
from fastapi import Depends, FastAPI, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

@app.get("/")
async def root():
    return {"message":"Hello World!"}

def authenticate_user(username, hashed_password):
    with grpc.insecure_channel("localhost:" + config("MS2_PORT")) as channel:
        stub = user_pb2_grpc.UserServiceStub(channel = channel)
        response = stub.Login(
            user_pb2.LoginRequest(username = username, hashed_password = hashed_password)
        )
        return response.auth_token

@app.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    access_token = authenticate_user(form_data.username, form_data.password)
    if not bool(access_token):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Incorrect username or password",
            headers = {"WWW-Authenticate": "Bearer"},
        )
    return {"access_token" : access_token, "token_type" : "bearer"}


def run():
    host = config("GATEWAY_HOST")
    port = config("GATEWAY_PORT", cast = int)
    log_level = config("LOG_LEVEL")
    uvicorn.run("server.app", host = host, port = port, log_level = log_level, reload = True)

if __name__ == "__main__":
    run()