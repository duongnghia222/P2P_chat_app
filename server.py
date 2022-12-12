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
        try:
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
                to_username = command[19:command.find('from') - 1]
                from_user = command[command.find('from') + 5:-1]
                # search for conn
                from_user_ip = ''
                from_user_port = ''
                for user in active_users:
                    if from_user == user['username']:
                        from_user_ip = user['address']
                        from_user_port = user['port']

                for user in active_users:
                    if to_username == user['username']:
                        address_send = user['address']
                        port_send = user['port']
                        to_user = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        to_user.connect((address_send, port_send))
                        to_user.send(('-friend_request_from_{}_ip={}_port={}-'.format(from_user,
                                                                                      from_user_ip,
                                                                                      from_user_port)).encode())
                        to_user.close()

            elif command[:21] == '-accept_request_from_':
                to_username = command[command.index('_to_') + 4:-1]
                from_user = command[21:command.index('_to_')]
                from_user_address, from_user_port = ['', '']
                for user in active_users:
                    if from_user == user['username']:
                        from_user_address = user['address']
                        from_user_port = user['port']
                for user in active_users:
                    if to_username == user['username']:
                        address_send = user['address']
                        port_send = user['port']
                        to_user = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        to_user.connect((address_send, int(port_send)))
                        to_user.send(('-accept_request_from_{}_ip={}_port={}-'.format(from_user,
                                                                                      from_user_address,
                                                                                      from_user_port)).encode())
                        to_user.close()
            elif command == '-change_information-':
                dump_client_info = client.recv(4096)  # receive at most 4096 bytes
                client_info = pickle.loads(dump_client_info)
                for user in active_users:
                    if user['username'] == client_info['username']:
                        user['age'] = client_info['age']
                        user['location'] = client_info['location']
                        user['password'] = client_info['password']
                print(client_info['username'], "updated information")
                print(active_users)
        except:
            client.close()


def receive_connection():
    while True:
        try:
            client, address = server.accept()
            t = threading.Thread(target=tcp, args=(client, address))
            t.start()
        except:
            client.close()


if __name__ == "__main__":
    start_server()
    receive_connection()
