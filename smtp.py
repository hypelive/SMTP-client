import socket

address = 'smtp.gmail.com'
port = 587

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((address, port))
    s.settimeout(2)
    print(s.recv(1024).decode().strip())
    while True:
        message = input() + '\r\n'
        if message.startswith('exit'):
            exit(0)
        s.send(message.encode())
        try:
            while True:
                responce = s.recv(1024).decode()
                if responce:
                    print(responce.strip())
        except socket.timeout:
            pass