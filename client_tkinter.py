from tkinter import *
from tkinter import messagebox
import PIL
from PIL import ImageTk
import re
from socket import *
from select import select
import _thread
import sys
global data
global admin_password
'''
longest message - 65 charachters
'''
#function that gets an open port within a set range
def get_open_port():
    start_port = 50000
    for i in range(start_port,start_port+3000):
        sock = socket(AF_INET,SOCK_DGRAM)
        try:
            sock.bind(("",i))
            return i
        except:
            pass

#in order to start the connection this function waits on a random port and gets the port,ip via a broadcast message
#then it returns it so the app can connect to the server
def get_info_from_host():
    global admin_password
    open_port = get_open_port()
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.bind((gethostbyname(gethostname()),open_port))
    data,adress = sock.recvfrom(1054)
    pass_pattern = re.compile(r"admin password:<(.+)>")
    data = data.decode()
    admin_password = re.findall(pattern=pass_pattern,string = data)[0]
    print(f"got info from {adress} and he is saying: {data}")
    return adress

#clear the screen
def clear_screen():
    for widget in root.winfo_children():
        widget.destroy()

#when trying to exit incorrectly this function shows an eror message
def dont_allow_exit():
    messagebox.showerror(title="No exit", message="You cannot exit the application using that button, you have to type exit like every other human being")

#returns the protocol of the message and if the message is sendable
def get_type(msg):
    proto = ""
    echo_pattern = re.compile(r"\s*(Echo).*")
    tmp = re.findall(echo_pattern,msg)
    if(len(tmp)!=0):
        proto += "echo"
    time_pattern = re.compile(r"\s*(time).*")
    tmp = re.findall(time_pattern,msg)
    if(len(tmp)!=0):
        proto += "time"
    HMM_pattern = re.compile(r"\s*(HMM).*")
    tmp = re.findall(HMM_pattern,msg)
    if(len(tmp)!=0):
        proto += "HMM"
    DM_pattern = re.compile(r"\s*(DM).*")
    tmp = re.findall(DM_pattern,msg)
    if(len(tmp)!=0):
        proto += "DM"
    CAP_pattern = re.compile(r"\s*(CAP).*")
    tmp = re.findall(CAP_pattern,msg)
    if(len(tmp)>0):
        proto+="CAP"
    CN_pattern = re.compile(r"\s*(CN).*")
    tmp = re.findall(CN_pattern,msg)
    if(len(tmp)>0):
        proto+="CN"
    GAP_pattern = re.compile(r"\s*(GAP).*")
    tmp = re.findall(GAP_pattern,msg)
    if(len(tmp)>0):
        proto+="GAP"
    kick_pattern = re.compile(r"\s*(kick).*")
    tmp = re.findall(kick_pattern,msg)
    if(len(tmp)>0):
        proto+="kick"
    if(proto==""):
        proto = "None"
    if(len(proto)>4 or proto=="DMCN"):
        messagebox.showerror(title = "too many protocols",message="You had the code of more than 1 protocol in your message")
        return False,proto
    return True,proto
    
#this function displays the options of the app in the GUI
def print_options():
    frame = Frame(root)
    options = ["None - send to everyone","Echo - echo to server","time - time in the server settings","HMM - how many members are connected","DM - direct message a person","CAP - change admin password (requires old one)", "CN - change your name","exit - exit the application","QUIT - close the server (requires admin password)", "GAP - display all current poeple connected","kick - kick someone from the chatroom (requires admin password)"]
    for i in options:
        lbl = Label(frame,text=i,font=("Arial",15))
        lbl.pack(side=TOP,anchor=W)
    img = ImageTk.PhotoImage(PIL.Image.open("chat_room.png"))
    img_lable = Label(frame, image=img, borderwidth=0)
    img_lable.image = img
    img_lable.pack(side=BOTTOM)
    frame.pack(side=RIGHT,anchor=N)

