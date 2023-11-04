from typing import Annotated

import grpc
#from grpc_interceptor.exceptions import GrpcException
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

    try:
        with grpc.insecure_channel(config("SERVER_ADDRESS") + ":" + config("SERVER_PORT")) as channel:
            stub = user_pb2_grpc.UserServiceStub(channel = channel)
            response = stub.Login(
                user_pb2.LoginRequest(username = username, hashed_password = hashed_password)
            )
            return {"identity_token" : response.identity_token, "access_token" : response.access_token, "refresh_token" : response.refresh_token}
    except grpc.RpcError as rpcError:
        raise HTTPException(status_code=rpcError.code(), detail="Grpc Error")
    except Exception as e:
        raise HTTPException(status_code=404, detail="Item not found")
        

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
    uvicorn.run("server:app", host = host, port = port, reload = True)

if __name__ == "__main__":
    run()