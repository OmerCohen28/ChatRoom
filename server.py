from socket import *
import _thread
import time
from select import select
import re
import datetime
import sys
import cmd_project
import ipaddress
admin_password = input("choose admin password: ") #the initial admin password

#a function that finds and returns the protocol of the recevied message.
def get_type(msg):
    echo_pattern = re.compile(r"\s*(Echo).*")
    tmp = re.findall(echo_pattern,msg)
    if(len(tmp)!=0):
        return "echo"
    time_pattern = re.compile(r"\s*(time).*")
    tmp = re.findall(time_pattern,msg)
    if(len(tmp)!=0):
        return "time"
    HMM_pattern = re.compile(r"\s*(HMM).*")
    tmp = re.findall(HMM_pattern,msg)
    if(len(tmp)!=0):
        return "HMM"
    DM_pattern = re.compile(r"\s*(DM).*")
    tmp = re.findall(DM_pattern,msg)
    if(len(tmp)!=0):
        return "DM"
    CAP_pattern = re.compile(r"\s*(CAP).*")
    tmp = re.findall(CAP_pattern,msg)
    if(len(tmp)>0):
        return "CAP"
    CN_pattern = re.compile(r"\s*(CN).*")
    tmp = re.findall(CN_pattern,msg)
    if(len(tmp)>0):
        return "CN"
    kick_pattern = re.compile(r"\s*(kick).*")
    tmp = re.findall(kick_pattern,msg)
    if(len(tmp)>0):
        return "kick"
    GAP_pattern = re.compile(r"\s*(GAP).*")
    tmp = re.findall(GAP_pattern,msg)
    if(len(tmp)>0):
        return "GAP"
    return "None"

#this function uses a previous project in order to find the broadcast ip adrress of the current LAN 
#without hardcoding it
def get_network_broadcast_adress():
    IP_Data = cmd_project.fetch_data()
    addr = f"{IP_Data[0]}/{IP_Data[3]}"
    network = ipaddress.IPv4Network(addr, strict=False).broadcast_address
    return network

#this function runs on a diffrent thread throughout the whole run of the server
#it checks for each connection whther it should send a timeout message/disconnet it
def send_timeout_message():
    while True:
        time.sleep(1)
        for sock in all_sockets:
            if sock != conn_sock:
                try:
                    if int(time.time()) - int(sock_time_dic[sock]) == int(sock_counter_time_dic[sock]):
                        if sock_counter_time_dic[sock] == 70:
                            sock.send("You have been out for too long, im sorry but i have to kick you (you also have been kind of annoying)".encode())
                            sock.close()
                            del all_sockets[all_sockets.index(sock)]
                        else:
                            sock.send("server: Wake up!!!".encode())
                            sock_counter_time_dic[sock]+=10
                            sock_time_dic[sock] = time.time()
                except:
                    pass   

#this function also runs on a diffrent thread and once every 2 seconds it sends the server info to everyone on the LAN
#so new people will be able to connect
def send_info():
    ip_addr = get_network_broadcast_adress()
    sock_info = socket(AF_INET,SOCK_DGRAM)
    sock_info.bind((gethostbyname(gethostname()),50500))
    while True:
        time.sleep(2)
        for i in range(50000,53000):
            if(i != 50500):
                sock_info.sendto(f"hello dear client, i am sitting at port 50500 comftorable, come join me. admin password:<{admin_password}>".encode(),(str(ip_addr),i))

sock_time_dic = {} #the time since they last sent message
sock_counter_time_dic = {} #the counter for the current time till the connection times out
all_sockets = [] #all socks
id_num=0 #current id num
clients_data = [] #sock,name,id tupples

_thread.start_new_thread(send_info,())
_thread.start_new_thread(send_timeout_message,())

conn_sock = socket(AF_INET,SOCK_STREAM)
all_sockets.append(conn_sock)
conn_sock.bind((gethostbyname(gethostname()),50500))
conn_sock.listen(2)

