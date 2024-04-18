import socket
import struct
import os
from urllib import response
from zlib import crc32
from constants import DEFAULT_SERVER_PORT,\
    BUFF_SIZE, RESPONSE_NOT_FOUND, RESPONSE_OK, RESPONSE_CHUNK, RESPONSE_ERROR,\
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
response_code_struct = struct.Struct(f"!3s")
chunk_id_struct = struct.Struct(f"!H")
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

    handle_request(data[header_struct.size:], length, checksum, source_port, addr[0])

# TODO: implementar logica procurar o arquivo e retornar o conteudo em chunks 
# ou retornar codigo de erro caso nao exista
def handle_request(payload, length, checksum, destination_port, destination_ip):
    data = payload[method_struct.size:].decode()
    method = method_struct.unpack(payload[:method_struct.size])[0].decode()

    if method.replace('\x00', '') == GET_METHOD:
        print(f"[*] GET request for file: {data}")
        try:
            chunk_id = 1
            with open(data, "rb") as file:
                while True:
                    chunk = file.read(BUFF_SIZE - header_struct.size - response_code_struct.size - chunk_id_struct.size)
                    if not chunk:
                        size = header_struct.size + response_code_struct.size + chunk_id_struct.size
                        message = struct.pack("!HH", 200, chunk_id) + b""
                        checksum = crc32(message)
                        header = struct.pack("!HHHI", server_port, destination_port, size, checksum)
                        response = header + message 
                        server_socket.sendto(response, (destination_ip, destination_port))
                        break
                    print(chunk_id)
                    size = header_struct.size + response_code_struct.size + chunk_id_struct.size + len(chunk)
                    message = struct.pack("!HH", 200, chunk_id) + chunk
                    checksum = crc32(message)
                    header = struct.pack("!HHHI", server_port, destination_port, size, checksum)
                    response = header + message
                    server_socket.sendto(response, (destination_ip, destination_port))
                    chunk_id = chunk_id + 1
        except FileNotFoundError:
            response_data = b"File not found"
            size = header_struct.size + response_code_struct.size + len(response_data)
            message = struct.pack("!HH", 404, chunk_id) + response_data
            checksum = crc32(message)
            header = struct.pack("!HHHI", server_port, destination_port, size, checksum)
            response = header + message
            server_socket.sendto(response, (destination_ip, destination_port))
        # except Exception: 
        #     response_data = b"Internal server error"
        #     size = header_struct.size + response_code_struct.size + len(response_data)
        #     response_headers = header_struct.pack(server_port, destination_port, size, crc32(response_data))
            
    
    
def send_response(data, addr, port, size, chunk_id):
    print(f"[*] Sending response to {addr[0]}:{port}")
    packet = header_struct.pack(server_port, port, size, b"")
    server_socket.sendto(packet + chunk_id + data, (addr, port))


if __name__ == "__main__":
    main()