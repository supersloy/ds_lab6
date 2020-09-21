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

#Client socket
sock = socket.socket()

#Connect to server
print("Connecting to server (domain:port)", server_ip, server_port ,sep = "")
sock.connect((server_ip, server_port))
print("Client is connected.")

#Send info about request
sock.send(f"recv,,,{file_name}".encode())

#Recieve file size from server
file_size = int(sock.recv(buffer_size).decode())

#Send the file and track the sending rate
progress = tqdm(range(ceil(file_size/buffer_size)), f"Sending {file_name}", unit="B", unit_scale=True)
with open(file_name, "wb") as client_file:
    for i in progress:
        bytes_read = sock.recv(buffer_size)
        if not bytes_read:
            break
        client_file.write(bytes_read)

sock.close()
