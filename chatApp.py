from tkinter import *
from tkinter import messagebox
import tkinter.font as tkFont
import threading
import socket
import pickle
import time

FORMAT = 'utf-8'

# =================
root = None
root2 = None
client = None
# config server
server = "172.26.80.1"  # ip of the server
port = 2222
# =========
server_server = "172.26.80.1"  # ip of the server of the app to receive response (user gethostbyname)
port_server = 2223
# port_for_response = 2223
# ==================
friend_requests = []
block_list = []
account_info = dict()
friend_conn = dict()
friend_list = []


def listen(client_listen, address_listen):
    while True:
        # print("receiving command")
        response = client_listen.recv(200)
        response = response.decode()
        if response[:21] == "-friend_request_from_":
            from_user = response[21:-1]
            friend_requests.append(from_user)
        elif response[:21] == '-accept_request_from_':
            from_user = response[21:response.index('_ip=')]
            from_user_address = response[response.index('_ip=')+4:response.index('_port=')]
            from_user_port = response[response.index('_port=')+6:-1]
            friend_conn['username'] = from_user
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.connect((from_user_address, int(from_user_port)))
            friend_conn['conn'] = conn
            friend_list.append(friend_conn)
            conn.send('hi {}'.format(from_user).encode())
        elif response != '':
            print(response)

def connect_user(user, top):
    client.send("-friend_request_to_{}_from_{}-".format(user, account_info['username']).encode())
    top.destroy()
    pass


def block_user(user, top):
    block_list.append(user)
    top.destroy()
    pass


def show_active_users_window(active_users):
    """Displays
    """
    top = Toplevel(root2)
    top.title("Active Users")
    top.grab_set()
    scrollbar = Scrollbar(top, orient=VERTICAL)
    listbox = Listbox(top, yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)
    scrollbar.pack(side=RIGHT, fill=Y)
    # buttons = Frame(top)
    add_btn = Button(top, text="Add & Chat",
                     command=lambda: connect_user(
                         listbox.get(ACTIVE), top))
    add_btn.pack(side=BOTTOM)
    block_btn = Button(top, text="Block",
                       command=lambda: block_user(
                           listbox.get(ACTIVE), top))
    block_btn.pack(side=BOTTOM)

    for index, username in enumerate(active_users):
        if username == account_info['username'] or (username in block_list):
            continue
        listbox.insert(index, username)
    listbox.pack(side=LEFT, fill=BOTH, expand=1)


def accept_request(user, top):
    client.send(('-accept_request_from_{}_to_{}-'.format(account_info['username'], user)).encode())
    friend_requests.remove(user)
    friend_conn['username'] = user
    top.destroy()
    pass

def delete_request(user, top):
    block_list.append(user)
    top.destroy()
    pass

def show_friend_requests():
    top = Toplevel(root2)
    top.title("Friend Requests")
    top.grab_set()
    scrollbar = Scrollbar(top, orient=VERTICAL)
    listbox = Listbox(top, yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)
    scrollbar.pack(side=RIGHT, fill=Y)
    # buttons = Frame(top)
    accept_btn = Button(top, text="Accept",
                     command=lambda: accept_request(
                         listbox.get(ACTIVE), top))
    accept_btn.pack(side=BOTTOM)
    delete_btn = Button(top, text="Delete",
                       command=lambda: delete_request(
                           listbox.get(ACTIVE), top))
    delete_btn.pack(side=BOTTOM)

    for index, username in enumerate(friend_requests):
        if username in block_list:
            continue
        listbox.insert(index, username)
    listbox.pack(side=LEFT, fill=BOTH, expand=1)


def show_active_user():
    client.send("-send_username_list-".encode())
    dump_active_users = client.recv(4096)  # receive at most 4096 bytes
    active_users = pickle.loads(dump_active_users)
    show_active_users_window(active_users)


