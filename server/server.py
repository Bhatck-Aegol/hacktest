import socket
import time
import threading
import pickle

class player():
    def __init__(self, name, ID, conn, addr) -> None:
        self.pos = [0, 0]
        self.name = name
        self.ID = ID
        self.conn = conn
        self.addr = addr

        self.timeout = 10

def dist(pos1, pos2) -> int:
    return max(abs(pos1[0]-pos2[0]), abs(pos1[1]-pos2[1]))

def distribute(client_list: list, packet: bytes, own_id):
    for client in client_list:
        if client[1].ID == own_id: continue
        client[1].conn.send(packet)

#GAME PART OF THE CODE#
def handle_packets(packet: str, player_obj: player):
    if packet == b"exit":
        return "EXIT"
    if packet.startswith(b"alive"):
        player_obj.timeout = 10
    if packet.startswith(b"move"):
        _, x, y = packet.split()
        if dist(player_obj.pos, [int(x), int(y)]) < 5:
            distribute(client_list, f"movement {player_obj.name} {x} {y}", player_obj.ID)
            print(f"player moved to {x} {y}")
            return
        #If the player is moving too fast
        player_obj.addr.send(b"invalid move")
    
    return
    

def receive_sockets(server):
    pass






'''
with open("config.txt", "r") as f:
    SIZE = int(f.readline().rsplit(" ")[1]) # read the first line of the file then get the second word , which is the 'SIZE' variable
'''
SIZE = 10
WORLD = [["**" for _ in range(SIZE)] for _ in range(SIZE)]










#GAME PART OF THE CODE#

#SETUP
client_list = []
ids = 0 #Figurative ids
TotalIds = 0 #Number of ids
#SETUP


def handle_client(conn, addr, ID):
    global TotalIds
    print(f"Connected to {addr}: ", end="")
    name = conn.recv(1024)
    print(name)
    C = player(name, ID, conn, addr)
    client_list[TotalIds-1].append(C)#Might bug out if 2 players join at the same time(~10ms?)

    conn.send(pickle.dumps(WORLD))
    conn.send(client_list[TotalIds])

    PastTime = time.time()
    while True:
        packets = conn.recv(1024)
        result = handle_packets(packets, C)

        if time.time() - PastTime >= 1:
            C.timeout -= 1
            PastTime = time.time()
        if C.timeout <= 0:
            conn.send(b"timeout")
            break
        if result == "EXIT":
            break
    conn.close() #timeout or client has exited
    client_list.pop(TotalIds)
    TotalIds -= 1
    distribute(client_list, pickle.dumps("CLIENTEXIT"))
    distribute(client_list, pickle.dumps(client_list), 'Never used')
    print("client exited")


#ip = 192.168.1.156
HOST = "localhost"
PORT = 8888

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind((HOST, PORT))

while True:
    s.listen()
    print("listening")
    conn, addr = s.accept()
    thread = threading.Thread(target=handle_client, args=(conn, addr, ids))
    client_list.append([thread]) #A player object will be added later into the list appended to the client list in the new thread
    thread.start()
    ids+=1
    TotalIds+=1