while True:
    try:
        read_sockets, write_sockets, error_sockets = select(all_sockets,all_sockets,[])
    except:
        pass
    for sock in read_sockets:
        if sock == conn_sock:
            client_socket,addr = conn_sock.accept()
            all_sockets.append(client_socket)
        else:
            try:
                data = sock.recv(1054).decode()
                if not data:
                    sock.close()
                    del all_sockets[all_sockets.index(sock)]
                if(data=="QUIT"): #if client sent QUIT protocol message shut down the server
                    for sockobj in all_sockets:
                        sockobj.close()
                    sys.exit()
            except ConnectionResetError:
                try:
                    del all_sockets[all_sockets.index(sock)]
                except:
                    pass
                continue
            except OSError:
                continue
            sock_time_dic[sock] = int(time.time()) #updates the last sent dictionary
            test_conn = "NEWCONN"
            is_conn=True
            for i in range(7):
                try:
                    if(data[i]!=test_conn[i]):
                        is_conn = False
                except:
                    is_conn=False
            if is_conn: #testing whther it is a new client
                name_pattern = re.compile(r"name:(.+)$")
                name = re.findall(pattern=name_pattern,string=data)
                if(len(name)>0):
                    name = name[0]
                    clients_data.append([sock,name,id_num])
                    sock.send(str(id_num).encode())                    
                    id_num+=1
                    sock_time_dic[sock] = int(time.time())
                    sock_counter_time_dic[sock] = 10
            else:
                name_of_sender = ""
            
                for sock_sender,name,id_num_loop in clients_data:
                    if sock_sender==sock:
                        name_of_sender = name
                        break

                proto = get_type(data)
                #analayzing the different protocols
                if(proto=="None"):
                    read,write,error = select([],all_sockets,[])
                    for sockobj in write:
                        msg = f"{name_of_sender}: {data}"
                        sockobj.send(msg.encode())

                elif(proto=="echo"):
                    data = data.replace('Echo',"")
                    data = f"server: {data}"
                    sock.send(data.encode())

                elif(proto=="time"):
                    server_time = datetime.datetime.now()
                    msg = f"server: {str(server_time)}"
                    sock.send(msg.encode())

                elif(proto=="HMM"):
                    count=0
                    for i in all_sockets:
                        if(i!=conn_sock and i!=sock):
                            count+=1
                    data = f"server: there are {count} members connected right now besides you"
                    sock.send(data.encode())

                elif(proto=="DM"):
                    name_to_send=""
                    id_to_send = ""
                    msg_to_send = ""
                    eror_count=0 #if this reches more than 1, it means the message was written incorrectly
                    try: #getting the id if there is one
                        id_pattern = re.compile(r"id:<(\d+)>")
                        id_to_send = re.findall(pattern=id_pattern,string=data)[0]
                    except:
                        eror_count+=1
                    try: #getting the name if there is one
                        name_pattern = re.compile(r"name:<(.+?)>")
                        name_to_send = re.findall(pattern=name_pattern,string=data)[0]
                    except:
                        eror_count+=1
                    try: #gfetting the msg
                        msg_pattern = re.compile(r"msg:(.+)$")
                        msg_tmp = re.findall(pattern=msg_pattern,string=data)
                        msg_to_send = f"{name_of_sender}:{msg_tmp[0]}"
                    except:
                        msg = "no message was written"
                        sock.send(msg.encode())               
                    if(name_to_send!=""): #looking for all the sockes fitting the name
                        for sock,name,id_num_test in clients_data:
                            if(name==name_to_send and sock in all_sockets):
                                sock.send(msg_to_send.encode())
                    if(id_to_send!=""):#looking for the socke that fits the id
                        for sock,name,id_num_test in clients_data:
                            if(str(id_num_test)==id_to_send and sock in all_sockets):
                                sock.send(msg_to_send.encode())
                    if(eror_count>1):
                        msg = "server: DM message was written incorrectly, please refer to the RFC document"
                        sock.send(msg.encode())

                elif(proto=="CAP"): #updating the admin password
                    pass_pattern = re.compile(r'password:<(.+?)>')
                    try:
                        admin_password = re.findall(pattern=pass_pattern,string = data)[0]
                        sock.send(f"CAP password was set successfuly, new password is:{admin_password}".encode())
                    except:
                        msg = "server: CAP message was written incorrectly, refer to the RFC"
                        sock.send(msg.encode())

                elif (proto=="CN"): #updating the name
                    name_pattern = re.compile(r"name:<(.+?)>")
                    try:
                        new_name = re.findall(string=data,pattern=name_pattern)[0]
                        for i in range(len(clients_data)):
                            if clients_data[i][0]==sock:
                                clients_data[i][1] = new_name
                        msg = f"CN name:<{new_name}>"
                        sock.send(msg.encode())
                    except:
                        sock.send("sever: CN message was written incorrectly, please refer to the RFC document".encode())

                elif (proto=="GAP"): #sending back all the name,id pairs
                    sock.send("GAP starting".encode())
                    len_people = len([p for p in clients_data if p[0] in all_sockets])
                    sock.send((str(len_people)).encode())
                    for sockobj,name,id_num_loop in clients_data:
                        if sockobj in all_sockets:
                            sock.recv(1054)
                            sock.send(f"name: {name}, id: {id_num_loop}".encode())

                elif (proto=="kick"): #kickng the person specified
                    kick_pattern = re.compile(r'id:<(\d+)>')
                    try:
                        id_to_kick = re.findall(string = data, pattern = kick_pattern)[0]
                        was_kicked = False
                        for sockobj,name,id_num_loop in clients_data:
                            if str(id_num_loop)==id_to_kick:
                                if sockobj==sock:
                                    sock.send("you can't kick yourself silly".encode())
                                    was_kicked = True
                                else:
                                    sockobj.close()
                                    del all_sockets[all_sockets.index(sockobj)]
                                    was_kicked = True
                                    sock.send("client kicked".encode())
                        if not was_kicked:
                            sock.send("Id was not found, no client was kicked".encode())
                    except:
                        sock.send("kick command was written inccorectly".encode())
