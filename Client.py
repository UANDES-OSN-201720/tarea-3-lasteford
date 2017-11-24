# -*- coding: utf-8 -*-
"""
Created on Fri Nov 24 15:39:08 2017

@author: ALFONSO
"""

import socket
import sys
import mensaje_pb2
import threading
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
    
def manage_connection(connection, server_address):
    mensaje = ""
    try:
        print 'Conexión desde', server_address
        while True:
            data = connection.recv(16)
            print 'Recibido "%s"' %data
            mensaje += data
            if data:
                print 'Enviando data de vuelta al cliente'
                connection.sendall(data)
            else:
                print 'No hay más data de', server_address
                break
    finally:
        connection.close()
        informacion = Deserializar(mensaje)
        print 'Te llegó un mensaje de %s:\n"%s"' %informacion.id_sender, informacion.content
    
def modoConectado():
    sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        connection, server_address = sock2.accept()
        t = threading.Thread(target=manage_connection, args=(connection, server_address))
        t.start()  
ip_server = raw_input("Ingrese el IP del servidor: ")
my_ip = get_ip_address()
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
thread_conexion = threading.Thread(target=modoConectado)
thread_conexion.start()
server_address = (ip_server, 8080)

print 'Conectando con %s puerto %s' %server_address
while True:
    raw_input("Presiona Enter para enviar un mensaje...")
    group = raw_input("¿Mensaje grupal(0) o personal(1)?: ")
    while True:
        if group == '0':
            group = True
            break
        elif group == '1':
            group == False
            break
        group = raw_input("¿Mensaje grupal(0) o personal(1)?: ")   
    dest = raw_input("Ingresa la IP del destino o código del grupo: ")
    data_type = raw_input("Escribe 'SI' deseas enviar un archivo en lugar de un mensaje: " )
    content = None    
    if data_type == 'SI':
        data_type = False
        content = "bla bla" #no esta implementado aun
        #falta completar
    else:
        data_type = True
        content = raw_input("Escribe el mensaje que quieres enviar:\n")
    sock.connect(server_address)
    try:
        info = Serializar(group, dest, str(get_ip_address()), str(data_type), content, datetime.date.today())
        print '\nEnviando: "%s"' % message
        sock.sendall(info)
        amount_received = 0
        amount_expected = len(info)
        while amount_received < amount_expected:
            data = sock.recv(16)
            amount_received += len(data)
            print 'Recibido: "%s"' % data
    
    finally:
        print 'Cerrando el socket'
        sock.close()