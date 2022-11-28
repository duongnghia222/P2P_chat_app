from tkinter import *
from tkinter import messagebox
import threading
import socket
import pickle
FORMAT = 'utf-8'

# =================
root = None
client = None
server = None
port = None
# ==================
friends = []
current_connections = []
account_id = 1
account_info = {
        "id": account_id,
        "username": "",
        "age": 999}



def show_active_users_window(active_users):
    """Displays
    """
    top = Toplevel(root)
    top.title("Active Users")
    top.grab_set()
    scrollbar = Scrollbar(top, orient=VERTICAL)
    listbox = Listbox(top, yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)
    scrollbar.pack(side=RIGHT, fill=Y)
    # buttons = Frame(cWindow)
    # cBut = Button(buttons, text="Connect",
    #               command=lambda: contacts_connect(
    #                                   listbox.get(ACTIVE).split(" ")))
    # cBut.pack(side=LEFT)
    # dBut = Button(buttons, text="Remove",
    #               command=lambda: contacts_remove(
    #                                   listbox.get(ACTIVE).split(" "), listbox))
    # dBut.pack(side=LEFT)
    # aBut = Button(buttons, text="Add",
    #               command=lambda: contacts_add(listbox, cWindow))
    # aBut.pack(side=LEFT)
    # buttons.pack(side=BOTTOM)

    for user in active_users:
        listbox.insert(END, user['username'])
    listbox.pack(side=LEFT, fill=BOTH, expand=1)


def show_active_user():
    client.send("-show_active_user-".encode())
    dump_active_users = client.recv(4096)  # receive at most 4096 bytes
    active_users = pickle.loads(dump_active_users)
    show_active_users_window(active_users)


def connect_to_server(name, age, top):
    global account_info
    account_info['username'] = name
    account_info['age'] = age
    global server
    server = "192.168.1.8"
    global port
    port = 2222
    global client
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server, port))
    dump_client_info = pickle.dumps(account_info)
    client.send(dump_client_info)
    top.destroy()


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
    btn = Button(top, text="Start chat", command=lambda: connect_to_server(name.get(), age.get(), top))
    btn.grid(row=2, column=1)
    pass

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


def join_server():
    pass

def main():
    # ==== init tk window =======
    global root
    root = Tk()
    root.title("Chat APP v1")
    # =====================================

    # ==== show the join button at bottom ===========
    root.geometry("360x720")
    connect_button = Button(root, text='Join Server', command=join_server)
    connect_button.pack(side=BOTTOM)

    menu_bar = Menu(root, tearoff=0)

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
    menu_bar.add_cascade(label="Show", menu=show_menu)

    root.config(menu=menu_bar)


    connect_button = Button(root, text='Register', command=connect_to_server_window)
    connect_button.pack()



    # connection_menu = Menu(menu_bar, tearoff=0)
    # connection_menu.add_command(label="Quick Connect", command=QuickClient)
    # connection_menu.add_command(
    #     label="Connect on port", command=lambda: client_options_window(root))
    # connection_menu.add_command(
    #     label="Disconnect", command=lambda: processFlag("-001"))
    # menu_bar.add_cascade(label="Connect", menu=connection_menu)
    #
    # server_menu = Menu(menu_bar, tearoff=0)
    # server_menu.add_command(label="Launch server", command=QuickServer)
    # server_menu.add_command(label="Listen on port",
    #                         command=lambda: server_options_window(root))
    # menu_bar.add_cascade(label="Server", menu=server_menu)
    #
    # menu_bar.add_command(label="Contacts", command=lambda:
    #                     contacts_window(root))

    # root.config(menu=menu_bar)
    #
    # main_body = Frame(root, height=20, width=50)
    #
    # main_body_text = Text(main_body)
    # body_text_scroll = Scrollbar(main_body)
    # main_body_text.focus_set()
    # body_text_scroll.pack(side=RIGHT, fill=Y)
    # main_body_text.pack(side=LEFT, fill=Y)
    # body_text_scroll.config(command=main_body_text.yview)
    # main_body_text.config(yscrollcommand=body_text_scroll.set)
    # main_body.pack()
    #
    # main_body_text.insert(END, "Welcome to the chat program!")
    # main_body_text.config(state=DISABLED)

    # text_input = Entry(root, width=60)
    # text_input.bind("<Return>", processUserText)  # when press enter function is called
    # text_input.pack()

    # statusConnect = StringVar()
    # statusConnect.set("Connect")
    # clientType = 1
    # Radiobutton(root, text="Client", variable=clientType,
    #             value=0, command=toOne).pack(anchor=E)
    # Radiobutton(root, text="Server", variable=clientType,
    #             value=1, command=toTwo).pack(anchor=E)
    # connecter = Button(root, textvariable=statusConnect,
    #                    command=lambda: connects(clientType))
    # connecter.pack()
    #
    # load_contacts()
    root.mainloop()

if __name__ == "__main__":
    main()