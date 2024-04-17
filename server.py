import socket
import struct
import os
from zlib import crc32
from constants import DEFAULT_SERVER_PORT,\
    BUFF_SIZE, \
    SOURCE_PORT_FORMAT,\
    DESTINATION_PORT_FORMAT, \
    LENGTH_FORMAT, \
    CHECKSUM_FORMAT, \
    METHOD_FORMAT, \
    GET_METHOD, \
    LIST_METHOD

IP_ADDRESS = "0.0.0.0"

# Create UDP socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
header_struct = struct.Struct(f"!{SOURCE_PORT_FORMAT}{DESTINATION_PORT_FORMAT}{LENGTH_FORMAT}{CHECKSUM_FORMAT}")
method_struct = struct.Struct(f"!{METHOD_FORMAT}")
server_port = DEFAULT_SERVER_PORT

def main(): 
    bind_socket()
    listen()
    print("Exiting...")
    server_socket.close()
    print("[*] Socket closed")

def bind_socket():
    global server_port
    while True: 
        try: 
            print(f"[*] Binding to port {server_port}...")
            server_socket.bind((IP_ADDRESS, server_port))
            print(f"[*] Successfully bound to port {server_port}")
            break
        except OSError: 
            print(f"[*] Port {DEFAULT_SERVER_PORT} is already in use. Trying another port...")
            server_port = server_port + 1
            continue

def listen(): 
    while True: 
        print(f"[*] Listening on port {DEFAULT_SERVER_PORT}...")

        data, addr = server_socket.recvfrom(BUFF_SIZE)
    
        print(len(data))
        print(f"[*] Request: {data}")
        print(f"[*] From: {addr[0]}:{addr[1]}")

        receive_request(data, addr)

def receive_request(data, addr): 
    source_port, destination_port, length, checksum = header_struct.unpack(data[:header_struct.size])
    
    print(f"[*] Source Port: {source_port}")
    print(f"[*] Destination Port: {destination_port}")
    print(f"[*] Length: {length}")
    print(f"[*] Checksum: {checksum}")

    response_data = handle_request(data[header_struct.size:], length, checksum).encode()
    send_response(response_data, addr, source_port)

# TODO: implementar logica procurar o arquivo e retornar o conteudo em chunks ou retornar codigo de erro caso nao exista
def handle_request(data, length, checksum):
    print(method_struct.unpack(data[:method_struct.size]))
    method = method_struct.unpack(data[:method_struct.size])[0]
    print(method.decode())
    
def send_response(data, addr, port):
    print(f"[*] Sending response to {addr[0]}:{port}")
    header = header_struct.pack(server_port, port, len(data) + 10, b"")
    server_socket.sendto(header + data, (addr[0], port))   



if __name__ == "__main__":
    main()