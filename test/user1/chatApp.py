import sys
from tkinter import *
from tkinter import messagebox
import tkinter.font as tkFont
import threading
import socket
import pickle
import time
import os
from tkinter.simpledialog import askstring
from tkinter.filedialog import asksaveasfilename, askopenfilename

FORMAT = 'utf-8'
SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096  # send 4096 bytes each time step

# =================
root = None
root2 = None
client = None
server_listen = None
# config server
server = socket.gethostbyname(socket.gethostname())  # ip of the server
port = 2222
# =========
server_server = socket.gethostbyname(socket.gethostname())  # ip of the server of the app to receive response
port_server = 2224
# port_for_response = 2223
# ==================
friend_requests = []
friend_requests_detail = []
block_list = []
account_info = dict()
friend_list = []
top_frame_list = []
msg_db_list = []


def listen(client_listen, address):
    while True:
        try:
            response = client_listen.recv(4000)
            response = response.decode()
            if response[:21] == "-friend_request_from_":
                from_user = response[21:response.index('_ip=')]
                from_user_address = response[response.index('_ip=') + 4:response.index('_port=')]
                from_user_port = response[response.index('_port=') + 6:-1]
                friend_requests.append(from_user)
                friend_requests_detail.append({'username': from_user, 'ip': from_user_address, 'port': from_user_port})
            elif response[:21] == '-accept_request_from_':
                from_user = response[21:response.index('_ip=')]
                from_user_address = response[response.index('_ip=') + 4:response.index('_port=')]
                from_user_port = response[response.index('_port=') + 6:-1]
                conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                conn.connect((from_user_address, int(from_user_port)))
                friend_list.append({'username': from_user, 'conn': conn})
                top_frame_list.append({'username': from_user, 'top': None})
                # conn.send('hi {}'.format(from_user).encode())
            elif response[:11] == '-send_file-':
                filename, file_from_user = response[11:].split(SEPARATOR)
                filename = os.path.basename(filename)
                bytes_read = client_listen.recv(BUFFER_SIZE)
                with open(filename, "wb") as f:
                    while True:
                        f.write(bytes_read)
                        # read 1024 bytes from the socket (receive)
                        bytes_read = client_listen.recv(BUFFER_SIZE)
                        if not bytes_read or bytes_read == '-EOF-'.encode():
                            break
                for top in top_frame_list:
                    if file_from_user == top['username']:
                        top['top'].config(state="normal")
                        top['top'].insert(END, "Received file from {} \n".format(file_from_user))
                        top['top'].config(state="disabled")
            elif response != '':
                from_who = response[:response.index(':')]
                msg = response[response.index(':') + 2:]
                for top in top_frame_list:
                    if from_who == top['username']:
                        if top['top'] is not None:
                            top['top'].config(state="normal")
                            top['top'].insert(END, response)
                            top['top'].insert(END, '\n')
                            top['top'].config(state="disabled")
                found = False
                for msg_db in msg_db_list:
                    if from_who == msg_db['username']:
                        msg_db['message'].append(msg)
                        found = True
                if not found:
                    msg_db_list.append({'username': from_who, 'message': [msg]})
        except:
            client_listen.close()


def connect_user(user, top):
    client.send("-friend_request_to_{}_from_{}-".format(user, account_info['username']).encode())
    top.destroy()
    pass


def block_user(user, top):
    block_list.append(user)
    top.destroy()
    pass



def show_active_users_window(active_users):
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
        listbox.insert(END, username)

    def show_infor(e):
        user = listbox.get(listbox.curselection())
        top_top = Toplevel(root2)
        top_top.title("Show Information")
        top_top.grab_set()
        username_label = Label(top_top, text='USERNAME: {}'.format(user))
        client.send('-send_infor_of_user_{}'.format(user).encode())
        dump_client_info = client.recv(4096)  # receive at most 4096 bytes
        client_info = pickle.loads(dump_client_info)
        username_label.pack()
        age_label = Label(top_top, text='AGE: {}'.format(client_info['age']))
        age_label.pack()
        location_label = Label(top_top, text='LOCATION: {}'.format(client_info['location']))
        location_label.pack()
    listbox.bind('<Double-Button>', show_infor)
    listbox.pack(side=LEFT, fill=BOTH, expand=1)


