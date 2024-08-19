"""
transport-layer-protocols
"""

from protocols.ip import IPStruct
from protocols.tun import TUNInterface

from .udp_struct import UDPStruct


class UDPClient:
    def __init__(self, host_ip: str, host_port: int, dest_ip: str, dest_port: int) -> None:
        self.__host_ip = host_ip
        self.__host_port = host_port
        self.__dest_ip = dest_ip
        self.__dest_port = dest_port
        self.__tun_interface = TUNInterface()

    def send(self, payload: bytes) -> None:
        marshaled_udp_frame = UDPStruct(
            self.__host_ip, self.__dest_ip, self.__host_port, self.__dest_port
        ).marshal(payload)

        marshaled_ip_frame = IPStruct(
            self.__host_ip,
            self.__dest_ip,
            IPStruct.Protocol.UDP,
        ).marshal(marshaled_udp_frame)

        self.__tun_interface.write(marshaled_ip_frame)
