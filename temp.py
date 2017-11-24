# -*- coding: utf-8 -*-
"""
Created on Fri Nov 24 17:39:47 2017

@author: ALFONSO
"""

import socket
import sys
import mensaje_pb2
import datetime


def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

print datetime.date.today()