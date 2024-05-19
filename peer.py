import socket
import threading
import time
import hashlib 
import random
from queue import Queue   

# class to store peer information
class Peer: 
    i = 0
    address = ""
    def __init__(self, addr): 
        self.address = addr 

# Function to create and bind a socket
def create_bind():
    try:
        global sock
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a TCP socket
        ADDRESS = (MY_IP, PORT)
        sock.bind(ADDRESS) # Bind the socket to the specified IP address and port
    except:
        print("Erro Detected in create-bind")

# Function to write messages to a log file
def write(out, port):
    print(out)
    try:
        file = open(f"peerlog_{port}.txt", "a")  # Open the log file in append mode
        file.write(out + "\n")  # Write the message to the log file
    except:
        print("Error writing")
    finally:
        file.close()  # Close the log file

# Function to start listening for connections
def begin():
    sock.listen(5)  # Start listening for incoming connections with a backlog of 5
    port_number = sock.getsockname()[1] # Get the port number the socket is listening on
    print("Peer is listening at port", port_number)
    while True:
        ADDRESS = sock.accept()  # Accept incoming connection
        sock.setblocking(1)   # Set the socket to blocking mode
        thread = threading.Thread(target=handlePeer, args=ADDRESS)   # Create a new thread to handle the connection
        thread.start()  # Start the thread
        
# Function to handle peer connections
def handlePeer(conn, addr):
    while True:
        try:
            message = conn.recv(1024).decode('utf-8')  # Receive data from the peer
            
            # If no message received, continue listening
            if message is None:
                continue
            else:
                msg = message.split(":")
                
                # Handling new connection requests
                if "New Connect Request From" in msg[0] and (len(connPeer) < 4):
                    accpt = "New Connect Accepted"
                    conn.send(accpt.encode('utf-8'))
                    connPeer.append( Peer(str(addr[0])+":"+str(msg[2])) )
                
                # Responding to liveness requests
                elif "Liveness Request" in msg[0]:             
                    reply = "Liveness Reply:" + str(msg[1]) + ":" + str(msg[2]) + ":" + str(MY_IP)
                    conn.send(reply.encode('utf-8'))
                
                # Handling gossip messages
                elif "GOSSIP" in msg[3][0:6]:
                    hash = hashlib.sha256(message.encode()).hexdigest()
                    if hash not in messagesLst:
                        messagesLst.append(str(hash))
                        write(message, PORT)
                        for peer in connPeer:
                            try:
                                sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                                peer_addr = peer.address.split(":")
                                sock.connect((str(peer_addr[0]), int(peer_addr[1])))
                                sock.send(message.encode('utf-8'))
                                sock.close()
                            except:
                                continue
        except:
            break
    conn.close()

# Function to establish connections with peer nodes
def peerConnect(peerList, selected_peer_nodes_index):
    # Iterate through the selected peer nodes
    for i in selected_peer_nodes_index:
        try:
            # Attempt to establish a socket connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            listi = peerList[i]
            peer_addr = listi.split(":")
            sock.connect((str(peer_addr[0]), int(peer_addr[1])))
            
            # Add connected peer to the list
            connPeer.append( Peer(peerList[i]) )
            
            # Send connection request message
            message = "New Connect Request From:" + str(MY_IP) + ":" + str(PORT)
            sock.send(message.encode('utf-8'))
            
            # Receive acknowledgment from the peer
            receive = sock.recv(1024).decode('utf-8')
            print(receive)
            
            # Close the socket connection
            sock.close()
        except:
            # Print error message if connection fails
            print("Peer Connection Error")

def combinePeers(peerList):
    global MY_IP
    peerList = peerList.split(",")  # Split the peer list
    MY_IP = peerList.pop().split(":")[0]  # Extract and set the current IP address
    for i in peerList:
        peerFromSeed.add(i)  # Add peers from the list to a set to remove duplicates
    peerList = list(peerFromSeed)  # Convert the set back to a list
    return peerList  # Return the combined list of peers

