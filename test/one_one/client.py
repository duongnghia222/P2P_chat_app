import socket
import threading
import sys
from cryptography.fernet import Fernet
key = b'PTdTxhA2j06W6nLSy6_CIs7CJ5yQ05u7bC8gYdZFZAg='
cipher_suite = Fernet(key)

nickname = input("Choose a nickname:\n")
SERVER = "192.168.132.51"
port = 5555
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)

client.connect((SERVER, port))
print(client)


def receive():
    while True:
        try:
            message = client.recv(1024).decode()
            if message == 'NICK':
                client.send(nickname.encode())
            else:
                print(message)
        except:
            print("An error occurred")
            client.close()
            break


def write():
    while True:
        message = '{}: {}'.format(nickname, (input('')))

        client.send(cipher_suite.encrypt(message.encode()))
        if message == '{}: exit'.format(nickname):
           sys.exit()




receive_thread = threading.Thread(target=receive)
receive_thread.start()
write_thread = threading.Thread(target=write)
write_thread.start()