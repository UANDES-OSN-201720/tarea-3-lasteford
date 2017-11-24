# -*- coding: utf-8 -*-
"""
Created on Fri Nov 24 15:26:01 2017

@author: ALFONSO
"""

import socket
import threading
import sys
import mensaje_pb2
import datetime

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

def Deserializar(data):
    b = mensaje_pb2.Mensaje()
    b.ParseFromString(data)
    return b
        

def Serializar(group, destination, sender, data_type, content, date):
    message = mensaje_pb2.Mensaje()
    message.group = group
    message.ip_destination = destination
    message.id_sender = sender
    message.data_type = data_type
    message.content = content
    message.date = date
    return message.SerializeToString()

def manage_connection(connection, client_address):
    mensaje = ""
    try:
        print 'Conexión desde', client_address
        while True:
            data = connection.recv(16)
            print 'Recibido "%s"' %data
            mensaje += data
            if data:
                print 'Enviando data de vuelta al cliente'
                connection.sendall(data)
            else:
                print 'No hay más data de', client_address
                break
    finally:
        connection.close()
        informacion = Deserializar(mensaje)
        sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        destination_address = (informacion.ip_destination, 8080)
        sock2.connect(destination_address)
        try:
            print '\nEnviando'
            sock2.sendall(mensaje)
            amount_received = 0
            amount_expected = len(mensaje)
            while amount_received < amount_expected:
                data = sock2.recv(16)
                amount_received += len(data)
                print 'Recibido'
    
        finally:
            print 'Cerrando el socket'
            sock2.close()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #se crea el socket

server_adress = 'localhost', 8080 #servidor y puerto

print 'Inicializando en %s puerto %s' %server_adress

sock.bind(server_adress)

sock.listen(1)

while True:
    print 'Esperando una conexión'
    connection, client_address = sock.accept()
    t = threading.Thread(target=manage_connection, args=(connection, client_address))
    t.start()    