def seedConnect():
    global peerList
    
    # Iterate through connected seed addresses
    for i in connectedSeedAddr:
        try:
            # Establish socket connection with seed
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            seed_addr = i.split(":")
            sock.connect((str(seed_addr[0]), int(seed_addr[1])))
            
            # Send own address to seed
            MY_ADDRESS = str(MY_IP) + ":" + str(PORT)
            sock.send(MY_ADDRESS.encode('utf-8'))
            
            # Receive and combine peer list from seed
            peerList = combinePeers(sock.recv(10240).decode('utf-8'))
            
            # Write each peer to a file
            for peer in peerList:
                write(peer, PORT)
            
            # Close socket connection
            sock.close()
        except:
            # Print error message if connection fails
            print("Seed Connection Error")
    
    # Connect to a limited number of peers
    if len(peerList) > 0:
        limit = min(random.randint(1, len(peerList)), 4)
        selected_peer_nodes_index = set()
        
        # Randomly select peers
        while len(selected_peer_nodes_index) < limit:
            selected_peer_nodes_index.add(random.randint(0, len(peerList) - 1))
        
        # Connect to selected peers
        peerConnect(peerList, selected_peer_nodes_index)

def peerDead(peer):
    # Compose dead node message
    dead_message = "Dead Node:" + peer + ":" + str(time.time()) + ":" + str(MY_IP)
    
    # Write dead node message to file
    write(dead_message, PORT)
    
    # Notify connected seeds about dead node
    for seed in connectedSeedAddr:        
        try:
            # Establish socket connection with seed
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            seed_address = seed.split(":")
            sock.connect((str(seed_address[0]), int(seed_address[1])))
            
            # Send dead node message to seed
            sock.send(dead_message.encode('utf-8'))
            
            # Close socket connection
            sock.close()
        except:
            # Print error message if connection fails
            print("Seed Down ", seed)

def handleGossip(i):
    # Construct gossip message
    msg = str(time.time()) + ":" + str(MY_IP) + ":" + str(PORT) + ":" + "GOSSIP" + str(i+1) 
    
    # Add message hash to the list
    messagesLst.append(str(hashlib.sha256(msg.encode()).hexdigest()))
    
    # Send gossip message to connected peers
    for peer in connPeer:
        try:
            # Establish socket connection with peer
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_addr = peer.address.split(":")
            sock.connect((str(peer_addr[0]), int(peer_addr[1])))
            
            # Send gossip message
            sock.send(msg.encode('utf-8'))
            
            # Close socket connection
            sock.close() 
        except:
            # Print error message if connection fails
            print("Peer Down ", peer.address)

def work():
   while True:
       x = queue.get()  # Get a task from the queue
       if x == 1:  # If task is 1, initiate connection and start application
           create_bind()
           begin()
       elif x == 2:  # If task is 2, perform liveness checks
           while True:
               # Send liveness request to peers
               print("Liveness Request:" + str(time.time()) + ":" + str(MY_IP))
               for peer in connPeer:
                   try:                
                       sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                       peer_addr = peer.address.split(":")
                       sock.connect((str(peer_addr[0]), int(peer_addr[1])))
                       msg = "Liveness Request:" + str(time.time()) + ":" + str(MY_IP)
                       sock.send(msg.encode('utf-8'))
                       msg = sock.recv(1024).decode('utf-8')
                       print(msg)
                       sock.close()  
                       peer.i = 0
                   except:
                       # Increase failure counter and handle dead peer
                       peer.i += 1
                       if (peer.i < 3):
                           continue
                       elif(peer.i == 3):
                           peerDead(peer.address)
                           connPeer.remove(peer)
               time.sleep(13)  # Wait before performing next liveness check
       elif x == 3:  # If task is 3, initiate gossiping
           for i in range(10):
               handleGossip(i)
               time.sleep(5)  # Wait before initiating next gossip round
       queue.task_done()  # Mark the task as done

n_thread = 3
job = [1, 2, 3]
queue = Queue()

MY_IP = "127.0.0.1" 
PORT = int(input("Enter port number for peer: "))
seedAddr = set()
peerFromSeed = set()
connPeer = []
messagesLst = []
connectedSeedAddr = []
peerList = []

# Read seed list from configuration file
file = open("config.txt","r")
seedList = file.read()
file.close()

tmp = seedList.split("\n")
for addr in tmp:
    if addr is None:
        continue
    else:
        # Extract IP address and port from each line
        addr = addr.split(":")
        seedAddr.add("127.0.0.1:" + str(addr[1]))

n = len(seedAddr)

seedAddr = list(seedAddr)

lst = set()
# Select random seed nodes to connect to
while len(lst) < n // 2 + 1:
    lst.add(random.randint(0, n - 1))
lst = list(lst)

for i in lst:
    connectedSeedAddr.append(seedAddr[i])

# Connect to selected seed nodes
seedConnect()

# Start multiple threads for concurrent execution
for i in range(n_thread):
    thread = threading.Thread(target=work)
    thread.daemon = True
    thread.start()

# Assign jobs to the queue
for i in job:
    queue.put(i)

# Wait for all jobs to be completed
queue.join()