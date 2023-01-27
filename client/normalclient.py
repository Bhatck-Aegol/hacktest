import socket
from time import time, sleep
import pickle
import pygame
from pygame.locals import *
from threading import Thread

SCREEN_SIZE = (32*16, 32*16)
SCREEN = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("<Insert name here>")#TODO: name the 'game'



class Player():
    def __init__(self, name) -> None:
        self.pos = [0, 0]
        self.name = name
        self.image = pygame.Surface([32, 32])
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect()


def translate_player(player) -> Player:
    new_player = Player(player[1].name)
    return new_player


def handle_keys(server: socket.socket, player: Player, KeysPressed):
    if KeysPressed[K_w]:
        server.sendall(f"move {player.pos[0]} {player.pos[1]-1}".encode('utf-8'))
        player.pos[1]-=2
    if KeysPressed[K_s]:
        server.sendall(f"move {player.pos[0]} {player.pos[1]+1}".encode('utf-8'))
        player.pos[1]+=2
    if KeysPressed[K_a]:
        server.sendall(f"move {player.pos[0]-1} {player.pos[1]}".encode('utf-8'))
        player.pos[0]-=2
    if KeysPressed[K_d]:
        server.sendall(f"move {player.pos[0]+1} {player.pos[1]}".encode('utf-8'))
        player.pos[0]+=2


def handle_server(server: socket.socket):
    global Server_packets
    while True:
        data = server.recv(4096)
        Server_packets.append(data)


def handle_packets():
    global Server_packets
    for packet in Server_packets:
        print(packet)
        packet = pickle.loads(packet)
        if type(packet[0][1]) == type(pickle.loads(b'\x80\x04\x95\x17\x00\x00\x00\x00\x00\x00\x00\x8c\x08__main__\x94\x8c\x06player\x94\x93\x94.')): #TODO: make this thing better
            Players = [my_player]
            for player in packet:
                Players.append(translate_player(player))
        match packet:
            case packet.startswith('move'):
                _, name, x, y = packet.split()
                for player in Players:
                    if player.name == name:
                        player.pos = [x, y]
                        break

            

def DrawBlock(Block, pos):
    bimg = pygame.Surface([32, 32])
    if Block == '**':
        bimg.fill((0, 255, 0))
    if Block == 'SS':
        bimg.fill((128, 128, 128))
    else: 
        bimg.fill((250, 0 ,0))
    SCREEN.blit(bimg, pos)


def draw_players(Players):
    for i in range(len(Players)):
        SCREEN.blit(Players[i].image, Players[i].pos)


def update(s, KeysPressed, World, Players: list = []):
    handle_packets()
    #Draw the world
    for row in range(len(World)):
        for index in range(len(World[row])):
            DrawBlock(World[row][index], [row*33, index*33])
    handle_keys(s, Players[0], KeysPressed)

    draw_players(Players)


HOST = "localhost"
PORT = 8888

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


print("connecting")
s.connect((HOST, PORT))
print("connected")

Server_packets = []
Server_handler = Thread(target=handle_server, args= (s))
Server_handler.start()
Name = "Bhatck"
s.sendall(bytes(Name, 'utf-8')) #Send name
World = pickle.loads(s.recv(4096))
print(World)

my_player = Player(Name)
Players = [my_player] #
Players.append(pickle.loads(s.recv(4096)))

FPS = 60
clock = pygame.time.Clock()

ctime = time()
exiting = False
while not exiting:
    clock.tick(FPS)
    SCREEN.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == QUIT:
            exit()
    KeysPressed = pygame.key.get_pressed()
    if KeysPressed[K_e]:
        exiting = True
        s.sendall(b"exit")
        continue #Exit the loop
    
    IsClicked = pygame.mouse.get_pressed()
    if IsClicked:
        MousePos = pygame.mouse.get_pos()
    update(s, KeysPressed, World, Players)

    if time() - ctime >= 5:
        s.sendall(b"alive")
        ctime = time()
    pygame.display.update()