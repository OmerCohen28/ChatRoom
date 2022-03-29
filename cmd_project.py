import subprocess
import sys
from texttable import *
def run_command(cmd):
    return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            stdin=subprocess.PIPE).communicate()

#returns a tupple where [0] = name, [1] = state, [2] = physical adress, [3] = DHCP enabled
#expects n to be the index in the data list of the name of the NIC
def Get_Data_On_NIC(data,n):
    result = []
    name = data[n][0]
    result.append(name[:len(name)-1]) #adding the name
    try:
        info = data[n+1]
    except:
        print("an attemp was made to analyze a non existing NIC")
        sys.exit(1)

    #finding info about physical adress
    for i in info:
        try:
            Physical_Index = i.index("Physical Address")+16
            Physcal = i
            break
        except:
            continue
    Physcal_adress=""
    Count_Indcies=0
    for i in range(Physical_Index,len(Physcal)):
        if(Physcal[i]!='.' and Physcal[i]!=":" and Physcal[i]!=" "):
            if(Count_Indcies<=17):
                Physcal_adress+=Physcal[i]
                Count_Indcies+=1

    #finding info about DHCO
    for i in info:
        try:
            DHCP_Index = i.index("DHCP Enabled")
            DHCP_Enabled = i
            break
        except:
            continue
    IsEnabled = False
    try:
        tmp = DHCP_Enabled.index("Yes")   
        IsEnabled = True 
    except:
        pass
    Result_DHCP = ""
    if(DHCP_Enabled):
        Result_DHCP = "Yes"
    else:
        Result_DHCP = "No"

    #finding info about the state of the NIC
    IsPrimary = True #if this variable stays true it means there is more than one NIC which means there is Media State field that needs to be cheked
    for i in info:
        try:
            tmp = i.index("Media")
            state = i
            IsPrimary = False #means there is no more than one NIC which means string manipulation is not needed
            break
        except:
            continue
    Result_Connection = "connected"
    if(not IsPrimary):
          IsConnected = True
          try:
              tmp = state.index("disconnected")   
              IsConnected = False 
          except:
              pass
          Result_Connection = ""
          if(IsConnected):
                Result_Connection = "connected"
          else:
               Result_Connection = "disconnected"
    result.append(Result_Connection)
    result.append(Physcal_adress)
    result.append(Result_DHCP)
    return result,IsPrimary
    

def Get_IP_Info(data,n):
    info = data[n]
    result = []
    
    #getting ip info
    for i in info:
        try:
            IP_Index = i.index("IPv4 Address")+13
            IP = i
            break
        except:
            continue
    IP_adress=""
    Start_Copy = 0
    for i in range(IP_Index,len(IP)):
        if(IP[i]!='.' and IP[i]!=":" and IP[i]!=" "):
            Start_Copy=i
            break
    for i in range(Start_Copy,len(IP)):
        try:
            int(IP[i])
            IP_adress+=str(IP[i])
        except:
            if(IP[i]=="."):
                IP_adress+="."
    
    #getting GateWay info
    GateWay_Index=0
    for i in range(len(info)):
        try:
            GateWay_Index = info[i].index("Default Gateway")+16
            GateWay = info[i]
            index = i
            break
        except:
            continue
    GateWay_adress=""
    Start_Copy = 0
    for i in range(GateWay_Index,len(GateWay)):
        if(GateWay[i]!='.' and GateWay[i]!=":" and GateWay[i]!=" "):
            Start_Copy=i
            break
    ipv6 = False
    for i in range(Start_Copy,len(GateWay)):
        if(GateWay[i]==":"):
            ipv6 = True
    if(ipv6):
        GateWay = info[index+1]
    for i in range(GateWay_Index,len(GateWay)):
      if(GateWay[i]!='.' and GateWay[i]!=":" and GateWay[i]!=" "):
          Start_Copy=i
          break
    for i in range(Start_Copy,len(GateWay)):
        try:
            int(GateWay[i])
            GateWay_adress+=str(GateWay[i])
        except:
            if(GateWay[i]=="."):
                GateWay_adress+="."

    #getting host name
    Host_List = data[1]
    for i in Host_List:
        try:
            Host_Index = i.index("Host Name")+10
            Host = i
            break
        except:
            continue
    Host_name=""
    for i in range(Host_Index,len(Host)):
        if(Host[i]!='.' and Host[i]!=":" and Host[i]!=" "):
                Host_name+=Host[i]


    #getting subnet mask
    for i in info:
        try:
            MASK_Index = i.index("Subnet Mask")+13
            MASK = i
            break
        except:
            continue
    MASK_adress=""
    Start_Copy = 0
    for i in range(MASK_Index,len(MASK)):
        if(MASK[i]!='.' and MASK[i]!=":" and MASK[i]!=" "):
            Start_Copy=i
            break
    for i in range(Start_Copy,len(MASK)):
        try:
            int(MASK[i])
            MASK_adress+=str(MASK[i])
        except:
            if(MASK[i]=="."):
                MASK_adress+="."

    result.append(IP_adress)
    result.append(GateWay_adress)
    result.append(Host_name)  
    result.append(MASK_adress)  
    return result  

def fetch_data():
    ipconfig = run_command("ipconfig/all")[0].decode("utf-8",errors = "ignore")
    data = [i.split("\r\n") for i in ipconfig.split("\r\n\r\n")]
    header = ["Name","state","Physical adress","DHCP enabled"]
    Nic_Data=[]
    Nic_Data.append(header)
    Primary_Index=0
    for i in range(2,len(data),2):
        Nic_Data.append(Get_Data_On_NIC(data,i)[0])
        if(Get_Data_On_NIC(data,i)[1]):
            Primary_Index = i+1


    IP_Table = []
    IP_Data = []
    IP_Header = ["IPv4 Address","Gateway","Host Name","Subnet Mask"]
    IP_Data = Get_IP_Info(data,Primary_Index)
    for i in range(len(IP_Data)):
        IP_Table.append([IP_Header[i],IP_Data[i]])
        
    return IP_Data

def main():
    ipconfig = run_command("ipconfig/all")[0].decode("utf-8",errors = "ignore")
    data = [i.split("\r\n") for i in ipconfig.split("\r\n\r\n")]
    header = ["Name","state","Physical adress","DHCP enabled"]
    Nic_Data=[]
    Nic_Data.append(header)
    Primary_Index=0
    for i in range(2,len(data),2):
        Nic_Data.append(Get_Data_On_NIC(data,i)[0])
        if(Get_Data_On_NIC(data,i)[1]):
            Primary_Index = i+1

    print("Computer Information:NIC")
    table_NIC = Texttable()
    table_NIC.set_cols_align(["c", "c", "c","c"])
    table_NIC.set_cols_valign(["m", "m", "m","m"])
    table_NIC.add_rows(Nic_Data)
    print(table_NIC.draw())


    IP_Table = []
    IP_Data = []
    IP_Header = ["IPv4 Address","Gateway","Host Name","Subnet Mask"]
    IP_Data = Get_IP_Info(data,Primary_Index)
    for i in range(len(IP_Data)):
        IP_Table.append([IP_Header[i],IP_Data[i]])

    print("Computer Information:IP")
    table_IP = Texttable()
    table_IP.set_cols_align(["c", "c"])
    table_IP.set_cols_valign(["m", "m"])
    table_IP.add_rows(IP_Table,header=False)
    print(table_IP.draw())


if __name__ == "__main__":
    main()