import socket
import json

HOST='localhost'
PORT = 7935

test_dict = {
        'first_name': 'jim',
        'last_name': 'heald',
        'age': 19
        }
json_data = json.dumps(test_dict)
json_bytes = str.encode(json_data)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # Bind the socket to host and port
    s.bind((HOST, PORT))
    # Will allow 1 unaccepted connection before refusing new connections
    s.listen(1)

    while True:
        # Conn is a new socket object that can send and recieve data
        conn, addr = s.accept()
        # Basically if there is a connection
        with conn:
            print('Connected by', addr)
            conn.sendall(json_bytes)

            # This would do something, not sure how it works
            # while True:
                # The 1024 is max data size allowed to be recieved
                # data = conn.recv(1024)
                # if not data: break
                # conn.sendall(b"What's up everyone?")

