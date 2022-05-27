This app was written by Omer Cohen

This app runs on python and requires several packages in order to run the client and server. - 
 - tkinter
 - PIL/pillow
 - socket
 - _thread
 - select
 - sys
 - datetime
 -ipaddress
 - cmd_project (a module i made which is included in the folder)

The "client_tkinter.py" is the client and "server.py" is the server, other required file are "chat_room.png", "chat.png" and "cmd_project.py"

This app is a multi users chat room that supports a variety of commands as specified in the RFC document.
Sadly for this app to work you will need to have the server and all the clients in the same LAN network.

This app does not hard code the port/ip of the server into the client but use a more elgant however expansive way of 
"announcing" itself to all the people in the LAN once every 2 seconds. Because of this fact sometimes it may take a second or 2 to log in.
Also it may cause some network issues altough i haven't exprienced any.
It may also slow the computer down a bit if it uses many application at the same time considering this procces costs from the computer.

Once the server starts running, you can run the clients and have a nice and plesent chatting experience.
Enjoy!