def accept_request(user, top):
    client.send(('-accept_request_from_{}_to_{}-'.format(account_info['username'], user)).encode())
    friend_requests.remove(user)
    friend_list.append({'username': user, 'conn': None})
    for friend in friend_list:
        if user == friend['username']:
            friend['conn'] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            for d in friend_requests_detail:
                if user == d['username']:
                    friend['conn'].connect((d['ip'], int(d['port'])))

    top_frame_list.append({'username': user, 'top': None})
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

    def show_infor(e):
        user = listbox.get(listbox.curselection())
        top_top = Toplevel(root2)
        top_top.title("Show Information")
        top_top.grab_set()
        username_label = Label(top_top, text='USERNAME: {}'.format(user))
        client.send('-send_infor_of_user_{}'.format(user).encode())
        dump_client_info = client.recv(4096)  # receive at most 4096 bytes
        client_info = pickle.loads(dump_client_info)
        username_label.pack()
        age_label = Label(top_top, text='AGE: {}'.format(client_info['age']))
        age_label.pack()
        location_label = Label(top_top, text='LOCATION: {}'.format(client_info['location']))
        location_label.pack()
    listbox.bind('<Double-Button>', show_infor)
    listbox.pack(side=LEFT, fill=BOTH, expand=1)


def show_active_user():
    client.send("-send_username_list-".encode())
    dump_active_users = client.recv(4096)  # receive at most 4096 bytes
    active_users = pickle.loads(dump_active_users)
    show_active_users_window(active_users)


def connect_to_server(name, age, location, password, confirm_password, top):
    if not age.isnumeric():
        messagebox.showerror("Age", "Age must be a number !!!")
        return
    if password != confirm_password:
        messagebox.showerror("Password", "Password not match !!!")
        return
    global client
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server, port))
    client.send('-send_username_list-'.encode())
    username_list_info = client.recv(4096)
    username_list = pickle.loads(username_list_info)
    for username in username_list:
        if name == username:
            messagebox.showerror("Sign Up", "Username existed")
            return

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


def login(username, password, top):
    login_info = dict()
    login_info['username'] = username
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
    user = askstring('Save conversation', 'Save conversation of user ?')
    for top_frame in top_frame_list:
        if top_frame['username'] == user:
            file_name = asksaveasfilename(
                title="Choose save location",
                filetypes=[('Plain text', '*.txt'), ('Any File', '*.*')])
            try:
                filehandle = open(file_name + ".txt", "w")
            except IOError:
                print("Can't save history.")
                return
            contents = top_frame['top'].get(1.0, END)
            for line in contents:
                filehandle.write(line)
            filehandle.close()
            return
    messagebox.showerror('Info', 'Can not find user')


def change_info(age, location, password, age_label, location_label, top):
    account_info['age'] = age
    account_info['location'] = location
    account_info['password'] = password
    age_label.config(text='AGE: {}'.format(age))
    location_label.config(text='LOCATION: {}'.format(location))
    client.send('-change_information-'.encode())
    dump_client_info = pickle.dumps(account_info)
    client.send(dump_client_info)
    messagebox.showinfo("Update information.", "Information updated")
    top.destroy()


def change_info_window(age_label, location_label):
    top = Toplevel(root2)
    top.title("Change Information")
    top.grab_set()  # prevent users from interacting with the main window
    Label(top, text="Username:").grid(row=0)
    name = Entry(top)
    name.insert(0, account_info['username'])
    name.config(state="disabled")
    name.focus_set()
    name.grid(row=0, column=1)
    Label(top, text="Age:").grid(row=1)
    age = Entry(top)
    age.insert(0, account_info['age'])
    age.focus_set()
    age.grid(row=1, column=1)
    Label(top, text="Location:").grid(row=2)
    location = Entry(top)
    location.insert(0, account_info['location'])
    location.focus_set()
    location.grid(row=2, column=1)
    Label(top, text="Password:").grid(row=3)
    password = Entry(top)
    password.insert(0, account_info['password'])
    password.focus_set()
    password.grid(row=3, column=1)

    btn = Button(top, text="Change", command=lambda: change_info(age.get(), location.get(),
                                                                 password.get(), age_label, location_label, top))
    btn.grid(row=4, column=1)


