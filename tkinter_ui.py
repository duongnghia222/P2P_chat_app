from tkinter import *
from tkinter import messagebox

root = None

def init_tk():
    global root
    root = Tk()
    root.title("Chat APP v1")

def join_ui():
    root.geometry("360x720")
    connect_button = Button(root, text='Register', command=join_server)
    connect_button.pack(side=BOTTOM)