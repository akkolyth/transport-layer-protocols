"""
transport-layer-protocols
"""

import logging
import struct
import sys

sys.path.append('/workspaces/transport-layer-protocols')

from rich.console import Console
from rich.logging import RichHandler

from protocols import TUNInterface, UDPClient

console = Console()
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    datefmt='[%X]',
    handlers=[RichHandler(console=console)],
)
logger = logging.getLogger('udp')


class DNSQuery:
    def __init__(self, domain_name: str) -> None:
        self.domain_name = domain_name

    def marshal(self) -> bytes:
        transaction_id = 0x1234  # Identifier (can be random)
        flags = 0x0100  # Standard query with recursion desired
        questions = 1  # Number of questions
        answer_rrs = 0  # No answers in the query
        authority_rrs = 0  # No authority resource records
        additional_rrs = 0  # No additional records

        dns_header = struct.pack(
            '!HHHHHH', transaction_id, flags, questions, answer_rrs, authority_rrs, additional_rrs
        )

        qname = (
            b''.join(
                struct.pack('!B', len(label)) + label.encode()
                for label in self.domain_name.split('.')
            )
            + b'\x00'
        )
        qtype = 1  # Type A (host address)
        qclass = 1  # Class IN (Internet)

        dns_question = qname + struct.pack('!HH', qtype, qclass)

        dns_query = dns_header + dns_question
        return dns_query


def _main() -> None:
    tun_interface = TUNInterface()
    udp_client = UDPClient(
        host_ip='192.0.2.2',
        host_port=30732,
        dest_ip='1.1.1.1',
        dest_port=53,
    )

    dns_query = DNSQuery('example.com').marshal()
    udp_client.send(dns_query)

    logger.info(tun_interface.read(1024).hex())


if __name__ == '__main__':
    _main()
