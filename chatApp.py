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
server = socket.gethostbyname(socket.gethostname())  # ip of the server
port = 2222
# =========
server_server = socket.gethostbyname(socket.gethostname())   # ip of the server of the app to receive response (user gethostbyname)
port_server = 2223
# port_for_response = 2223
# ==================
friend_requests = []
block_list = []
account_info = dict()
friend_list = []
top_frame_list = []
msg_db_list = []

def listen(client_listen, address_listen):
    while True:
        try:
            response = client_listen.recv(4000)
            response = response.decode()
            if response[:21] == "-friend_request_from_":
                from_user = response[21:-1]
                friend_requests.append(from_user)
            elif response[:21] == '-accept_request_from_':
                from_user = response[21:response.index('_ip=')]
                from_user_address = response[response.index('_ip=')+4:response.index('_port=')]
                from_user_port = response[response.index('_port=')+6:-1]
                conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                conn.connect((from_user_address, int(from_user_port)))
                friend_list.append({'username': from_user, 'conn': conn})
                top_frame_list.append({'username': from_user, 'top': None})
                # conn.send('hi {}'.format(from_user).encode())
            elif response != '':

                print(response)
                from_who = response[:response.index(':')]
                msg = response[response.index(':')+2:]
                for top in top_frame_list:
                    if from_who == top['username']:
                        if top['top'] is not None:
                            print(top['top'])
                            top['top'].insert(END, response)
                            top['top'].insert(END, '\n')
                found = False
                for msg_db in msg_db_list:
                    if from_who == msg_db['username']:
                        msg_db['message'].append(msg)
                        found = True
                if not found:
                    msg_db_list.append({'username':from_who, 'message':[msg]})
        except:
            # print('disconnect with', address_listen)
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
    friend_list.append({'username': user, 'conn': None})
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
    while True:
        try:
            client_listen, address_listen = server_listen.accept()
            if friend_list:
                friend_list[-1]['conn'] = client_listen
            t = threading.Thread(target=listen, args=(client_listen, address_listen))
            t.start()
        except:
            server_listen.close()



def send_file():
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
        for top_frame in top_frame_list:
            if friend_frame.get(ACTIVE) == top_frame['username']:
                top_main_chat_box = Toplevel(root2)
                top_main_chat_box.title("Conversation with {}".format(friend_frame.get(ACTIVE)))
                # top_frame['top'].grab_set()
                top_width = 320
                top_height = 500
                top_screenwidth = top_main_chat_box.winfo_screenwidth()
                top_screenheight = top_main_chat_box.winfo_screenheight()
                top_alignstr = '%dx%d+%d+%d' % (top_width, top_height, (top_screenwidth - top_width) / 2, (top_screenheight - top_height) / 2)
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
                        if friend_frame.get(ACTIVE) == msg_db['username']:
                            for line in msg_db['message']:
                                top_frame['top'].insert(END, friend_frame.get(ACTIVE) + ': ' + line)
                                top_frame['top'].insert(END, '\n')
                else:
                    top_frame['top'].insert(END, "You are chatting with {} \n".format(friend_frame.get(ACTIVE)))





                top_send_file_btn = Button(top_main_chat_box)
                top_send_file_btn["bg"] = "#6b6b6b"
                ft = tkFont.Font(family='Times', size=10)
                top_send_file_btn["font"] = ft
                top_send_file_btn["fg"] = "#ffffff"
                top_send_file_btn["text"] = "       Send File"
                top_send_file_btn.place(x=240, y=450, width=70, height=30)
                top_send_file_btn["command"] = send_file

                top_chat_box = Entry(top_main_chat_box)
                top_chat_box["borderwidth"] = "1px"
                ft = tkFont.Font(family='Times', size=10)
                top_chat_box["font"] = ft
                top_chat_box["fg"] = "black"
                top_chat_box.place(x=10, y=450, width=248, height=31)

                def send_text(e):
                    for friend in friend_list:
                        if friend_frame.get(ACTIVE) == friend['username']:
                            text = account_info['username'] + ": " + top_chat_box.get()
                            # print(friend_list)
                            # print(top_frame['top'])
                            try:
                                friend['conn'].send(text.encode())
                            except:
                                print('can not send message')
                            top_frame['top'].insert(END, 'You: '+ top_chat_box.get() +'\n')


                    top_chat_box.delete(0, END)
                top_chat_box.bind("<Return>", send_text)


    def foo(e):
        start_chat_with_a_user(False)
    friend_frame.bind('<Double-Button>', foo)

    # ===========================
    imcome_mess_frame = Listbox(root2)
    imcome_mess_frame["borderwidth"] = "1px"
    ft = tkFont.Font(family='Times', size=10)
    imcome_mess_frame["font"] = ft
    imcome_mess_frame["fg"] = "yellow"
    imcome_mess_frame["bg"] = "grey"
    imcome_mess_frame.place(x=40, y=150, width=80, height=268)

    def open_conversation_with_user(*args):
        start_chat_with_a_user(True)




    imcome_mess_frame_added_list = []
    def imcome_mess_frame_update():
        for msg_db in msg_db_list:
            if msg_db['username'] not in imcome_mess_frame_added_list:
                imcome_mess_frame.insert(END, msg_db['username'] + ':' +msg_db['message'][-1])
                imcome_mess_frame_added_list.append(msg_db['username'])
        imcome_mess_frame.after(1000, imcome_mess_frame_update)
    imcome_mess_frame_update()
    imcome_mess_frame.bind('<Double-Button>', open_conversation_with_user)
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
    main_body_text.insert(END, '\n\n')

    main_body_text.config(state=DISABLED)

    # ==========================================


    text_input = Entry(root2)
    text_input["borderwidth"] = "1px"
    ft = tkFont.Font(family='Times', size=10)
    text_input["font"] = ft
    text_input["fg"] = "black"
    text_input["justify"] = "center"
    text_input["text"] = "Entry"
    text_input.place(x=40, y=440, width=458, height=30)
    # text_input.bind("<Return>", send_text)
    text_input.config(state=DISABLED)
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

    GLabel_60 = Label(root)
    ft = tkFont.Font(family='Times', size=10)
    GLabel_60["font"] = ft
    GLabel_60["fg"] = "black"
    GLabel_60["justify"] = "center"
    GLabel_60["text"] = "CHAT APP"
    GLabel_60.place(x=70, y=80, width=70, height=25)

    GLabel_271 = Label(root)
    ft = tkFont.Font(family='Times', size=6)
    GLabel_271["font"] = ft
    GLabel_271["fg"] = "#c8c3bc"
    GLabel_271["justify"] = "center"
    GLabel_271["text"] = "2022"
    GLabel_271.place(x=50, y=350, width=99, height=30)


    root.mainloop()


if __name__ == "__main__":
    main()