#this function prints the chat in the GUI
def print_chat():
    global name_entry_var
    global text_entry
    global lbl_lst
    global var_lst
    global you_var
    global name
    global butt
    lbl_lst = []
    var_lst = []
    frame = Frame(root)
    text_list = ["Welcome to the chat room!","Feel free to chat with your pals and use our variety of commands as you please","In case you forget the commands:","They are displayed at the top right corner.","Enjoy!"]
    for i in range(len(text_list)): 
        lbl = Label(frame,text = text_list[i],font=("Arial",15))
        lbl.pack(side=TOP,anchor=W)
    for i in range(10):
        var = StringVar()
        sttring = ""
        var.set(sttring)
        lbl = Label(frame,textvariable=var,font=("Arial",15))
        lbl.pack(side=TOP,anchor=W,pady=5)
        lbl_lst.append(lbl)
        var_lst.append(var)
    name_entry_var = StringVar()
    name_entry_var.set("")
    text_entry = Entry(frame,width=75,textvariable=name_entry_var,font=("Arial",15))
    text_entry.pack(anchor=W,side=TOP,pady=20)
    butt = Button(frame,text="Send!",font=("Arial",15),command=send_message)
    butt.pack(anchor=W,side=TOP)
    you_var = StringVar()
    you_var.set(f"You are seen publicly as: {name}, and your respective ID is: {id_num}")
    you_lbl = Label(frame,font=("Arial",15),textvariable=you_var)
    you_lbl.pack(side=BOTTOM,anchor=W)
    frame.pack(side=LEFT,anchor=N)

#this function connects the the server after getting its info
def manage_connection():
    global sock
    adress = get_info_from_host()
    while True:
        try:
            sock = socket(AF_INET,SOCK_STREAM)
            sock.connect((adress))
            break
        except:
            pass

#this function works with the GAP protocol and opens a seperate window to display all the other people
def display_all_people():
    display_window = Toplevel(height=30,width=30)
    msg_lbl = Label(display_window,text="Here are all the people in the chat room right now:", font=("Arial",15))
    msg_lbl.pack(side=TOP,anchor=W)
    len = sock.recv(1054).decode()
    for i in range(int(len)):
        sock.send("ok".encode())
        data = sock.recv(1054).decode()
        lbl = Label(display_window, text = data, font=("Arial",15))
        lbl.pack(side=TOP,anchor=W)

#this function runs on a diffrent thread and updates the message when they are recevied
#note - i am aware that using a linked list would be better here instead of normal list
#when trying to update the labels but i didn't know if we were allowed to use it
def get_messages_and_display():
    global lbl_lst
    global var_lst
    global you_var
    global stopping
    global text_entry
    global butt
    global admin_password
    stopping = False
    data_lst = [""]*10
    while True:
        try:
            if(stopping):
                _thread.exit()
            global sock
            data = sock.recv(1054).decode() 
            proto = get_type(data)[1]
            if(proto=="GAP"):
                display_all_people()
            else:
                if proto=="CAP":
                    pass_pattern = re.compile(r'is:(.+)$')
                    try:
                        admin_password = "hye"
                        admin_password = re.findall(pattern = pass_pattern, string = data)[0]
                    except:
                        pass
                if not data:
                    messagebox.showinfo(title="You have disconnected",message="We are very sorry to infrom you that you have been kicked or the server has been shut down, press escape to close the application")
                    butt['state'] = DISABLED
                    text_entry['state'] = DISABLED
                    root.bind('<Escape>',close_win) 
                    break
                is_cn = False
                cn_pattern = re.compile(r'^CN')
                try:
                    cn = re.findall(pattern=cn_pattern,string = data)[0]
                    is_cn=True
                except:
                    pass
                if(is_cn):
                    name_pattern = re.compile('name:<(.+?)>$')
                    new_name = re.findall(string=data,pattern=name_pattern)[0]
                    you_var.set(f"You are seen publicly as: {new_name}, and your respective ID is: {id_num}")
                else:
                    tmp = []
                    for i in range(9):
                        tmp.append(data_lst[i+1])
                    tmp.append(data)
                    data_lst = tmp
                    for i in range(10):
                        var_lst[i].set(data_lst[i])
        except ConnectionResetError:
            messagebox.showinfo(title="Server has been closed",message="The server has been closed, press escape to exit the app")
            butt['state'] = DISABLED
            text_entry['state'] = DISABLED
            root.bind('<Escape>',close_win)
            break
        except:
            pass

