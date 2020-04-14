import socket
import ssl
import base64

GMAIL_SMTP = 'smtp.gmail.com'

class ResponseException(Exception):
    WRONG_RESPONSE = "found unexpected response:\n"

    def __init__(self, resp):
        self.text = self.WRONG_RESPONSE + resp

def main():
    port = 587
    context = ssl.create_default_context()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(2)
        sock.connect((GMAIL_SMTP, port))
        check_responce(2, sock)
        request_start_ssl(sock)
        with context.wrap_socket(sock, server_hostname=GMAIL_SMTP) as ssock:
            while not login(ssock):
                pass
            while True:
                try:
                    message = input('введите имя файла, который хотите отправить (для выхода введите \'Q\'): ')
                    if message == 'Q':
                        exit(0)
                    with open(message, 'r') as file:
                        messageData = file.read()
                        send_message(messageData, ssock)
                except socket.timeout:
                    pass
                except ResponseException as e:
                    print(e.text)
                except FileNotFoundError:
                    print('неверное имя файла')

def request_start_ssl(sock):
    sock.send('EHLO smtp.korobeynikov.nikolay\r\n'.encode())
    check_responce(2, sock)
    sock.send('STARTTLS\r\n'.encode())
    check_responce(2, sock)

def login(sock):
    print('пройдите авторизацию на gmail сервере')
    sock.send('AUTH LOGIN\r\n'.encode())
    check_responce(3, sock)
    login = input('адрес электронной почты для авторизации: ')
    sock.send(base64.standard_b64encode(login.encode()) + '\r\n'.encode())
    check_responce(3, sock)
    password = input('пароль для авторизации: ')
    sock.send(base64.standard_b64encode(password.encode()) + '\r\n'.encode())
    try:
        check_responce(2, sock)
    except ResponseException:
        print('неверные данные для авторизации')
        return False
    print('авторизация успешно пройдена')
    return True

def send_message(messageData, sock):
    sock.send(f'MAIL FROM: <{input("какой адрес указать в качестве отправителя?: ")}>\r\n'.encode())
    check_responce(2, sock)
    recievers = input("какой адрес указать в качестве получателя? (можно указать несколько через \',\'): ").split(',')
    for reciever in recievers:
        sock.send(f'rcpt to: <{reciever.strip()}>\r\n'.encode())
        check_responce(2, sock)
    sock.send('DATA\r\n'.encode())
    check_responce(3, sock)
    sock.send((messageData + '\r\n.\r\n').encode())
    check_responce(2, sock)
    print('письмо отправлено')

def check_responce(number: int, sock):
    response = sock.recv(1024).decode().strip()
    if not response.startswith(str(number)):
        raise ResponseException(response)
    return response

if __name__ == '__main__':
    main()