"""
transport-layer-protocols

The Internet Protocol is designed for use in interconnected systems of
packet-switched computer communication networks.
The internet protocol provides for transmitting blocks of data called
datagrams from sources to destinations, where sources and destinations
are hosts identified by fixed length addresses.  The internet protocol
also provides for fragmentation and reassembly of long datagrams, if
necessary, for transmission through "small packet" networks.

    0                   1                   2                   3
    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |Version|  IHL  |Type of Service|          Total Length         |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |         Identification        |Flags|      Fragment Offset    |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |  Time to Live |    Protocol   |         Header Checksum       |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                       Source Address                          |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                    Destination Address                        |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                    Options                    |    Padding    |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
"""

import socket
import struct
from enum import Enum, IntEnum


class IPDecorator:
    class Version(IntEnum):
        IPV4 = 4

    class IHL(IntEnum):
        DEFAULT = 5

    class Flags(IntEnum):
        RESERVED = 0
        DF = 2
        MF = 1

    class Protocol(IntEnum):
        ICMP = 1
        TCP = 6
        UDP = 17

    class TOS(Enum):
        DEFAULT = 0
        LOW_DELAY = 0x10
        HIGH_THROUGHPUT = 0x08
        HIGH_RELIABILITY = 0x04
        MINIMUM_COST = 0x02

    def __init__(
        self, source_ip: str, dest_ip: str, protocol: Protocol, payload_size: int, ttl: int = 64
    ) -> None:
        self.__version = IPDecorator.Version.IPV4
        self.__ihl = IPDecorator.IHL.DEFAULT
        self.__tos = IPDecorator.TOS.DEFAULT.value
        self.__total_length = 20 + payload_size
        self.__identification = 54321
        self.__flags = IPDecorator.Flags.DF
        self.__fragment_offset = 0
        self.__ttl = ttl
        self.__protocol = protocol
        self.__source_ip = source_ip
        self.__dest_ip = dest_ip

    def decorate(self, payload: bytes) -> bytes:
        ver_ihl = (self.__version << 4) + self.__ihl
        flags_frag_offset = (self.__flags << 13) + self.__fragment_offset

        initial_ip_header = self.__build_initial_header(ver_ihl, flags_frag_offset)
        checksum = self.__calculate_checksum(initial_ip_header)
        ip_header = self.__build_final_header(ver_ihl, flags_frag_offset, checksum)

        return ip_header + payload

    def __build_initial_header(self, ver_ihl: int, flags_frag_offset: int) -> bytes:
        ip_header = struct.pack(
            '!BBHHHBBH4s4s',
            ver_ihl,
            self.__tos,
            self.__total_length,
            self.__identification,
            flags_frag_offset,
            self.__ttl,
            self.__protocol,
            b'\x00',
            socket.inet_aton(self.__source_ip),
            socket.inet_aton(self.__dest_ip),
        )

        return ip_header

    def __build_final_header(self, ver_ihl: int, flags_frag_offset: int, checksum: int) -> bytes:
        ip_header = struct.pack(
            '!BBHHHBBH4s4s',
            ver_ihl,
            self.__tos,
            self.__total_length,
            self.__identification,
            flags_frag_offset,
            self.__ttl,
            self.__protocol,
            checksum,
            socket.inet_aton(self.__source_ip),
            socket.inet_aton(self.__dest_ip),
        )

        return ip_header

    def __calculate_checksum(self, header: bytes) -> int:
        if len(header) % 2 != 0:
            header += b'\x00'

        checksum = 0
        for i in range(0, len(header), 2):
            word = (header[i] << 8) + header[i + 1]
            checksum += word
            checksum = (checksum & 0xFFFF) + (checksum >> 16)

        checksum = ~checksum & 0xFFFF

        return checksum
