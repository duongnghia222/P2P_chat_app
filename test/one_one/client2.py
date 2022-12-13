import socket
import threading
import sys
from cryptography.fernet import Fernet
key = b'PTdTxhA2j06W6nLSy6_CIs7CJ5yQ05u7bC8gYdZFZAg='

print(key)
cipher_suite = Fernet(key)

nickname = input("Choose a nickname:\n")
SERVER = socket.gethostbyname(socket.gethostname())
port = 5555
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((SERVER, port))
server.listen()
client = None
def receive():
    while True:
        try:
            message = client.recv(1024)
            if message == 'NICK':
                client.send(nickname.encode(''))
            else:
                message = cipher_suite.decrypt(message).decode()
                print(message)
        except:
            print("An error occurred")
            client.close()
            break


def write():
    while True:
        message = '{}: {}'.format(nickname, input(''))
        client.send((str(message)).encode())
        if message == '{}: exit'.format(nickname):
           sys.exit()


def receive_connection():
    global client
    while True:
        client, address = server.accept()
        print("connected")
        print(client)
        receive_thread = threading.Thread(target=receive)
        receive_thread.start()
        write_thread = threading.Thread(target=write)
        write_thread.start()

receive_connection()
