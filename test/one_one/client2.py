import socket
import threading
import sys

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
            message = client.recv(1024).decode('ascii')
            if message == 'NICK':
                client.send(nickname.encode('ascii'))
            else:
                print(message)
        except:
            print("An error occurred")
            client.close()
            break


def write():
    while True:
        message = '{}: {}'.format(nickname, input(''))
        client.send((str(message)).encode('ascii'))
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
