"""
transport-layer-protocols
"""

from src.ip import IPStruct
from src.tun import TUNInterface

from .udp_struct import UDPStruct


class UDPClient:
    def __init__(self, host_ip: str, host_port: int, dest_port: int) -> None:
        self.__host_ip = host_ip
        self.__host_port = host_port
        self.__dest_port = dest_port
        self.__tun_interface = TUNInterface()

    def send(self, payload: bytes) -> None:
        marshaled_udp_frame = UDPStruct(self.__host_port, self.__dest_port).marshal(payload)
        marshaled_ip_frame = IPStruct(
            '127.0.0.1', self.__host_ip, IPStruct.Protocol.UDP, len(marshaled_udp_frame)
        ).marshal(payload)
        self.__tun_interface.write(marshaled_ip_frame)
