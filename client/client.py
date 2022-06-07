# -*- coding: utf-8 -*-
"""
Created on Tue May 31 14:01:23 2022

@author: Admin
"""

import socket
import sys

HOST = 'localhost'

BUFFER_SIZE = 4096


class Client:
    def __init__(self):
        self.__client_socket = None

    def set_client_socket(self):
        self.__client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def download_file(self, command):
        # send get command (get <filename)
        self.__client_socket.sendto(command.encode(), SERVER_ADDRESS)
        # receive the first datagram
        bytes_read, addr = self.__client_socket.recvfrom(BUFFER_SIZE)
        # if the received datagram contains an error message the transmission cannot continue
        if bytes_read.decode().split()[0] == 'error':
            print(bytes_read.decode())
            return
        try:
            with open(command.split()[1], 'wb') as file:
                # if the first datagram received is not an error message it is part of the file, so it can be written
                file.write(bytes_read)
                while True:
                    self.__client_socket.settimeout(2.0)
                    try:
                        bytes_read, addr = self.__client_socket.recvfrom(BUFFER_SIZE)
                        file.write(bytes_read)
                    except socket.timeout:
                        # no more datagram from the server, eof reached
                        self.__client_socket.settimeout(None)
                        break
            file.close()
        except OSError:
            print('\r\n error on get (client side): cannot open ' + command.split()[1] + '!')
            return
        # receive the final message from the server, confirms the transmission is over
        bytes_read, addr = self.__client_socket.recvfrom(BUFFER_SIZE)
        print(bytes_read.decode())

    def upload_file(self, command):
        try:
            with open(command.split()[1], "r") as file:
                # send put command
                self.__client_socket.sendto(command.encode(), SERVER_ADDRESS)
                # receiving ok message
                bytes_read, addr = self.__client_socket.recvfrom(BUFFER_SIZE)
                while True:
                    bytes_read = file.read(BUFFER_SIZE)
                    if not bytes_read:
                        # eof reached
                        break
                    self.__client_socket.sendto(bytes_read.encode(), addr)
            file.close()
        except OSError:
            print('\r\n error on put (client side): cannot open ' + command.split()[1] + '!')
            return
        bytes_read, addr = self.__client_socket.recvfrom(BUFFER_SIZE)
        print(bytes_read.decode())

    def run(self):
        self.set_client_socket()
        while True:
            try:
                command = input('\n\r: ')

                if command.split()[0].lower() == 'get':
                    if len(command.split()) == 2:
                        self.download_file(command)
                    else:
                        print('\r\n error on get (client side): two args needed!')

                elif command.split()[0].lower() == 'put':
                    if len(command.split()) == 2:
                        self.upload_file(command)
                    else:
                        print('\r\n error on put (client side): two args needed!')
                elif command.split()[0].lower() == 'quit':
                    break
                else:
                    self.__client_socket.sendto(command.encode(), SERVER_ADDRESS)
                    bytes_read, addr = self.__client_socket.recvfrom(BUFFER_SIZE)
                    print(bytes_read.decode())
            except IndexError:
                print('\r\n error: no command typed in!')
            except ConnectionResetError:
                print('\r\n error: cannot receive any data (please choose the right port)')
        self.__client_socket.close()


try:
    if len(sys.argv) != 2:
        print('\r\n error: port number needed!')
        sys.exit()
    server_port = int(sys.argv[1])
    SERVER_ADDRESS = (HOST, server_port)
    Client().run()
except ValueError:
    print('\r\n please insert an integer value')