def run_listen():
    while True:
        try:
            client_listen, address_listen = server_listen.accept()
            t = threading.Thread(target=listen, args=(client_listen, address_listen))
            t.start()
        except:
            server_listen.close()


def main_chat_box():
    # start a thread for listen response from server
    global server_listen
    server_listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_listen.bind((server_server, port_server))
    server_listen.listen()
    t = threading.Thread(target=run_listen)
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
                          command= lambda: change_info_window(age_label, location_label))
    tool_menu.add_separator()  # <hr> to separate exit option
    tool_menu.add_command(label="Exit", command=exit_app)
    menu_bar.add_cascade(label="Tool", menu=tool_menu)
    # ==========================================
    show_menu = Menu(menu_bar, tearoff=0)
    show_menu.add_command(label="Show active users", command=show_active_user)
    show_menu.add_command(label="Show friend requests", command=show_friend_requests)
    menu_bar.add_cascade(label="Show", menu=show_menu)

    root2.config(menu=menu_bar)

    # ===================================-=============
    welcome_title = Label(root2)
    ft = tkFont.Font(family='Times', size=14)
    welcome_title["font"] = ft
    welcome_title["fg"] = "black"
    welcome_title["justify"] = "center"
    welcome_title["text"] = "Welcome to chat app v1 {}".format(account_info['username'])
    welcome_title.place(x=160, y=0, width=330, height=30)

    #  =====================================
    friend_frame = Listbox(root2)
    friend_frame["borderwidth"] = "1px"
    ft = tkFont.Font(family='Times', size=10)
    friend_frame["font"] = ft
    friend_frame["fg"] = "yellow"
    friend_frame["bg"] = "grey"
    friend_frame["justify"] = "center"
    friend_frame.place(x=40, y=40, width=80, height=100)

    added_list = []

    def friend_frame_update():
        for friend in friend_list:
            if friend['username'] not in added_list:
                friend_frame.insert(END, friend['username'])
                added_list.append(friend['username'])
        friend_frame.after(1000, friend_frame_update)

    friend_frame_update()

    def start_chat_with_a_user(is_open):
        which_user = None
        if is_open:
            which_user = income_mess_frame.get(ACTIVE)[:income_mess_frame.get(ACTIVE).index(':')]
        else:
            which_user = friend_frame.get(ACTIVE)
        print(which_user)
        for top_frame in top_frame_list:
            if which_user == top_frame['username']:
                top_main_chat_box = Toplevel(root2)
                top_main_chat_box.title("Conversation with {}".format(which_user))
                # top_frame['top'].grab_set()
                top_width = 350
                top_height = 500
                top_screenwidth = top_main_chat_box.winfo_screenwidth()
                top_screenheight = top_main_chat_box.winfo_screenheight()
                top_alignstr = '%dx%d+%d+%d' % (
                    top_width, top_height, (top_screenwidth - top_width) / 2, (top_screenheight - top_height) / 2)
                top_main_chat_box.geometry(top_alignstr)
                top_main_chat_box.resizable(width=False, height=False)

                top_frame['top'] = Text(top_main_chat_box)
                chat_body_text_scroll = Scrollbar(top_main_chat_box)
                chat_body_text_scroll.pack(side=RIGHT, fill=Y)
                top_frame['top'].pack(side=LEFT, fill=Y)
                chat_body_text_scroll.config(command=top_frame['top'].yview)
                top_frame['top'].config(yscrollcommand=chat_body_text_scroll.set)
                top_frame['top'].place(x=10, y=10, width=295, height=429)
                top_frame['top'].insert(END, "Press Enter to send message\n")
                if is_open:
                    for msg_db in msg_db_list:
                        if which_user == msg_db['username']:
                            for line in msg_db['message']:
                                top_frame['top'].insert(END, which_user + ': ' + line)
                                top_frame['top'].insert(END, '\n')
                else:
                    top_frame['top'].insert(END, "You are chatting with {} \n".format(which_user))
                top_frame['top'].config(state="disabled")

                def send_file():
                    file = askopenfilename(title="Choose a file", initialdir=os.path.dirname(__file__))
                    filename = str(file.split('/')[-1])
                    file_size = os.path.getsize(file)
                    for friend in friend_list:
                        if which_user == friend['username']:
                            conn = friend['conn']
                            conn.send(
                                ('-send_file-{}{}{}'.format(filename, SEPARATOR, account_info['username'])).encode())
                            time.sleep(0.1)
                            with open(file, "rb") as f:
                                while True:
                                    bytes_read = f.read(BUFFER_SIZE)
                                    if not bytes_read:
                                        break
                                    conn.send(bytes_read)
                                time.sleep(0.1)
                                conn.send('-EOF-'.encode())
                            top_frame['top'].config(state="normal")
                            top_frame['top'].insert(END, "file sent. Size: {} \n".format(file_size))
                            top_frame['top'].config(state="disabled")

                def send_emoji():
                    emoji_frame = Toplevel(top_main_chat_box, height=100, width=50)
                    emoji_frame.title("Emoji")
                    emoji_list = Listbox(emoji_frame)
                    emoji_list.pack()
                    emoji_list.insert(END, "\N{grinning face}")
                    emoji_list.insert(END, "\N{grinning face with smiling eyes}")
                    emoji_list.insert(END, "\N{slightly smiling face}")
                    emoji_list.insert(END, "\N{winking face}")
                    emoji_list.insert(END, "\N{smiling face with sunglasses}")
                    emoji_list.insert(END, "\N{face with tears of joy}")
                    emoji_list.insert(END, "\N{upside-down face}")

                    def handle_emoji(e):
                        top_chat_box.insert(END, emoji_list.get(emoji_list.curselection()))
                    emoji_list.bind('<Double-Button>', handle_emoji)

                top_send_file_btn = Button(top_main_chat_box, text="Send File", command=send_file)
                top_send_file_btn.place(x=270, y=440, width=60, height=20)
                top_send_emoji_btn = Button(top_main_chat_box, text="Send Emoji", command=send_emoji)
                top_send_emoji_btn.place(x=270, y=465, width=60, height=20)

                top_chat_box = Entry(top_main_chat_box)
                top_chat_box["borderwidth"] = "1px"
                top_chat_box["font"] = tkFont.Font(family='Times', size=10)
                top_chat_box["fg"] = "black"
                top_chat_box.place(x=10, y=450, width=248, height=31)

                def send_text(e):
                    for friend in friend_list:
                        if which_user == friend['username']:
                            text = account_info['username'] + ": " + top_chat_box.get()
                            try:
                                friend['conn'].send(text.encode())
                            except:
                                print('can not send message')
                            top_frame['top'].config(state="normal")
                            top_frame['top'].insert(END, 'You: ' + top_chat_box.get() + '\n')
                            top_frame['top'].config(state="disabled")

                    top_chat_box.delete(0, END)

                top_chat_box.bind("<Return>", send_text)

    def foo(e):
        start_chat_with_a_user(False)

    friend_frame.bind('<Double-Button>', foo)

    # ===========================
    income_mess_frame = Listbox(root2)
    income_mess_frame["borderwidth"] = "1px"
    ft = tkFont.Font(family='Times', size=10)
    income_mess_frame["font"] = ft
    income_mess_frame["fg"] = "yellow"
    income_mess_frame["bg"] = "grey"
    income_mess_frame.place(x=40, y=150, width=80, height=268)

    def open_conversation_with_user(*args):
        start_chat_with_a_user(True)

    income_mess_frame_added_list = []

    def income_mess_frame_update():
        for msg_db in msg_db_list:
            if msg_db['username'] not in income_mess_frame_added_list:
                income_mess_frame.insert(END, msg_db['username'] + ': ' + msg_db['message'][-1])
                income_mess_frame_added_list.append(msg_db['username'])
        income_mess_frame.after(3000, income_mess_frame_update)

    income_mess_frame_update()
    income_mess_frame.bind('<Double-Button>', open_conversation_with_user)
    # =================================

    main_body = Frame(root2, height=100, width=447)

    main_body_text = Text(main_body)
    body_text_scroll = Scrollbar(main_body)
    main_body_text.focus_set()
    body_text_scroll.pack(side=RIGHT, fill=Y)
    main_body_text.pack(side=LEFT, fill=Y)
    body_text_scroll.config(command=main_body_text.yview)
    main_body_text.config(yscrollcommand=body_text_scroll.set)
    main_body.place(x=130, y=40)

    main_body_text.insert(END, "Welcome to \n\n")
    main_body_text.insert(END, " #####  #     #    #    #######       #    ######  ######  \n")
    main_body_text.insert(END, "#     # #     #   # #      #         # #   #     # #     #\n")
    main_body_text.insert(END, "#       #     #  #   #     #        #   #  #     # #     #\n")
    main_body_text.insert(END, "#       ####### #     #    #       #     # ######  ######\n")
    main_body_text.insert(END, "#       #     # #######    #       ####### #       #\n")
    main_body_text.insert(END, "#     # #     # #     #    #       #     # #       #\n")
    main_body_text.insert(END, " #####  #     # #     #    #       #     # #       #       \n")

    main_body_text.config(state=DISABLED)

    # ==========================================
    main_label = Label(main_body, text='YOUR INFORMATION:', font=('Arial', 23))
    username_label = Label(main_body, text='USERNAME: {}'.format(account_info['username']), font=('Arial', 13))
    age_label = Label(main_body, text='AGE: {}'.format(account_info['age']), font=('Arial', 13))
    location_label = Label(main_body, text='LOCATION: {}'.format(account_info['location']), font=('Arial', 13))
    main_label.place(x=10, y=160)
    username_label.place(x=10, y=210)
    age_label.place(x=10, y=240)
    location_label.place(x=10, y=270)

    # ==========================================

    text_input = Entry(root2)
    text_input["borderwidth"] = "1px"
    ft = tkFont.Font(family='Times', size=10)
    text_input["font"] = ft
    text_input["fg"] = "black"
    text_input["justify"] = "center"
    text_input["text"] = "Entry"
    text_input.place(x=40, y=440, width=458, height=30)
    text_input.config(state=DISABLED)
    # ==================================

    exit_btn = Button(root2)
    exit_btn["bg"] = "#6b6b6b"
    ft = tkFont.Font(family='Times', size=10)
    exit_btn["font"] = ft
    exit_btn["fg"] = "#ffffff"
    exit_btn["justify"] = "center"
    exit_btn["text"] = "EXIT"
    exit_btn.place(x=510, y=440, width=70, height=25)
    exit_btn['command'] = exit_app

    root2.mainloop()