def connect_to_server(name, age, location, password, confirm_password, top):
    if (not age.isnumeric()):
        messagebox.showerror("Age", "Age must be a number !!!")
        return
    if (password != confirm_password):
        messagebox.showerror("Password", "Password not match !!!")
        return
    global client
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server, port))
    client.send('-send_username_list-'.encode())
    username_list_info = client.recv(4096)
    username_list = pickle.loads(username_list_info)
    print(username_list)
    for username in username_list:
        if name == username:
            messagebox.showerror("Sign Up", "Username existed")
            return
    # client.close()
    # client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # client.connect((server, port))
    global account_info
    account_info['address'] = server_server
    account_info['port'] = port_server
    account_info['username'] = name
    account_info['age'] = age
    account_info['location'] = location
    account_info['password'] = password
    dump_client_info = pickle.dumps(account_info)
    client.send('-sign_up-'.encode())
    time.sleep(0.1)
    client.send(dump_client_info)
    messagebox.showinfo("Sign Up", "Sign Up Successfully")
    top.destroy()
    root.destroy()
    main_chat_box()


def connect_to_server_window():
    top = Toplevel(root)
    top.title("Your information")
    top.grab_set()  # prevent users from interacting with the main window
    Label(top, text="Username:").grid(row=0)
    name = Entry(top)
    name.focus_set()
    name.grid(row=0, column=1)
    Label(top, text="Age:").grid(row=1)
    age = Entry(top)
    age.focus_set()
    age.grid(row=1, column=1)
    Label(top, text="Location:").grid(row=2)
    location = Entry(top)
    location.focus_set()
    location.grid(row=2, column=1)
    Label(top, text="Password:").grid(row=3)
    password = Entry(top)
    password.focus_set()
    password.grid(row=3, column=1)
    Label(top, text="Confirm Password:").grid(row=4)
    confirm_password = Entry(top)
    confirm_password.focus_set()
    confirm_password.grid(row=4, column=1)

    def go(*args):
        connect_to_server(name.get(), age.get(),
                          location.get(), password.get(),
                          confirm_password.get(), top)

    btn = Button(top, text="Start chat", command=go)
    top.bind('<Return>', go)
    btn.grid(row=5, column=1)


def login(usename, password, top):
    login_info = dict()
    login_info['username'] = usename
    login_info['password'] = password
    global client
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server, port))
    dump_login_info = pickle.dumps(login_info)
    client.send('-login-'.encode())
    time.sleep(0.1)
    client.send(dump_login_info)
    success = client.recv(20)
    success = success.decode()
    if success == 'success':
        messagebox.showinfo("Login", "Login Successfully")
    else:
        messagebox.showerror("Login", "Username or Password not match")
    top.destroy()
    root.destroy()
    main_chat_box()


def login_window():
    top = Toplevel(root)
    top.title("Login")
    top.grab_set()  # prevent users from interacting with the main window
    Label(top, text="Username:").grid(row=0)
    username = Entry(top)
    username.focus_set()
    username.grid(row=0, column=1)
    Label(top, text="Password:").grid(row=1)
    password = Entry(top)
    password.focus_set()
    password.grid(row=1, column=1)

    def go(*args):
        login(username.get(), password.get(), top)

    btn = Button(top, text="Login", command=go)
    top.bind('<Return>', go)
    btn.grid(row=2, column=1)


def save_history():
    pass


def change_info(name, age, top):
    account_info['username'] = name
    account_info['age'] = age
    dump_client_info = pickle.dumps(account_info)
    client.send(dump_client_info)
    messagebox.showinfo("Update information.", "Information updated")
    top.destroy()


def change_info_window():
    top = Toplevel(root)
    top.title("Change Information")
    top.grab_set()  # prevent users from interacting with the main window
    Label(top, text="Username:").grid(row=0)
    name = Entry(top)
    name.focus_set()
    name.grid(row=0, column=1)
    Label(top, text="Age:").grid(row=1)
    age = Entry(top)
    age.focus_set()
    age.grid(row=1, column=1)
    btn = Button(top, text="Change", command=lambda: change_info(name.get(), age.get(), top))
    btn.grid(row=2, column=1)


def run_listen(server_listen):
    try:
        while True:
            client_listen, address_listen = server_listen.accept()
            friend_conn['conn'] = client_listen
            friend_list.append(friend_conn)
            t = threading.Thread(target=listen, args=(client_listen, address_listen))
            t.start()

    except run_listen().error:
        print(' Connection lose')
    pass


def send_file():
    pass

def send_text():
    pass

