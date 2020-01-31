# coding=utf-8
from dataclasses import dataclass
from typing import Optional


@dataclass
class Room:
    room_number: str
    description: str
    vlan_number: str
