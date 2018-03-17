# -*- coding: utf-8 -*-
import os
import logging
import socket
SERVER_IP = '127.0.0.1'
SERVER_PORT = 25500
LISTEN_SIZE = 4
import select
LOG_FORMAT = '%(levelname)s | %(asctime)s | %(processName)s | ' \
             '%(message)s'
LOG_LEVEL = logging.DEBUG
LOG_DIR = 'log'
LOG_FILE = LOG_DIR+'/server.log'
READ_SIZE = 1024


def create_log():
    if not os.path.isdir(LOG_DIR):
        os.makedirs(LOG_DIR)
    with open(LOG_FILE, 'w') as log_file:
        log_file.write('')
    logging.basicConfig(format=LOG_FORMAT, filename=LOG_FILE, level=LOG_LEVEL)


def main():
    create_log()
    server_socket = socket.socket()
    try:
        server_socket.bind((SERVER_IP, SERVER_PORT))
        server_socket.listen(LISTEN_SIZE)
        messages_to_send = []
        open_client_sockets = []
        send_sockets = []
        while True:
            rlist, wlist, xlist = select.select([server_socket]+open_client_sockets,
                                                send_sockets, open_client_sockets)
            #sockets with exceptions
            for current_socket in xlist:
                logging.info('handling exception socket')
                current_socket.close()
                open_client_sockets.pop(open_client_sockets.index(
                    current_socket))
            #sockets ready for reading
            for current_socket in rlist:
                # check for new connection
                if current_socket is server_socket:
                    client_socket, client_address = current_socket.accept()
                    logging.info('received new connection from ' +
                                 str(client_address[0]+':'
                                     + str(client_address[1])))
                    open_client_sockets.append(client_socket)
                else:
                    data = current_socket.recv(READ_SIZE)
                    if data == '':
                        current_socket.close()
                        open_client_sockets.pop(open_client_sockets.index(
                            current_socket))
                    else:
                        logging.info('received data: ' + data)
                        messages_to_send.append((current_socket, data))
                        send_sockets.append(current_socket)
            # socket ready to write
            for current_socket in wlist:
                for message in messages_to_send:
                    if message[0] is current_socket:
                        current_socket.send(message[1])
                        messages_to_send.pop(
                            messages_to_send.index(message))
                        logging.info('send to a client: '+message[1])
                send_sockets.pop(send_sockets.index(
                    current_socket))
    except socket.error as err:
        logging.info('received socket error - exiting, '
                     + str(err))
    finally:
        server_socket.close()


if __name__ == '__main__':
    main()