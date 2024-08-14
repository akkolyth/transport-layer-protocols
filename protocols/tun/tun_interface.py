"""
transport-layer-protocols
"""

import struct
from fcntl import ioctl
from typing import BinaryIO


class TUNInterface:
    _TUN_NAME = b'tun0'
    _TUN_DEVICE = 'dev/net/tun'

    # Define the TUN device flag. This is used to configure a virtual network interface in TUN mode.
    # TUN mode operates at the IP level (Layer 3), where it passes IP packets directly.
    _LINUX_IFF_TUN = 0x0001

    # Disable packet information for the TUN device.
    # The NO_PI flag indicates that no packet information (like protocol type) should be prepended to packets.
    _LINUX_IFF_NO_PI = 0x1000

    # This is the ioctl command used to set interface options for the TUN device.
    # TUNSETIFF is the command that will set the name of the TUN/TAP device and its mode (TUN or TAP).
    _LINUX_TUNSETIFF = 0x400454CA

    def __init__(self) -> None:
        self.__ifs = struct.pack(
            '16sH22s',
            TUNInterface._TUN_DEVICE,
            TUNInterface._LINUX_IFF_TUN | TUNInterface._LINUX_IFF_NO_PI,
            b'',
        )

    def read(self, size: int) -> bytes:
        tun = self.__open_device()
        payload = tun.read(size)
        return payload

    def write(self, payload: bytes) -> None:
        tun = self.__open_device()
        tun.write(payload)

    def __open_device(self) -> BinaryIO:
        tun = open(TUNInterface._TUN_DEVICE, mode='r+b', buffering=0)
        ioctl(tun, TUNInterface._LINUX_TUNSETIFF, self.__ifs)
        return tun
