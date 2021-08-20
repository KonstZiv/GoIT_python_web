import asyncio
from asyncio.tasks import sleep
import datetime
import socket

HOST = 'localhost'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)


users_dict = {}     # словарь пользователей системы:
# логин пользователя: пароль

# словарь который хранит все неотправленные сообщения:
messages_dict = {key: [] for key in users_dict}
# логин получателя (ключ): список объектов Message

actually_sockets = {}


class Message():
    # класс объектов сообщения, которые хранятся в списках значений словаря messades_dict
    def __init__(self, message, sender):
        self.message = message
        self.time = datetime.datetime.now().strftime('%d/%m  %H:%M:%S')
        self.sender = sender


async def autorisation(conn: socket, users_dict: dict):
    # функция автризации пользователя, вызывается при установлении соединения с клиентом
    # если от пользователя получен существующий логин и пароль - возвращает логин пользователяб
    # если получен неиспользуемый логин и нет пароля - предлагает ввести пароль и
    # зарегистрировать нового пользователя, в случае удачи - возвращает логин нового
    # пользователя во всех остальных слоцучаях возвращает None
    name, _, password = (await loop.sock_recv(conn, 1024)).decode().partition(':')
    print(f'получены: {name}, {password}')
    if name in users_dict and users_dict[name] == password:
        await loop.sock_sendall(conn,
                                f'You sent to server:\nname: {name}\npassword: {password}\nAccess is allowed.'.encode())

        return name
    elif name and not password:
        if name in users_dict:
            await loop.sock_sendall(conn,
                                    f'You sent to server:\nname: {name}\npassword: {password}\nThere is such user-name. Choose different user-name.'.encode())

        else:
            await loop.sock_sendall(conn,
                                    f'You sent to server:\nname: {name}\npassword: {password}\nName {name} is available. Enter password: '.encode())

            password = (await loop.sock_recv(conn, 1024)).decode()
            users_dict[name] = password
            messages_dict[name] = [Message('hello, new user!', 'server')]
            print(f'new user: {name}: {users_dict[name]}')
            return name


async def user_session(conn: socket, name: str):
    # принимает сокет и имя пользователя (name), в бесконечном цикле проверяет состояние
    # словаря сообщения messages_dict, если там появляется сообщение для name то читает его
    # (удаляя из словаря при этом) и отправляет получателю.

    async def user_session_send(conn: socket, name: str):
        # проверяет наличие сообщений в messages_dict для пользователя name и при наличии
        # отправляет их в сокет conn
        print(
            f"I'm in user_session_send {name}. Current messages_dict: {messages_dict}")
        if name:
            while True:
                if messages_dict.get(name):

                    for _ in range(len(messages_dict[name])):
                        asyncio.sleep(0.1)
                        message = messages_dict[name].pop()
                        await loop.sock_sendall(actually_sockets[name],
                                                f'at {message.time} from {message.sender}:  {message.message}'.encode())
                    print(
                        f"I'm in an END an user_session_send {name}. Current messages_dict: {messages_dict}")
                await asyncio.sleep(0.3)

    async def user_session_recv(conn: socket) -> tuple:
        # читает сообщение от пользователя, разбивает его на логин получателя и текст сообщения (по ":"),
        #  проверяет существование такого получателя в системе и наличие сообщения. Если существует -
        #  возвращает кортеж из имени получателя и текста сообщения, если какой-то из параметров Fase -
        # сообщаает об этом и дает возможность три раза ввести верный логин и сообщение. После этого -
        # возвращает кортех из двух None
        count = 0
        print(f'я в функции user_session_recive, {name}')
        while True:
            raw_message = (await loop.sock_recv(conn, 1024)).decode()
            name_to, _, message = raw_message.partition(':')
            name_to, message = name_to.strip(), message.strip()
            if (name_to in users_dict) and message != '':
                print(
                    f'name_to+message:\n for: {name_to}\nfrom: {name}\ntext:{message}')
                messages_dict[name_to].append(Message(message, name))
                print(f'writed message from {name} to {name_to}: {message}')
            elif not (name_to in users_dict):
                for key in users_dict:
                    print(
                        f'NOT name_to+message:\n for: {key}\nfrom: {name}\ntext:{message}')
                    messages_dict[key].append(Message(raw_message, name))
                    print(
                        f'writed message from {name} to {name_to}: {raw_message}')
            await asyncio.sleep(0.3)

    print(f"I'm in user_session name={name}")
    if name:
        actually_sockets[name] = conn
        loop.create_task(user_session_send(conn, name))
        loop.create_task(user_session_recv(conn))

    else:
        print('wrong name, close {conn}')
        loop.sock_sendall(conn,
                          f'wrong password passed for existing name {name}'.encode())
        conn.close()
        #!!!надо как-то снять задачу из цикла, если она сама не снимается по завершении!!!


async def run_server(s):
    while True:
        conn, _ = await loop.sock_accept(s)
        loop.create_task(user_session(
            conn, await autorisation(conn, users_dict)))


if __name__ == '__main__':
    users_dict = {}
    messages_dict = {}
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        s.setblocking(False)

        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(run_server(s))
        except KeyboardInterrupt:
            s.close()