def exit_app():
    for friend in friend_list:
        friend['conn'].close()
    server_listen.close()
    client.close()
    root2.destroy()
    sys.exit()


def main():
    # ==== init tk window =======
    global root
    root = Tk()
    root.title("Chat APP v1")
    # =====================================

    width = 200
    height = 400
    screenwidth = root.winfo_screenwidth()
    screenheight = root.winfo_screenheight()
    alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
    root.geometry(alignstr)
    root.resizable(width=False, height=False)

    register_btn = Button(root)
    register_btn["bg"] = "#6b6b6b"
    ft = tkFont.Font(family='Times', size=10)
    register_btn["font"] = ft
    register_btn["fg"] = "#ffffff"
    register_btn["justify"] = "center"
    register_btn["text"] = "Register"
    register_btn.place(x=70, y=190, width=70, height=25)
    register_btn["command"] = connect_to_server_window

    login_btn = Button(root)
    login_btn["bg"] = "#6b6b6b"
    ft = tkFont.Font(family='Times', size=10)
    login_btn["font"] = ft
    login_btn["fg"] = "#ffffff"
    login_btn["justify"] = "center"
    login_btn["text"] = "Login"
    login_btn.place(x=70, y=240, width=70, height=25)
    login_btn["command"] = login_window

    login_label = Label(root)
    ft = tkFont.Font(family='Times', size=10)
    login_label["font"] = ft
    login_label["fg"] = "black"
    login_label["justify"] = "center"
    login_label["text"] = "CHAT APP"
    login_label.place(x=70, y=80, width=70, height=25)

    login_footer = Label(root)
    ft = tkFont.Font(family='Times', size=6)
    login_footer["font"] = ft
    login_footer["fg"] = "#c8c3bc"
    login_footer["justify"] = "center"
    login_footer["text"] = "2022"
    login_footer.place(x=50, y=350, width=99, height=30)

    root.mainloop()


if __name__ == "__main__":
    main()
