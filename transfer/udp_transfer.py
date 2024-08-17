import logging
import socket
import sys

sys.path.append('/workspaces/transport-layer-protocols')
import threading

from rich.console import Console
from rich.logging import RichHandler

from protocols import UDPClient

console = Console()
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    datefmt='[%X]',
    handlers=[RichHandler(console=console)],
)
logger = logging.getLogger('udp')


class UDPSocketReceiver:
    def __init__(self, host_ip: str, host_port: int, output_file: str) -> None:
        self.__host_ip = host_ip
        self.__host_port = host_port
        self.__output_file = output_file
        self.__is_running = True

    def start(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind((self.__host_ip, self.__host_port))
            logger.info(f'Listening on {self.__host_ip}:{self.__host_port}')

            with open(self.__output_file, 'wb') as f:
                while self.__is_running:
                    data, addr = sock.recvfrom(65535)
                    if not data:
                        break

                    logger.info(f'Received data from {addr}')
                    f.write(data)
                    f.flush()

    def stop(self) -> None:
        self.__is_running = False
        logger.info('Receiver stopped')


class UDPSocketSender:
    def __init__(self, dest_ip: str, dest_port: int) -> None:
        self.__dest_ip = dest_ip
        self.__dest_port = dest_port

    def send(self, data: bytes) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, b'tun0')
            sock.sendto(data, (self.__dest_ip, self.__dest_port))
            logger.info(f'Sent data to {self.__dest_ip}:{self.__dest_port}')


def _send_file_via_client(file_path: str, client: UDPClient) -> None:
    with open(file_path, 'rb') as f:
        while chunk := f.read(1024):
            client.send(chunk)
    logger.info('File sent successfully!')


def _send_file_via_socket_client(file_path: str, client: UDPSocketSender) -> None:
    with open(file_path, 'rb') as f:
        while chunk := f.read(1024):
            client.send(chunk)
    logger.info('File sent successfully!')


def _socket_client_thread(file_path: str, client: UDPSocketSender) -> None:
    _send_file_via_socket_client(file_path, client)


def _client_thread(file_path: str, client: UDPClient) -> None:
    _send_file_via_client(file_path, client)


def _receiver_thread(receiver: UDPSocketReceiver) -> None:
    receiver.start()


def _main() -> None:
    udp_receiver = UDPSocketReceiver(
        '127.0.0.1', 5000, '/workspaces/transport-layer-protocols/data/received_file.txt'
    )

    udp_client = UDPClient(host_ip='192.0.1.1', host_port=5001, dest_ip='1.1.1.1', dest_port=53)

    receiver_thread_instance = threading.Thread(target=_receiver_thread, args=(udp_receiver,))
    client_thread_instance = threading.Thread(
        target=_client_thread,
        args=('/workspaces/transport-layer-protocols/data/lorem_ipsum.txt', udp_client),
    )

    receiver_thread_instance.start()
    client_thread_instance.start()
    client_thread_instance.join()
    udp_receiver.stop()
    receiver_thread_instance.join()


if __name__ == '__main__':
    _main()
