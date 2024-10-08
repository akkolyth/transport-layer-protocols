"""
transport-layer-protocols

User Datagram  Protocol  (UDP)  is  defined  to  make  available  a
datagram   mode  of  packet-switched   computer   communication  in  the
environment  of  an  interconnected  set  of  computer  networks.
This protocol  assumes  that the Internet  Protocol  (IP)  is used as the
underlying protocol. RFC available here: https://datatracker.ietf.org/doc/html/rfc768

 0      7 8     15 16    23 24    31
+--------+--------+--------+--------+
|     Source      |   Destination   |
|      Port       |      Port       |
+--------+--------+--------+--------+
|                 |                 |
|     Length      |    Checksum     |
+--------+--------+--------+--------+
|
|          data octets ...
+---------------- ...
"""

import ipaddress
import struct


class UDPStruct:
    _HEADER_SIZE_BYTES = 8
    _MAX_PAYLOAD_BYTES = 65527

    def __init__(self, src_ip: str, dest_ip: str, src_port: int, dest_port: int) -> None:
        self.__src_ip = ipaddress.ip_address(src_ip).packed
        self.__dest_ip = ipaddress.ip_address(dest_ip).packed
        self.__src_port = src_port
        self.__dest_port = dest_port

    def marshal(self, payload: bytes) -> bytes:
        if len(payload) > UDPStruct._MAX_PAYLOAD_BYTES:
            raise ValueError(f'Payload exceeds max UDP size: {UDPStruct._MAX_PAYLOAD_BYTES} bytes')

        packed_ports = self.__pack_port(self.__src_port) + self.__pack_port(self.__dest_port)
        length = self.__calculate_length(payload)
        pseudoheader = self.__create_pseudoheader(length)
        checksum = self.__calculate_checksum(
            pseudoheader + packed_ports + length + b'\x00\x00' + payload
        )
        return packed_ports + length + checksum + payload

    def __pack_port(self, port: int) -> bytes:
        return struct.pack('!H', port)

    def __calculate_length(self, payload: bytes) -> bytes:
        length = UDPStruct._HEADER_SIZE_BYTES + len(payload)
        return struct.pack('!H', length)

    def __create_pseudoheader(self, length: bytes) -> bytes:
        return self.__src_ip + self.__dest_ip + b'\x00' + b'\x11' + length

    def __calculate_checksum(self, header_and_data: bytes) -> bytes:
        if len(header_and_data) % 2 != 0:
            header_and_data += b'\x00'

        checksum = 0

        for i in range(0, len(header_and_data), 2):
            word = (header_and_data[i] << 8) + header_and_data[i + 1]
            checksum += word
            checksum = (checksum & 0xFFFF) + (checksum >> 16)

        checksum = ~checksum & 0xFFFF

        # if checksum results in 0x0000, return 0xFFFF as per UDP standard
        return struct.pack('!H', checksum if checksum != 0 else 0xFFFF)
