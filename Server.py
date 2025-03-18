import socket
import threading
import struct
import time

def find_free_port(start_port=20000, max_attempts=100):
    """
    Searches for a free port by attempting to bind from start_port upwards.
    Returns the first available port.
    """
    for port in range(start_port, start_port + max_attempts):
        try:
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.bind(("0.0.0.0", port))
            test_socket.close()
            return port
        except OSError:
            continue
    raise Exception("Could not find a free port.")

def get_local_ip():
    """
    Returns the local IP address of the machine (best guess).
    """
    try:
        temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        temp_socket.connect(("8.8.8.8", 80))
        ip = temp_socket.getsockname()[0]
        temp_socket.close()
        return ip
    except Exception:
        return "127.0.0.1"

# Constants
MAGIC_COOKIE = 0xabcddcba
OFFER_MSG_TYPE = 0x2
REQUEST_MSG_TYPE = 0x3
PAYLOAD_MSG_TYPE = 0x4

# Helper Functions
def create_offer_packet(udp_port, tcp_port):
    """Create an offer packet."""
    return struct.pack('!IBHH', MAGIC_COOKIE, OFFER_MSG_TYPE, udp_port, tcp_port)

def parse_request_packet(packet):
    """Parse an offer packet."""
    try:
        magic, msg_type, file_zise = struct.unpack('!IBQ', packet)
        if magic != MAGIC_COOKIE or msg_type != REQUEST_MSG_TYPE or file_zise > 2**64 -1:
            return None
        return file_zise
    except struct.error:
        return None

# Server Class
class Server:
    def __init__(self, udp_port, tcp_port):
        self.ip = None
        self.udp_port = udp_port
        self.tcp_port = tcp_port
        self.clientUdpPort = 33333
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = True



    def start(self):
        self.ip = get_local_ip()
        print(f"Server started, listening on IP address {self.ip}")
        threading.Thread(target=self._udp_server_and_broadcast, daemon=True).start()
        threading.Thread(target=self._start_tcp_server, daemon=True).start()

    def _udp_server_and_broadcast(self):
        """Handle both UDP broadcast and server requests."""
        self.udp_socket.bind(('0.0.0.0', self.udp_port))  # Bind the socket to the UDP port
        print(f"UDP server started, listening on port {self.udp_port}")
        offer_packet = create_offer_packet(self.udp_port, self.tcp_port)

        while self.running:
            try:
                # Send a broadcast
                self.udp_socket.sendto(offer_packet, ('<broadcast>', self.clientUdpPort))
                last_broadcast_time = time.time()

                self.udp_socket.settimeout(1)  # 1 second timeout for listening
                while True:
                    if time.time() - last_broadcast_time > 1:
                        break
                    # Set a short timeout for listening to allow frequent broadcast checks
                    data, addr = self.udp_socket.recvfrom(13)  # Listen for client requests
                    # if addr[0] == self.ip:
                    #     continue
                    file_size = parse_request_packet(data)
                    if file_size:
                        print(f"Received request from {addr} for file size: {file_size}")
                        threading.Thread(
                            target=self._handle_udp_request,
                            args=(self.udp_socket, file_size, addr)
                        ).start()
                        # Process the incoming request

            except socket.timeout:
                # No client requests received during the timeout period
                continue

        self.udp_socket.close()  # Ensure the socket is properly closed when the server stops

    def _handle_udp_request(self, udp_socket, file_size, addr):
        """Handle a single UDP client request."""
        try:
            # Send the requested file size back as a response in segments
            segment_size = 1024 - 21  # Size of each payload chunk - IBQQ --> 21B
            if file_size:
                total_segments = (file_size + segment_size - 1) // segment_size

                for segment_number in range(total_segments):
                    payload_size = min(segment_size, file_size - (segment_number * segment_size))
                    payload_data = b'a' * payload_size

                    payload_packet = struct.pack(
                        '!IBQQ', MAGIC_COOKIE, PAYLOAD_MSG_TYPE, total_segments, segment_number
                    ) + payload_data

                    udp_socket.sendto(payload_packet, addr)
                print(f"Sent {file_size} bytes to {addr} over UDP")
        except Exception as e:
            print(f"Error handling UDP request from {addr}: {e}")

    def _start_tcp_server(self):
        """Start the TCP server to handle client requests."""
        self.tcp_socket.bind(('0.0.0.0', self.tcp_port))
        self.tcp_socket.listen()
        print(f"Server started, listening on TCP port {self.tcp_port}")

        while self.running:
            conn, addr = self.tcp_socket.accept()
            print(f"Accepted connection from {addr}")
            threading.Thread(target=self._handle_tcp_client, args=(conn,), daemon=True).start()

    def _handle_tcp_client(self, conn):
        """Handle a single TCP client."""
        try:
            # Receive the request packet
            request_data = conn.recv(13)
            # The request message is 13 bytes long
            # Parse the request packet using the provided function
            file_size = parse_request_packet(request_data)

            if not file_size:
                raise ValueError
            print(f"Received valid request for file size: {file_size} bytes")

            # Chunk size for sending data
            chunk_size = 1024
            bytes_sent = 0

            while bytes_sent < file_size:
                remaining = file_size - bytes_sent
                chunk = min(chunk_size, remaining)
                conn.sendall(b'a' * chunk)
                bytes_sent += chunk

            print(f"Sent {file_size} bytes to client in chunks.")
        except ValueError as ve:
            print(f"Request validation error: {ve}")
        except Exception as e:
            print(f"Error handling TCP client: {e}")
        finally:
            conn.close()

    def stop(self):
        self.running = False
        self.udp_socket.close()
        self.tcp_socket.close()

# Main Function for Server
def main():
    udp_port = 11111
    tcp_port = 22222

    server = Server(udp_port, tcp_port)
    try:
        server.start()
        # print("Server running. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down server...")
        server.stop()

if __name__ == "__main__":
    main()
