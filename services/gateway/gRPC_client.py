import grpc
import user_pb2
import user_pb2_grpc
from decouple import config

class GRPCClient(object):
    def __init__(self):
        self.host = config("SERVER_ADDRESS")
        self.server_port = config("SERVER_PORT")

        self.channel = grpc.insecure_channel('{}:{}'.format(self.host, self.server_port))

        self.stub = user_pb2_grpc.UserServiceStub(self.channel)

    def get_url(self):
        return self.stub.Login(user_pb2.LoginRequest(email = "conaça", hashed_password = "datuamae"))
    
if __name__ == '__main__':
    client = GRPCClient()
    result = client.get_url()
    print(f'{result}')