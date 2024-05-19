import socket
import threading

# Function to create and bind a socket
def create_bind():
    try:
        global socket
        socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a TCP socket
        ADDRESS = (MY_IP, PORT)
        socket.bind(ADDRESS)  # Bind the socket to the specified IP address and port
    except OSError as os_err:
        print("OS error occurred:", os_err)
    except socket.error as soc_err:
        print("Socket error occurred:", soc_err)

# Function to write messages to a log file
def write(out):
    print(out)
    try:
        file = open("seedlog.txt", "a")  # Open the log file in append mode
        file.write(out + "\n")  # Write the message to the log file
    except:
        print("Error writing")
    finally:
        file.close()  # Close the log file

# Function to handle peer connections
def peer_conn(conn, addr):
    while True:
        try:
            message = conn.recv(1024).decode('utf-8')  # Receive data from the peer
            if message:
                msg = message.split(":")
                if message[0:9] == "Dead Node":
                    write(message)  # Log the message
                    dead_peer = str(msg[1]) + ":" + str(msg[2])
                    if dead_peer in peers:
                        peers.remove(dead_peer)  # Remove the dead peer from the list of peers
                else:
                    print(addr, msg)
                    peers.append(str(addr[0])+":"+str(msg[1]))  # Add the peer to the list of peers
                    out = "Received Connection -- "+str(addr[0])+":"+str(msg[1])
                    write(out)  # Log the message
                    PeerList = ",".join(peers)
                    conn.send(PeerList.encode('utf-8'))  # Send the list of peers back to the peer
        except:
            break
    conn.close()  # Close the connection

# Function to start listening for connections
def begin():
    socket.listen(5)  # Start listening for incoming connections with a backlog of 5
    port_number = socket.getsockname()[1]  # Get the port number the socket is listening on
    print("Seed is listening at port", port_number)
    while True:
        ADDRESS = socket.accept()  # Accept incoming connection
        socket.setblocking(1)  # Set the socket to blocking mode
        thread = threading.Thread(target=peer_conn, args=ADDRESS)  # Create a new thread to handle the connection
        thread.start()  # Start the thread

MY_IP = "127.0.0.1"  # IP address of the server
PORT = int(input("Enter port number for seed: "))  # Port number for the server
peers = []  # List to store information about connected peers

create_bind()  # Create and bind the socket
begin()  # Start listening for connections