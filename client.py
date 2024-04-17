import os
import socket
import struct
from zlib import crc32
from constants import DEFAULT_SERVER_PORT,\
    DEFAULT_CLIENT_PORT, RESPONSE_NOT_FOUND, RESPONSE_OK, RESPONSE_CHUNK, RESPONSE_ERROR,\
    BUFF_SIZE, GET_METHOD, \
    SOURCE_PORT_FORMAT,\
    DESTINATION_PORT_FORMAT, \
    LENGTH_FORMAT, \
    CHECKSUM_FORMAT, \
    GET_METHOD, \
    LIST_METHOD

IP_ADDRESS = "127.0.0.1"

server_IP_address = IP_ADDRESS
server_port = DEFAULT_SERVER_PORT
client_port = DEFAULT_CLIENT_PORT

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.settimeout(5)
header_struct = struct.Struct(f"!{SOURCE_PORT_FORMAT}{DESTINATION_PORT_FORMAT}{LENGTH_FORMAT}{CHECKSUM_FORMAT}")
method_struct = struct.Struct(f"!4s")

def main(): 
    bind_socket()
    set_server_address()
    select_action()
    print("Exiting...")
    client_socket.close()
    print("[*] Socket closed")

def bind_socket():
    global client_port
    while True: 
        try: 
            print(f"[*] Binding to port {client_port}...")
            client_socket.bind((IP_ADDRESS, client_port))
            print(f"[*] Successfully bound to port {client_port}")
            break
        except OSError: 
            print(f"[*] Port {DEFAULT_CLIENT_PORT} is already in use. Trying another port...")
            client_port = client_port + 1
            continue

def set_server_address(): 
    global server_IP_address
    global server_port

    IP_address = input(f"Enter server IP address (default {IP_ADDRESS}): ")
    port = input(f"Enter server port (default {DEFAULT_SERVER_PORT}): ")

    if IP_address.strip() != "":
        server_IP_address = IP_address
    if port.strip() != "":
        server_port = int(port)
    
    print(f"[*] Server set to: {server_IP_address}:{server_port}")

def select_action():
    while True:
        action = input("What would you like to do? (0 - exit, 1 - send request): ")
        if action == "0":
            break
        elif action == "1":
            print("Available request formats:")
            print("Get file: GET <file_name.extension>")
            request = input("Enter request: ")
            send_request(request)
        else:
            print("Invalid action. Please try again.")
            continue
        
def send_request(request):
    global client_port
    global server_port
    global server_IP_address
    request_method, request_filename = request.split(" ")
    print (request_method.encode())
    if request_method.replace("\x00", "") == GET_METHOD:
        
        method = method_struct.pack(request_method.encode())
        request = method + request_filename.encode()
        checksum = crc32(request)
        header = header_struct.pack(client_port, server_port, len(request) + 10, checksum)
        print(server_IP_address, server_port)
        client_socket.sendto(header + request, (server_IP_address, server_port))
        listen_to_response(request_filename)
    else:
        print("Invalid request format. Please try again.")
        return

# TODO: verificar checksum, tratar codigos de erro, salvar resposta em arquivo, 
# implementar opcao de descartar pacotes
def listen_to_response(filename):
    try:
        with open('copy_' + filename, "wb") as newFile:
            expected_chunk_id = 1
            while True:
                print(f"[*] Waiting for chunk {expected_chunk_id}...")
                data, addr = client_socket.recvfrom(BUFF_SIZE)
                source_port, dest_port, length, checksum = header_struct.unpack(data[:header_struct.size])
                code, chunk_id = struct.unpack("!HH", data[header_struct.size:header_struct.size + 4])
                payload = data[header_struct.size + 4:]

                calculated = crc32(data[header_struct.size:])
                print(f"Checksum: {checksum}")
                print(f"Calculated: {calculated}")
                print(f"Code: {code}")
                print(f"ID: {chunk_id}")
                if payload == b"":
                    break
                print(code == RESPONSE_OK)
                print(chunk_id == expected_chunk_id)
                if code == RESPONSE_OK and chunk_id == expected_chunk_id:
                    print(f"[*] Chunk {chunk_id} received.")
                    newFile.write(payload)
                    expected_chunk_id += 1
                    # Enviar confirmação ao servidor
                    client_socket.sendto(b"ACK", (server_IP_address, server_port))
                else:
                    print("[*] Invalid chunk received. Resending ACK.")
                    # Reenviar a confirmação ao servidor
                    client_socket.sendto(b"ACK", (server_IP_address, server_port))
    except socket.timeout as e:
        os.rename('temp_' + filename, 'corrupted_' + filename)
        return
    except Exception as e:
        print(f"[*] Error: {e}")
        return

def arrayToByteString(file):
    result = b""
    for value in file:
        result += value["data"]
    return result

if __name__ == "__main__":
    main()