# -*- coding: utf-8 -*-
"""
Created on Tue May 31 13:47:59 2022

@author: Admin
"""

import threading
from threading import Thread
import socket
import os
import time
import sys
import random

HOST = 'localhost'
BUFFER_SIZE = 4096

lock = threading.Lock()

class Server(threading.Thread):
    def __init__(self, address):
        threading.Thread.__init__(self)
        self.__address = address
        self.__server_socket = None
        self.__sockets = {}

    def set_server_socket(self):
        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.__server_socket.bind(self.__address)
        except OverflowError:
            print('\r\n please select a port between 0 and 65535')
            sys.exit()

    def close(self):
        for client_socket in self.__sockets:
            client_socket.close()
        self.__server_socket.close()

    def handle_client(self, args, client_address, new_port):
        message = None
        if args[0].lower() == 'get':
            lock.acquire()
            message = self.handle_get(args, client_address, new_port)
        elif args[0].lower() == 'put':
            lock.acquire()
            message = self.handle_put(args, client_address, new_port)
        elif args[0].lower() == 'list':
            lock.acquire()
            message = '\r\n' + str(os.listdir()) + '.'
        elif args[0].lower() == 'help':
            # acquiring lock is not needed (help command does not use resources)
            message = '\r\nget <filename> -> download <filename> from server\r\nput <filename> -> upload ' \
                      'the local <filename> to the server\r\nlist -> get the list of files in the ' \
                      'server\r\nquit -> disconnect from the server '
        else:
            message = '\n\r no valid command'
        time.sleep(2)
        self.__sockets[new_port].sendto(message.encode(), client_address)
        if lock.locked():
            lock.release()

    def handle_get(self, args, client_address, new_port):
        try:
            with open(args[1], "r") as file:
                while True:
                    bytes_read = file.read(BUFFER_SIZE)
                    if not bytes_read:
                        break
                    self.__sockets[new_port].sendto(
                        bytes_read.encode(), client_address)
            file.close()
        except FileNotFoundError:
            message = '\r\n error on get: ' + args[1] + ' not found!'
            return message
        except OSError:
            message = '\r\n error on get: cannot open ' + args[1] + '!'
            return message
        except:
            message = '\r\n error on get: unexpected error handling ' + \
                      args[1] + '!'
            return message
        message = '\r\n' + args[1] + ' downloaded.'
        return message

    def handle_put(self, args, client_address, new_port):
        try:
            message = "init message"
            self.__sockets[new_port].sendto(
                message.encode(), client_address)
            with open(args[1], 'wb') as file:
                self.__sockets[new_port].settimeout(2.0)
                while True:
                    try:
                        bytes_read, addr = self.__sockets[new_port].recvfrom(
                            BUFFER_SIZE)
                        file.write(bytes_read)
                    except socket.timeout:
                        self.__sockets[new_port].settimeout(None)
                        break
            file.close()
        except OSError:
            message = '\r\n error on put: cannot open ' + args[1] + '!'
            return message
        except:
            message = '\r\n error on put: unexpected error handling ' + \
                      args[1] + '!'
            return message
        message = '\r\n' + args[1] + ' uploaded.'
        return message

    def run(self):
        self.set_server_socket()
        print('\n\r server on %s port %s' % self.__address)
        while True:
            self.__server_socket.settimeout(None)
            data, client_address = self.__server_socket.recvfrom(BUFFER_SIZE)
            # assign a random port to new client
            new_port = int(sys.argv[1]) + random.randint(1, 100)
            while new_port in self.__sockets:
                new_port = int(sys.argv[1]) + random.randint(1, 100)
            self.__sockets[new_port] = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.__sockets[new_port].bind((HOST, new_port))

            Thread(target=self.handle_client,
                   args=(data.decode().split(), client_address, new_port,)).start()


try:
    if len(sys.argv) != 2:
        print('\r\n error: port number needed!')
        sys.exit()
    port = int(sys.argv[1])
    server_address = (HOST, port)
    myserver = Server(server_address)
    MAIN_THREAD = Thread(target=myserver.run)
    MAIN_THREAD.start()
    MAIN_THREAD.join()
    myserver.close()
except ValueError:
    print('\r\n please insert an integer value')