#a function that cloes the window
def close_win(*args):
    global sock
    global stopping
    stopping = True
    root.destroy()
    sock.close()
    sys.exit(1)

#function that sends the messages to the server, it also deals with the logic of confirming and checking admin 
#password etc
def send_message():
    global sock
    global text_entry
    global butt
    global name
    data = text_entry.get()
    if(data=="exit"):
        root.bind('<Escape>',close_win)
        messagebox.showinfo(title="Close App",message="The system has recognized your request to leave the app, press escape in order to close it")
        butt['state'] = DISABLED
        text_entry['state'] = DISABLED
    else:
        if(len(data)+len(name)>70):
            messagebox.showerror(title="too long of a message", message="Sorry but this app is a chatroom for short messages, you can try to split your message")
        else:
            tupp = get_type(data)
            can_send =  tupp[0]
            proto = tupp[1]
            if(proto=="CAP" or data=="QUIT" or proto=="kick"):
                get_admin_password()
            else:
                if can_send:
                    sock.send(data.encode())
                    text_entry.delete(0,END)

#after logging in this function displays the GUI and srtats a thread to update the chat
def chat_screen():
    global id_num
    global name
    global admin_password
    clear_screen()
    msg = f"NEWCONN name:{name}"
    root.protocol("WM_DELETE_WINDOW", dont_allow_exit)
    sock.send(msg.encode())
    id_num = int(sock.recv(1054).decode())
    root.geometry("1400x800+100+100")
    print_options()
    print_chat()
    _thread.start_new_thread(get_messages_and_display,())

#gets and check the name before logging in
def get_and_check_name():
    global name
    name = name_entry.get()
    name_entry.delete(0,END)
    pattern = re.compile(r"[a-zA-Z]")
    tmp = re.findall(pattern=pattern,string=name)
    if(len(name)>20):
        messagebox.showerror(title = "name eror",message="sorry but the name can not be longer than 20 letters")
    else:
        if(len(tmp)>0):
            chat_screen()
        else:
            messagebox.showerror(title = "name eror",message="You need to have at least a single letter from the english alphabet in your name")

#when using a command that needs admin password, this function opens a top level to recieve it 
#and checks it using the check_admin_password() function
def get_admin_password():
    global top
    top = Toplevel()
    lbl = Label(top,text = "Enter admin password", font=("Arial",15))
    lbl.pack()
    pass_entry = Entry(top,font=("Arial",15))
    pass_entry.pack()
    submit_but = Button(top,text="Submit!",font=("Arial",15),command=lambda :check_admin_password(pass_entry))
    submit_but.pack()

#checks the admin password after receving it, if correct it sends the message
def check_admin_password(pass_entry):
    global admin_password
    global text_entry
    global sock
    global top
    data = text_entry.get()
    password = pass_entry.get()
    if(str(password) == str(admin_password)):
        sock.send(data.encode())
        text_entry.delete(0,END)
        top.destroy()
    else:
        messagebox.showerror(message="Incorrect Password, try again")

#cresting the first screen GUI and waiting to get server's details
data = [""]*10
manage_connection()
root = Tk()
root.geometry("800x600+100+100")
root.resizable(False, False)
title_msg = Label(root,text="Welcome to the chatroom",font=("Arial",15))
title_msg.pack(pady=15)
name_frame = Frame(root)
name_msg = Label(name_frame,text="name:",font=("Arial",15))
name_msg.pack(side=LEFT,anchor=N)
name_var = StringVar()
name_entry = Entry(name_frame,font=("Arial",18))
name_entry.pack(side=LEFT,anchor=N,padx=10)
name_button = Button(name_frame,text="Log-In!",font=("Arial",13),command=get_and_check_name)
name_button.pack(side=LEFT,anchor=N,padx=10)
name_frame.pack()
img = ImageTk.PhotoImage(PIL.Image.open("chat.png"))
img_lable = Label(root, image=img, borderwidth=0)
img_lable.image = img
img_lable.pack(pady=30)
root.mainloop()