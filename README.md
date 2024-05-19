# P2P Gossips Protocol

- **Subject** - Computer Networks
- **Semester** - Spring 2024
- **Team Members**
  - B21CS037 - Kashvi Jain
  - B21CS015 - Arun Raghav S

## Code Description

- Config file:
    - `IP` and `Port` of seed nodes are hard-coded

- Seed:
    - Initializes functions to create and bind sockets `create_bind()`, write logs `write()`, and handle incoming connections from peers `begin()`.
    - Implements a thread function `peer_conn()` to handle peer connections, processing various types of messages received.
    - Upon receiving a connection request from a peer, it responds by sending its peer list.
    - Monitors for "dead" messages from peers and removes them from the peer list accordingly.
    - Listens for incoming connections from peers and spawns separate threads to handle each connection.
    - Provides functionality to listen for and accept incoming connections `begin()`, manage peer lists `peer_conn()`, and handle dead peers `peer_conn()`.
    - Utilizes threading `threading.Thread` to handle multiple peer connections concurrently.
    - Reads the port number for the seed node from user input and initializes necessary variables `PORT`.

- Reporting the node as Dead:
    - When 3 consecutive liveness requests do not receive a reply, the peer sends a message of the following format to all the seeds it is connected to: `Dead Node`:`DeadNode.IP`:`self.timestamp`:`self.IP`

- Peer:
    - MessagesLst (ML) being printed in peerlog.
    - Connects to `least_integer(n/2)+1` seed nodes. 
    - Initializes a Peer class `Peer` to manage peer addresses.
    - Defines functions to create and bind sockets `create_bind()`, write logs `write()`, and handle incoming connections `begin()`.
    - Initiates a listening loop `begin()` to accept incoming connections from peers.
    - Implements a handler `handlePeer()` for each peer connection, processing various types of messages received.
    - Provides functionality to connect to other peers `peerConnect()`, manage peer lists, and handle dead peers `peerDead()`.
    - Implements gossiping among peers `handleGossip()` by exchanging messages and ensuring message uniqueness.
    - Manages liveness testing `work()` to monitor peer availability and take action upon failures.
    - Utilizes a worker function `work()` to manage different tasks such as socket creation, liveness checking, and gossiping concurrently.
    - Utilizes threading `threading.Thread` and a queue `Queue` to manage concurrent execution of tasks.
    - Reads seed addresses from a configuration file and connects to a subset of them `seedConnect()`.

- Gossip message:
    - Peer generates msg of the format: `self.timestamp`:`self.IP`:`self.Msg#`

- Liveliness message:
    - If 3 consecutive liveness messages are not replied to, the node will notify the seed nodes that it is connected to, that this particular IP Address is not responding

- Request Message Format:
    - `Liveness Request`:`self.timestamp`:`self.IP`

- Reply Message Format:
    - `Liveness Reply`:`sender.timestamp`:`sender.IP`:`self.IP`

- Log file:
    - SeedLog file store the connection requests from new peers as well as the output from dead node.
    - Each peer has its own log file where it writes the list of peers it got from seed nodes. Gossip messages are also logged with timestamp.
    
## Execution Steps:

- Clone this repository
- Edit config.txt to add localhost IP address and any port number. Sample has been provided
- Run `python seed.py` and enter the port number used in config file. Repeat the same for all ports
- Run `python peer.py` and enter any port number.
- If another instance of peer is started, gossips would start.
- All of this is logged in the output file.
