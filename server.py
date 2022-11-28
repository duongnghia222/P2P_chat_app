from tkinter import *
import threading
import socket
import pickle
FORMAT = 'utf-8'

active_users = []


host = socket.gethostbyname(socket.gethostname())  # use public ip to have public access
port = 2222
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
def start_server():
    print("Sever is listening on", host)
    server.listen()

def send_active_user(client):
    dump_active_users = pickle.dumps(active_users)
    client.send(dump_active_users)



def receive_connection():
    try:
        while True:
            client, address = server.accept()
            # receive client info
            dump_client_info = client.recv(4096)  # receive at most 4096 bytes
            print("Connected with", address)
            client_info = pickle.loads(dump_client_info)
            active_users.append(client_info)
            # ==========================================
            # receive client request
            request = client.recv(1024).decode()
            print(request)
            if request == "-show_active_user-":
                send_active_user(client)



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
        print("start_server error !!!")

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