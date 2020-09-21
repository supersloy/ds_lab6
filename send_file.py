import socket
from tqdm import tqdm
import os
import sys
from math import ceil

buffer_size = 1024

#Get info from console command
file_name = str(sys.argv[1])
server_ip = str(sys.argv[2])
server_port = int(sys.argv[3])
#Find size of the file
file_size = os.path.getsize(file_name)

#Client socket
sock = socket.socket()

#Connect to server
print("Connecting to server (domain:port)", server_ip, server_port ,sep = "")
sock.connect((server_ip, server_port))
print("Client is connected.")

#Send info about request
sock.send(f"send,,,{file_name},,,{file_size}".encode())

#Check new name of the file if there are file with same name on the server
new_file_name = sock.recv(buffer_size).decode()
if new_file_name != "NO_CHANGE_NAME":
	print("ALERT: File name will be changed on:",new_file_name,"on the server")

#Send the file and track the sending rate
progress = tqdm(range(ceil(file_size/buffer_size)), f"Sending {file_name}", unit="B", unit_scale=True)
with open(file_name, "rb") as client_file:
    for i in progress:
        bytes_read = client_file.read(buffer_size)
        if not bytes_read:
            break
        sock.sendall(bytes_read)

sock.close()
