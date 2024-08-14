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

import struct


class UDPDecorator:
    _HEADER_SIZE_BYTES = 8
    _MAX_PAYLOAD_BYTES = 65527

    def __init__(self, host_port: int, dest_port: int) -> None:
        self.__host_port = host_port
        self.__dest_port = dest_port

    def decorate(self, payload: bytes) -> bytes:
        if len(payload) > UDPDecorator._MAX_PAYLOAD_BYTES:
            raise ValueError(
                f'Payload exceeds max UDP size: {UDPDecorator._MAX_PAYLOAD_BYTES} bytes'
            )

        packed_ports = self.__pack_port(self.__host_port) + self.__pack_port(self.__dest_port)
        length = self.__calculate_length(payload)
        checksum = self.__calculate_checksum(packed_ports + length + b'\x00\x00' + payload)
        return packed_ports + length + checksum + payload

    def __pack_port(self, port: int) -> bytes:
        return struct.pack('!H', port)

    def __calculate_length(self, payload: bytes) -> bytes:
        length = UDPDecorator._HEADER_SIZE_BYTES + len(payload)
        return struct.pack('!H', length)

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
