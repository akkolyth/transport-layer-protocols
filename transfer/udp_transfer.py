"""
transport-layer-protocols
"""

import socket
import threading

from protocols import UDPClient


class UDPReceiver:
    def __init__(self, host_ip: str, host_port: int, output_file: str) -> None:
        self.host_ip = host_ip
        self.host_port = host_port
        self.output_file = output_file
        self.is_running = True

    def start(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind((self.host_ip, self.host_port))
            print(f'Listening on {self.host_ip}:{self.host_port}')

            with open(self.output_file, 'wb') as f:
                while self.is_running:
                    data, addr = sock.recvfrom(65535)
                    if not data:
                        break
                    print(f'Received data from {addr}')
                    f.write(data)
                    f.flush()

    def stop(self) -> None:
        self.is_running = False


def send_file(file_path: str, client: UDPClient) -> None:
    with open(file_path, 'rb') as f:
        while chunk := f.read(1024):
            client.send(chunk)
    print('File sent successfully!')


def receiver_thread(receiver: UDPReceiver) -> None:
    receiver.start()


def client_thread(file_path: str, client: UDPClient) -> None:
    send_file(file_path, client)


def _main() -> None:
    udp_receiver = UDPReceiver('127.0.0.1', 5000, 'received_file.txt')
    udp_client = UDPClient('127.0.0.1', 5001, 5000)

    receiver_thread_instance = threading.Thread(target=receiver_thread, args=(udp_receiver,))
    client_thread_instance = threading.Thread(
        target=client_thread, args=('file_to_send.txt', udp_client)
    )

    receiver_thread_instance.start()
    client_thread_instance.start()

    client_thread_instance.join()
    udp_receiver.stop()
    receiver_thread_instance.join()


if __name__ == '__main__':
    _main()
