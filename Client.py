import socket
import struct
import threading
import time

# Constants
MAGIC_COOKIE = 0xabcddcba
OFFER_MSG_TYPE = 0x2
REQUEST_MSG_TYPE = 0x3
PAYLOAD_MSG_TYPE = 0x4


# Helper Functions
def parse_offer_packet(packet):
    """Parse an offer packet."""
    try:
        magic, msg_type, udp_port, tcp_port = struct.unpack('!IBHH', packet)
        if magic != MAGIC_COOKIE or msg_type != OFFER_MSG_TYPE:
            raise ValueError("Invalid offer packet")
        return udp_port, tcp_port
    except struct.error:
        raise ValueError("Malformed offer packet")


def parse_payload_packet(packet):
    """Parse a payload packet and validate payload size."""
    try:
        header_size = struct.calcsize('!IBQQ')
        magic, msg_type, total_segments, current_segment = struct.unpack('!IBQQ', packet[:header_size])
        if magic != MAGIC_COOKIE or msg_type != PAYLOAD_MSG_TYPE:
            raise ValueError("Invalid payload packet")
        payload = packet[header_size:]
        payload_size = len(payload)  # Measure payload size

        return total_segments, current_segment, payload, payload_size
    except struct.error:
        raise ValueError("Malformed payload packet")


# Client Class
class Client:
    def __init__(self, udp_port):
        self.udp_port = udp_port
        self.running = True
        self.lookingforserver = True
        self.file_size = 1024*1024*5
        self.tcp_amount = 2
        self.udp_amount = 2

    def start(self):
        while self.running:
            self._listen_for_offers()

    @staticmethod
    def clear_udp_buffer(udp_socket):
        """Clear the UDP socket buffer."""
        udp_socket.setblocking(False)  # Set socket to non-blocking mode
        try:
            while True:
                udp_socket.recvfrom(1024)  # Discard data
        except BlockingIOError:
            # No more data in the buffer
            pass
        finally:
            udp_socket.setblocking(True)  # Reset socket to blocking mode

    def _listen_for_offers(self):
        """Listen for server offer messages."""
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow address reuse
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # Enable broadcast reception
        udp_socket.bind(('', self.udp_port))
        print(f"Client started, listening for offer requests {self.udp_port}...")

        while self.lookingforserver:
            try:
                self.clear_udp_buffer(udp_socket)
                print("Waiting for broadcast.................................................................")
                data, addr = udp_socket.recvfrom(1024)
                print("Broadcast received.")
                server_ip = addr[0]
                udp_port, tcp_port = parse_offer_packet(data)
                print(f"Received offer from {server_ip} on ports UDP: {udp_port}, TCP: {tcp_port}")
                self.speed_test(server_ip, udp_port, tcp_port)
            except Exception as e:
                print(f"Error receiving offer: {e}")

    def speed_test(self, server_ip, udp_port, tcp_port):
        tcp_threads = []
        udp_threads = []

        # Create threads for each TCP connection
        for i in range(self.tcp_amount):
            tcp_thread = threading.Thread(
                target=self._handle_server,
                args=(server_ip, tcp_port, i+1)
            )
            tcp_threads.append(tcp_thread)
            tcp_thread.start()

        # Create threads for each UDP connection
        for i in range(self.udp_amount):
            udp_thread = threading.Thread(
                target=self._handle_udp_connection,
                args=(server_ip, udp_port, i+1)
            )
            udp_threads.append(udp_thread)
            udp_thread.start()

        # Wait for all TCP threads to complete
        for tcp_thread in tcp_threads:
            tcp_thread.join()

        # Wait for all UDP threads to complete
        for udp_thread in udp_threads:
            udp_thread.join()

        print("All transfers complete, listening to offer requests\n\n")

    def _handle_udp_connection(self, server_ip, udp_port, id):
        """Handle UDP connection to the server."""
        try:
            udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_socket.settimeout(1)  # Timeout for detecting end of transfer
            request_packet = struct.pack('!IBQ', MAGIC_COOKIE, REQUEST_MSG_TYPE, self.file_size)

            # Create and send request packet
            udp_socket.sendto(request_packet, (server_ip, udp_port))
            print(f"Sent UDP #{id} request for file size: {self.file_size} bytes to {server_ip}:{udp_port}.")

            # Initialize transfer statistics
            start_time = time.time()
            total_segments = None
            received_segments = set()
            total_data = 0

            while True:
                try:
                    # Receive a packet from the server
                    data, addr = udp_socket.recvfrom(1024)

                    # Parse the payload packet
                    total_segments, current_segment, payload, payload_size = parse_payload_packet(data)

                    # Update transfer statistics
                    total_data += payload_size
                    if total_segments is None:
                        total_segments = total_segments

                    received_segments.add(current_segment)

                    if total_segments == current_segment + 1:
                        break

                except socket.timeout:
                    # Timeout indicates the end of the transfer
                    start_time += 1
                    break

            end_time = time.time()

            # Calculate transfer statistics
            transfer_time = end_time - start_time
            transfer_speed = total_data * 8 / transfer_time  # Bits per second
            received_percentage = (len(received_segments) / total_segments) * 100 if total_segments else 0

            # Log the results
            print(f"UDP transfer #{id} finished, total time: {transfer_time:.2f} seconds, total speed: {transfer_speed:.2f} bits/second"
                  f"\nPercentage of packets received successfully: {received_percentage:.2f}% \n")

        except Exception as e:
            print(f"Error during UDP transfer: {e}")
        finally:
            udp_socket.close()

    def _handle_server(self, server_ip, tcp_port, id):
        """Handle connection to the server."""
        print(f"TCP thread #{id} is Connecting to server...")
        self._handle_tcp_connection(server_ip, tcp_port, self.file_size, id)

    def _handle_tcp_connection(self, server_ip, tcp_port, file_size, id):
        """Handle TCP connection to the server."""
        try:
            tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_socket.connect((server_ip, tcp_port))

            # Send the file size as a request
            request_packet = struct.pack('!IBQ', MAGIC_COOKIE, REQUEST_MSG_TYPE, file_size)
            tcp_socket.sendall(request_packet)
            print(f"Sent TCP #{id} request for file size: {file_size} bytes to {server_ip}:{tcp_port}.")

            # Measure the time for receiving the data
            start_time = time.time()
            received_data = b""
            while len(received_data) < file_size:
                chunk = tcp_socket.recv(min(1024, file_size - len(received_data)))
                if not chunk:
                    raise ConnectionError("Connection closed prematurely by server.")
                received_data += chunk
            end_time = time.time()

            # Validate and log results
            transfer_time = end_time - start_time
            transfer_speed = len(received_data) * 8 / transfer_time  # Bits per second

            print(f"TCP transfer #{id} finished, total time: {transfer_time:.2f} seconds, total speed: {transfer_speed:.2f} bits/second")
        except Exception as e:
            print(f"Error in TCP connection: {e}")
        finally:
            tcp_socket.close()

    def stop(self):
        self.running = False


# Main Function for Client
def main():
    udp_port = 33333

    client = Client(udp_port)
    try:
        client.start()
        print("Client running. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down client...")
        client.stop()


if __name__ == "__main__":
    main()
