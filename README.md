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

1. Clone this repository: git clone https://github.com/your-repo/network-speed-test.git

2. cd UDP-TCP-speed-test

3. Ensure you have Python 3 installed.
   
4. No additional dependencies are required.
   

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

Server started, listening on IP address 192.168.68.55

UDP server started, listening on port 11111

Server started, listening on TCP port 22222

Accepted connection from ('Client IP', 52016)

Received request from ('Client IP', 54700) for file size: 5242880

Received valid request for file size: 5242880 bytes

Accepted connection from ('Client IP', 52017)

Received request from ('Client IP', 54701) for file size: 5242880

Received valid request for file size: 5242880 bytes

Finished to Sent 5242880 bytes to ('Client IP', 54700) over UDP

Finished to Sent 5242880 bytes to ('Client IP', 54701) over UDP


Finished to Sent 5242880 bytes to ('Client IP', 52017) over TCP

Finished to Sent 5242880 bytes to ('Client IP', 52016) over TCP


Client Output -

Waiting for broadcast.......................................................


Broadcast received.

Received offer from (Server IP) on ports UDP: 11111, TCP: 22222

TCP thread #1 is Connecting to server...

TCP thread #2 is Connecting to server...

Sent TCP #1 request for file size: 5242880 bytes to (Server IP:22222).

Sent UDP #1 request for file size: 5242880 bytes to (Server IP:11111).

Sent TCP #2 request for file size: 5242880 bytes to (Server IP:22222).

Sent UDP #2 request for file size: 5242880 bytes to (Server IP:11111).

UDP transfer #1 finished, total time: 1.12 seconds, total speed: 917879.60 bits/second

Percentage of packets received successfully: 2.45% 

UDP transfer #2 finished, total time: 1.19 seconds, total speed: 764046.73 bits/second

Percentage of packets received successfully: 2.16% 

TCP transfer #2 finished, total time: 5.16 seconds, total speed: 8125786.72 bits/second

TCP transfer #1 finished, total time: 5.21 seconds, total speed: 8043278.36 bits/second

All transfers complete, listening to offer requests

Troubleshooting:

Ensure the server and client are on the same network.

Check firewall settings to allow UDP and TCP communication.

Run the client and server with administrator privileges if necessary.

