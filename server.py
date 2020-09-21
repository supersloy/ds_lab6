import socket
import os
import sys
import tqdm
from math import ceil
from threading import Thread


clients = []

# Thread to listen one particular client
class ClientListener(Thread):
    def __init__(self, id: str, sock: socket.socket):
        super().__init__(daemon=True)
        self.sock = sock
        self.id = id
        self.buffer_size = 1024
        self.separator = ",,,"
        self.block = False

    # clean up
    def _close(self):
        clients.remove(self.sock)
        self.sock.close()
        print(self.id + ' disconnected')

    def run(self):
        while True:
            if self.block == True:
                self._close()
                break
            self.block = True
            #Get required information for further processing
            request_info = self.sock.recv(self.buffer_size).decode()
            request_info_list = str(request_info).split(self.separator)
            #Check whether client want to send or recieve file
            #Upload file on server
            if request_info_list[0] == "send":
                #Get the data about file
                file_name, file_size = request_info_list[1:3]
                file_name = os.path.basename(file_name)
                file_size = int(file_size)
                #Check whether name of the file should be changed
                nameChanged = False
                #Change file name if file with same name exists
                while(os.path.isfile(file_name)):
                    nameChanged = True    
                    name, ext = file_name.split(".")
                    if "_copy_" in name:
                        init_name , copy_ind = name.split("_copy_")
                        copy_ind = int(copy_ind)+1
                        name = init_name+"_copy_"+str(copy_ind)
                    else:
                        name = name + "_copy_1"
                    file_name = name + "." + ext
                #Print info in server console
                print("Client with id:",self.id," sends a file with the name " +file_name)
                if nameChanged:
                    print("File name is adjusted becouse there are already file(s) with same initial name.")
                    self.sock.sendall(file_name.encode())
                else:
                    self.sock.sendall("NO_CHANGE_NAME".encode())

                #Download file
                with open(file_name, "wb") as server_file:
                    #Client end connection when file is downloaded from server
                    while True:
                        bytes_read = self.sock.recv(self.buffer_size)
                        if not bytes_read:
                            break
                        server_file.write(bytes_read)
                #Print info about end of transfering file in server console
                print("Transfer of file from client with id:",self.id,"is complete.")
            #Send file from server
            elif request_info_list[0] == "recv":
                #Get the data about file
                file_name = request_info_list[1]
                file_name = os.path.basename(file_name)
                try:
                    file_size = os.path.getsize(file_name)
                    #Send size of the requested file
                    self.sock.send(f"{file_size}".encode())
                    #Print info in server console
                    print("Client with id:",self.id,"start download a file with the name " +file_name)
                    #Send file
                    with open(file_name, "rb") as client_file:
                        for i in range(ceil(file_size/self.buffer_size)):
                            bytes_read = client_file.read(self.buffer_size)
                            if not bytes_read:
                                break
                            self.sock.sendall(bytes_read)
                    print(f"Client with id: {self.id} downloaded the file: {file_name}")
                except Exception as e:
                    print("Client with id:",self.id,"tryed to download file with name: ", file_name)
                    print("but there is no such file.")

def main():
    #Create server socket
    next_id = 1
    server_port = int(sys.argv[1])
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', server_port))
    sock.listen()
    while True:
        con, addr = sock.accept()
        clients.append(con)
        id = str(next_id)
        next_id += 1
        print(str(addr) + ' connected with id:' + id)
        ClientListener(id, con).start()

if __name__ == "__main__":
    main()
