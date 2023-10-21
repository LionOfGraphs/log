import grpc
import user_pb2
import user_pb2_grpc

class GRPCClient(object):
    def __init__(self):
        self.host = '127.0.0.1'
        self.server_port = '8000'

        self.channel = grpc.insecure_channel('{}:{}'.format(self.host, self.server_port))

        self.stub = user_pb2_grpc.UserServiceStub(self.channel)

    def get_url(self):
        return self.stub.Login(user_pb2.LoginRequest(username = "conaça", hashed_password = "datuamae"))
    
if __name__ == '__main__':
    client = GRPCClient()
    result = client.get_url()
    print(f'{result}')