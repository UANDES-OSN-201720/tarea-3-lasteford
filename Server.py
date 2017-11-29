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

class Client:
    def __init__(self, IP, port, name):
        self.IP = IP
        self.port = port
        self.name = name
        
def registrar(ip, puerto, nombre, registro):
    if nombre not in registro:
        c = Client(ip, puerto, nombre)
        registro[nombre] = c
        print'"%s" se ha registrado!' % nombre
    else:
        registro[nombre].port = puerto
        registro[nombre].IP = ip

def get_ip_address():
    return ([l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0])

def Deserializar(data):
    b = mensaje_pb2.Mensaje()
    b.ParseFromString(data)
    return b
        
def crear_grupo(informacion, grupos, registros):
    grupos[informacion.ip_destination] = []
    nombres = informacion.content.split('_')
    for i in range(1,len(nombres)-1):
        if nombres[i] in registros:
            grupos[informacion.ip_destination].append(registros[nombres[i]])

def Serializar(group, destination, sender, data_type, content, date):
    message = mensaje_pb2.Mensaje()
    message.group = group
    message.ip_destination = destination
    message.id_sender = sender
    message.data_type = data_type
    message.content = content
    message.date = date
    return message.SerializeToString()

def manage_connection(connection, client_address, registro, grupos):
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
        info = informacion.content.split('_')
        print info[0]
        if info[0] == 'NEWUSER':
            registrar(info[2], int(info[3]), info[1], registro)
            return
        elif info[0] == 'NEWGROUP':
            crear_grupo(informacion, grupos, registro)
            return
        elif informacion.group != True:
            for i in grupos[informacion.ip_destination]:
                sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                destination_address = (i.IP, i.port)
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
            return
        sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        destino = informacion.ip_destination
        destination_address = (registro[destino].IP, registro[destino].port)
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
            
registrados = {}
grupos = {}

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #se crea el socket

server_adress = '10.52.76.218', 15555 #servidor y puerto

print 'Inicializando en %s puerto %s' %server_adress

sock.bind(server_adress)

sock.listen(1)

while True:
    print 'Esperando una conexión'
    connection, client_address = sock.accept()
    t = threading.Thread(target=manage_connection, args=(connection, client_address, registrados, grupos))
    t.start()    