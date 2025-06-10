import socket
import threading
import time

HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
connectedClients = []  # List to keep track of connected clients
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
turns = {}


def round():
    print("New round started")
    i=0
    playerOneMove = ""
    playerTwoMove = ""
    for addr, conn in connectedClients:
        if(i == 0):
            playerOneMove = turns.get(addr)
        elif(i == 1):
            playerTwoMove = turns.get(addr)
        i += 1
        print(f"Player One Move: {playerOneMove}, Player Two Move: {playerTwoMove}")
    if(playerOneMove == "shoot" and playerTwoMove == "reload"):
        print("Player One wins")
        return "1"
    elif(playerOneMove == "reload" and playerTwoMove == "shoot"):
        print("Player Two wins")
        return "2"
    else:
        print("It's a tie or invalid moves")
        return "again"

    # Reset turns for the next round
def send_msg(conn, msg):
    message = msg.encode(FORMAT)
    msg_length = str(len(message)).encode(FORMAT)
    msg_length += b' ' * (HEADER - len(msg_length))
    conn.send(msg_length)
    conn.send(message)
first = True
def handle_client(conn, addr):
    connected = True
    global first
    while connected:
        if(len(connectedClients) == 2 and first):
                for addr, conn in connectedClients:
                        send_msg(conn, "round")
                first = False
        
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
              
            print(f"[{addr}] says: {msg}")
            if msg == DISCONNECT_MESSAGE:
                print(f"[{addr}] Disconnected")
                connected = False
            
            
            if(msg == "shoot"):
                turns[addr] = "shoot"
            elif(msg == "block"):
                turns[addr] = "block"
            elif(msg == "reload"):
                turns[addr] = "reload"
            if len(turns) == 2 and all(move is not None for move in turns.values()):

                result = round()
                if(result) == "1":
                    
                        send_message_to_other(connectedClients[0][0][0])
                        connected = False
                elif(result) == "2":
                        send_message_to_other(connectedClients[1][0][0])
                        connected = False
                else:
                        for addr in turns.keys():
                            turns[addr] = None
                        time.sleep(2)
                        send_message_to_other("round")
                
                        

            
    conn.close()
    connectedClients.remove((addr, conn))
            
def send_message_to_other(msg):
    for addr, conn in connectedClients:

            print(f"Sending message to {addr}: {msg}")
            send_msg(conn,msg )
        # Here you would implement the logic to send the message to all connected clients
        # For example, you could store client connections in a list and iterate through it

def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        print(f"[NEW CONNECTION] {addr} connected.")
        connectedClients.append((addr, conn))
        turns[addr] = None
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")   
print("server is starting...")
start()