def main_chat_box():
    # start a thread for listen response from server
    server_listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_listen.bind((server_server, port_server))
    server_listen.listen()
    t = threading.Thread(target=lambda: run_listen(server_listen))
    t.start()
    global root2
    root2 = Tk()
    width = 800
    height = 500
    screenwidth = root2.winfo_screenwidth()
    screenheight = root2.winfo_screenheight()
    alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
    root2.geometry(alignstr)
    root2.resizable(width=False, height=False)
    root2.title("Chat APP v1")


    menu_bar = Menu(root2, tearoff=0)

    tool_menu = Menu(menu_bar, tearoff=0)
    tool_menu.add_command(label="Save chat", command=save_history)
    tool_menu.add_command(label="Change my information",
                          command=change_info_window)
    tool_menu.add_separator()  # <hr> to separate exit option
    tool_menu.add_command(label="Exit", command=root.destroy)
    menu_bar.add_cascade(label="Tool", menu=tool_menu)
    # ==========================================
    show_menu = Menu(menu_bar, tearoff=0)
    show_menu.add_command(label="Show active users", command=show_active_user)
    show_menu.add_command(label="Show friend requests", command=show_friend_requests)
    menu_bar.add_cascade(label="Show", menu=show_menu)

    root2.config(menu=menu_bar)

    # ===================================-=============
    welcome_title = Label(root2)
    ft = tkFont.Font(family='Times', size=10)
    welcome_title["font"] = ft
    welcome_title["fg"] = "#c8c3bc"
    welcome_title["justify"] = "center"
    welcome_title["text"] = "Welcome to chat app v1"
    welcome_title.place(x=160, y=0, width=330, height=30)

    #  =====================================
    friend_frame = Listbox(root2)
    friend_frame["borderwidth"] = "1px"
    ft = tkFont.Font(family='Times', size=10)
    friend_frame["font"] = ft
    friend_frame["fg"] = "#c8c3bc"
    friend_frame["justify"] = "center"
    friend_frame.place(x=40, y=40, width=80, height=100)

    # ===========================
    imcome_mess_frame = Listbox(root2)
    imcome_mess_frame["borderwidth"] = "1px"
    ft = tkFont.Font(family='Times', size=10)
    imcome_mess_frame["font"] = ft
    imcome_mess_frame["fg"] = "#c8c3bc"
    imcome_mess_frame["justify"] = "center"
    imcome_mess_frame.place(x=40, y=150, width=80, height=268)


    # =================================

    main_body = Frame(root2, height=377, width=447)

    main_body_text = Text(main_body)
    body_text_scroll = Scrollbar(main_body)
    main_body_text.focus_set()
    body_text_scroll.pack(side=RIGHT, fill=Y)
    main_body_text.pack(side=LEFT, fill=Y)
    body_text_scroll.config(command=main_body_text.yview)
    main_body_text.config(yscrollcommand=body_text_scroll.set)
    main_body.place(x=130, y=40)

    main_body_text.insert(END, "Text show here")
    main_body_text.config(state=DISABLED)

    # ==========================================


    text_input = Entry(root2)
    text_input["borderwidth"] = "1px"
    ft = tkFont.Font(family='Times', size=10)
    text_input["font"] = ft
    text_input["fg"] = "#c8c3bc"
    text_input["justify"] = "center"
    text_input["text"] = "Entry"
    text_input.place(x=40, y=440, width=458, height=30)
    text_input.bind("<Return>", send_text)
    # ==================================

    send_file_btn = Button(root2)
    send_file_btn["bg"] = "#6b6b6b"
    ft = tkFont.Font(family='Times', size=10)
    send_file_btn["font"] = ft
    send_file_btn["fg"] = "#ffffff"
    send_file_btn["justify"] = "center"
    send_file_btn["text"] = "Button"
    send_file_btn.place(x=510, y=440, width=70, height=25)
    send_file_btn["command"] = send_file

    root2.mainloop()


def main():
    # ==== init tk window =======
    global root
    root = Tk()
    root.title("Chat APP v1")
    # =====================================

    # ==== show the join button at bottom ===========
    root.geometry("360x620")

    connect_button = Button(root, text='Register', command=connect_to_server_window)
    connect_button.grid(column=2, row=4)
    connect_button = Button(root, text='Login', command=login_window)
    connect_button.grid(column=2, row=5)


    root.mainloop()


if __name__ == "__main__":
    main()
