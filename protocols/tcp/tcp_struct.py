"""
transport-layer-protocols

TCP segments are sent as internet datagrams.  The Internet Protocol
header carries several information fields, including the source and
destination host addresses [2].  A TCP header follows the internet
header, supplying information specific to the TCP protocol.  This
division allows for the existence of host level protocols other than TCP.
https://datatracker.ietf.org/doc/html/rfc9293

0                   1                   2                   3
0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|          Source Port          |       Destination Port        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                        Sequence Number                        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    Acknowledgment Number                      |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|  Data |           |U|A|P|R|S|F|                               |
| Offset| Reserved  |R|C|S|S|Y|I|            Window             |
|       |           |G|K|H|T|N|N|                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|           Checksum            |         Urgent Pointer        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    Options                    |    Padding    |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                             data                              |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
"""

import socket
import struct


class TCPStruct:
    def __init__(
        self,
        source_port: int,
        source_ip: str,
        dest_port: int,
        seq_num: int,
        ack_num: int,
        data_offset: int,
        flags: int,
        window_size: int,
        urgent_ptr: int,
        dest_ip: str,
    ) -> None:
        self.__source_port = source_port
        self.__source_ip = source_ip
        self.__dest_port = dest_port
        self.__dest_ip = dest_ip
        self.__seq_num = seq_num
        self.__ack_num = ack_num
        self.__data_offset = data_offset
        self.__flags = flags
        self.__window_size = window_size
        self.__urgent_ptr = urgent_ptr

    def marshal(self, payload: bytes) -> bytes:
        # TCP header format: !HHLLBBHHH
        # Explanation of format:
        # H = unsigned short (2 bytes), L = unsigned long (4 bytes), B = unsigned char (1 byte)
        # ! = network (big-endian) byte order
        # Source port, Destination port, Sequence number, Acknowledgment number, Data offset and flags packed into 1 byte each
        tcp_header = struct.pack(
            '!HHLLBBHHH',
            self.__source_port,  # Source Port (2 bytes)
            self.__dest_port,  # Destination Port (2 bytes)
            self.__seq_num,  # Sequence Number (4 bytes)
            self.__ack_num,  # Acknowledgment Number (4 bytes)
            (self.__data_offset << 4)
            | (self.__flags >> 2),  # Data Offset (4 bits) and Reserved (3 bits)
            self.__flags & 0x3F,  # Flags (6 bits)
            self.__window_size,  # Window size (2 bytes)
            0,  # Checksum (initialize as 0)
            self.__urgent_ptr,  # Urgent Pointer (2 bytes)
        )

        # Pseudo-header for checksum calculation
        pseudo_header = struct.pack(
            '!4s4sBBH',
            socket.inet_aton(self.__source_ip),  # Source IP (4 bytes)
            socket.inet_aton(self.__dest_ip),  # Destination IP (4 bytes)
            0,  # Zero (1 byte)
            socket.IPPROTO_TCP,  # Protocol (TCP=6)
            len(tcp_header) + len(payload),  # TCP Length (header + payload)
        )

        # Calculate checksum including pseudo-header, TCP header, and payload
        full_packet = pseudo_header + tcp_header + payload
        tcp_checksum = self.__checksum(full_packet)

        # Re-pack TCP header with the correct checksum
        tcp_header = struct.pack(
            '!HHLLBBHHH',
            self.__source_port,
            self.__dest_port,
            self.__seq_num,
            self.__ack_num,
            (self.__data_offset << 4) | (self.__flags >> 2),
            self.__flags & 0x3F,
            self.__window_size,
            tcp_checksum,
            self.__urgent_ptr,
        )

        # Return full TCP segment (header + payload)
        return tcp_header + payload

    def __checksum(self, msg: bytes) -> int:
        if len(msg) % 2 != 0:
            msg += b'\x00'  # Padding if the length of the data is odd
        s = sum(struct.unpack(f'!{len(msg) // 2}H', msg))
        s = (s >> 16) + (s & 0xFFFF)  # Add overflow if any
        s += s >> 16  # Add overflow again
        s = ~s & 0xFFFF  # One's complement
        return s
