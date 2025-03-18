# UDP-TCP-speed-test
Network Speed Test Client-Server
This repository contains a client-server implementation for testing ---network speed over UDP and TCP. The server listens for client requests and transmits data over both protocols to measure throughput and latency.

Features

Server:
- Broadcasts UDP offers to clients.
- Handles TCP and UDP connections for data transmission.
- Sends requested file sizes to clients.

Client:
- Listens for server broadcast offers.
- Establishes TCP and UDP connections with the server.
- Measures transmission speed and packet loss.

Installation
1.1 Clone this repository: git clone https://github.com/your-repo/network-speed-test.git
1.2 cd UDP-TCP-speed-test
2. Ensure you have Python 3 installed.
3. No additional dependencies are required.

Usage
Running the Server:
Start the server on a machine: python server.py
*The server will broadcast its availability and wait for client connections.

Running the Client:
Start the client on another machine: python client.py
*The client will listen for offers, connect to the server, and perform the speed test.

Configuration:
The server and client can be configured by modifying the following variables in their respective scripts:

Server:
udp_port = 11111
tcp_port = 22222

Client:
udp_port = 33333
file_size = 5 * 1024 * 1024 (5 MB default test size)
tcp_amount = 2 (number of TCP connections)
udp_amount = 2 (number of UDP connections)

How It Works:
1. The server periodically broadcasts UDP packets containing its availability.
2. The client listens for these packets and initiates a connection.
3. The client sends a request to the server, specifying the file size for the test.
4. The server sends the requested data back to the client over TCP and UDP.
5. The client records the transfer speed, packet loss, and other statistics.

Output Example
Server Output -
Server started, listening on IP address 192.168.1.10
UDP server started, listening on port 11111
Server started, listening on TCP port 22222
Received request from ('192.168.1.20', 33333) for file size: 5242880
Sent 5242880 bytes to ('192.168.1.20', 33333) over UDP
Accepted connection from ('192.168.1.20', 54321)
Sent 5242880 bytes to client in chunks.

Client Output -
Client started, listening for offer requests 33333...
Waiting for broadcast...
Received offer from 192.168.1.10 on ports UDP: 11111, TCP: 22222
Sent TCP #1 request for file size: 5242880 bytes to 192.168.1.10:22222.
TCP transfer #1 finished, total time: 1.24 seconds, total speed: 33.77 Mbps
Sent UDP #1 request for file size: 5242880 bytes to 192.168.1.10:11111.
UDP transfer #1 finished, total time: 1.55 seconds, total speed: 26.98 Mbps

Troubleshooting
Ensure the server and client are on the same network.
Check firewall settings to allow UDP and TCP communication.
Run the client and server with administrator privileges if necessary.
