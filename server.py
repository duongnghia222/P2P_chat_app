from tkinter import *
import threading
import socket
import pickle
FORMAT = 'utf-8'

active_users = []

# config server
host = socket.gethostbyname(socket.gethostname())  # use public ip to have public access
port = 2222
# ===============
# client_port = 2223
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
def start_server():
    print("Sever is listening on", host)
    server.listen()



def tcp(client, address):
    while True:
        # print("receiving command")
        command = client.recv(50)
        command = command.decode()
        if command == "-sign_up-":
            # receive client info
            dump_client_info = client.recv(4096)  # receive at most 4096 bytes
            client_info = pickle.loads(dump_client_info)

            print("1st time connected with", address)

            active_users.append(client_info)
            print(client_info)
        elif command == '-login-':
            dump_login_info = client.recv(1024)  # receive at most 4096 bytes
            login_info = pickle.loads(dump_login_info)
            print(active_users)
            for user in active_users:
                if login_info['username'] == user['username']:
                    if login_info['password'] == user['password']:
                        print("login successfully!!!")
                        client.send('success'.encode())
                        print("connected with", login_info['username'])
            client.send('fail'.encode())
        elif command == '-send_username_list-':
            user_name_list = []
            for user in active_users:
                user_name_list.append(user['username'])
            username_list_info = pickle.dumps(user_name_list)
            client.send(username_list_info)
        elif command[:19] == '-friend_request_to_':
            to_username = command[19:command.find('from')-1]
            from_user = command[command.find('from')+5:-1]
            # search for conn
            for user in active_users:
                if to_username == user['username']:
                    address_send = user['address']
                    port_send = user['port']
                    to_user = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    to_user.connect((address_send, port_send))
                    to_user.send(('-friend_request_from_{}-'.format(from_user)).encode())
                    to_user.close()
                    print("i sent ")

def receive_connection():
    try:
        while True:
            client, address = server.accept()
            t = threading.Thread(target=tcp, args=(client, address))
            t.start()



            # ==========================================



            # client.send("NICK".encode('ascii'))
            # nickname = client.recv(1024).decode('ascii')
            # nicknames.append(nickname)
            # clients.append(client)
            # print("Nick name of the client is", nickname)
            # Broadcast("{} joined the chat".format(nickname).encode('ascii'), client)
            # client.send('Connected to the server'.encode('ascii'))
            # thread = threading.Thread(target=handle, args=(client,))
            # thread.start()
    except receive_connection.error:
        print(' Connection lose')


if __name__ == "__main__":
    start_server()
    receive_connection()

#
# def Broadcast(message, me):
#     for client in clients:
#         if client != me:
#             client.send(message)
#
#
# def handle(client):
#     while True:
#         index = clients.index(client)
#         nickname = nicknames[index]
#
#         try:
#             message = client.recv(1024).decode('ascii')
#             if message == '{}: exit'.format(nickname):
#                 print("someone left")
#                 clients.remove(client)
#                 client.close()
#                 Broadcast('{} left !'.format(nickname).encode('ascii'), client)
#                 nicknames.remove(nickname)
#                 break
#             Broadcast(message.encode('ascii'), client)
#         except InterruptedError:
#             clients.remove(client)
#             client.close()
#             Broadcast('{} left except!'.format(nickname).encode('ascii'), client)
#             nicknames.remove(nickname)
#             break
#
#
#
# def receive():
#     while True:
#         client, address = server.accept()
#         print("Connected with", address)
#         client.send("NICK".encode('ascii'))
#         nickname = client.recv(1024).decode('ascii')
#         nicknames.append(nickname)
#         clients.append(client)
#         print("Nick name of the client is", nickname)
#         Broadcast("{} joined the chat".format(nickname).encode('ascii'), client)
#         client.send('Connected to the server'.encode('ascii'))
#         thread = threading.Thread(target=handle, args=(client,))
#         thread.start()
#
#
# receive()