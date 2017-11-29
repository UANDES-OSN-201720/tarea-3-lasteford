# -*- coding: utf-8 -*-
"""
Created on Fri Nov 24 15:39:08 2017

@author: ALFONSO
"""
import os
import socket
import sys
import mensaje_pb2
import threading
import datetime
import base64
from numpy import random
from time import gmtime, strftime, sleep

def clear():
    os.system('cls')
    print '\t\t~~~CHATROOM~~~'
    print '\t\t  BIENVENID@\n'

def get_ip_address():
    return ([l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0])
    
def redactar():
    clear()
    print "¿Que tipo de mensaje desea enviar?\n\t1. Grupal\n\t2. Personal"
    group = None
    while group not in ['1', '2']:
        group = raw_input("Su respuesta: ")
    ip_destination = None
    clear()
    if group == '2':
        group = True
        ip_destination = raw_input("Ingrese nombre del destinatario: ")
    else:
        group = False
        ip_destination = raw_input("Ingrese el código de la conversación grupal: ")
    clear()
    data_type = raw_input("¿Desea enviar un...?\n\t1. Mensaje\n\t2. Archivo\nSu respuesta: ")
    while data_type not in ['1', '2']:
        data_type = raw_input("Su respuesta: ")
    clear()
    content = None
    if data_type == '1':
        data_type = True
        content = raw_input("Escriba su mensaje aquí: \n\t")
    else:
        data_type = False
        origen = raw_input("Ingrese el nombre del archivo que desea enviar: ")
        content = encode_file(origen)
    clear()
    return Serializar(group, ip_destination, '10.52.76.218', data_type, content, str(datetime.date.today()))

def create_group():
    personas = ""
    while True:
        p = raw_input('Ingrese el nombre de una persona o deje en blanco para terminar: ')
        if p != "":
            personas += p+"_"
        else:
            break
    mensaje = 'NEWGROUP_'+personas+"END"
    codigo = random.randint(10000,99999)
    print 'El código de tu grupo es', codigo
    raw_input("Presiona Enter para continuar...")
    return Serializar(True, str(codigo),'10.52.76.218', True, mensaje, str(datetime.date.today()))

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
    
def encode_file(file_name):
    the_file = open(file_name, 'rb')
    file_read = the_file.read()
    return base64.encodestring(file_read)
    
def decode_file(encoded_file):
    file_decoded = base64.decodestring(encoded_file)
    file_store = open('chat '+str(strftime("%Y%m%d%H%M%S", gmtime())), 'wb')
    file_store.write(file_decoded)
    file_store.close()
    
def manage_connection(connection, server_address):
    mensaje = ""
    try:
        #print 'Conexión desde', server_address
        while True:
            data = connection.recv(16)
            #print 'Recibido "%s"' %data
            mensaje += data
            if data:
                #print 'Enviando data de vuelta al cliente'
                connection.sendall(data)
            else:
                #print 'No hay más data de', server_address
                break
    finally:
        connection.close()
        informacion = Deserializar(mensaje)
        clear()
        if informacion.data_type:
            print 'Te llegó un mensaje de '+str(informacion.id_sender)+'\n'
            print '\t"%s"' %informacion.content
        else:
            print '\t----------Te llegó un archivo desde %s\n' % str(informacion.id_sender)
            decode_file(informacion.content)
    
def modoConectado(my_ip, puerto):
    sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    myIP = my_ip, puerto
    sock2.bind(myIP)
    sock2.listen(1)
    while True:
        connection, server_address = sock2.accept()
        t = threading.Thread(target=manage_connection, args=(connection, server_address))
        t.start()  

ip_server = raw_input("Ingrese el IP del servidor: ")
my_ip = '10.52.76.218'
name = raw_input("Ingrese su nombre: ")
puerto = random.randint(10000,16001)
mensaje_inicial = 'NEWUSER'+"_"+name+"_"+my_ip+"_"+str(puerto)
intro = Serializar(True, ip_server, my_ip, True, mensaje_inicial, str(datetime.date.today()))
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ip_server, 15555
sock.connect(server_address)
try:
    sock.sendall(intro)
    amount_received = 0
    amount_expected = len(intro)
    while amount_received < amount_expected:
        data = sock.recv(16)
        amount_received += len(data)
        #print 'Recibido: "%s"' % data

finally:
    #print 'Cerrando el socket'
    sock.close()
clear()

thread_conexion = threading.Thread(target=modoConectado, args=(my_ip, puerto))
thread_conexion.start()

while True:
    sleep(1)
    accion = raw_input("¿Que desea hacer?\n\t1. Enviar mensaje\n\t2. Crear grupo\n\t3. Salir\nSu respuesta: ")
    info = None    
    if accion == '1' or accion == '2':
        if accion == '1':
            info = redactar()
        else:
            info = create_group()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ip_server, 15555
        sock.connect(server_address)
        try:
            sock.sendall(info)
            amount_received = 0
            amount_expected = len(info)
            while amount_received < amount_expected:
                data = sock.recv(16)
                amount_received += len(data)
                #print 'Recibido: "%s"' % data
        
        finally:
            #print 'Cerrando el socket'
            sock.close()
    elif accion == '3':
        exit(1)
    else:
        continue