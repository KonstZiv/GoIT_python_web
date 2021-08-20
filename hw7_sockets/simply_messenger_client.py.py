import asyncio
import socket
import sys

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432        # The port used by the server


def shotdown():
    # гасим все задачи кроме основной
    print('it is shutdown')
    for task in asyncio.all_tasks():
        if task is not asyncio.current_task():
            task.cancel(f'task {task} is cancelled')


def help():
    help = '''
    тут должна быть подсказка по запуску и пользованию клиентом'''
    return help


async def client_recv():
    while True:
        in_message = await loop.sock_recv(s, 1024)
        print(
            f'--->> \033[4;37;45mrecive:{in_message.decode()}\033[0m')


async def client_send():
    # Ждём действия от пользователя
    while True:
        # Запускаем input() в отдельном потоке и ждём его завершения
        message_for_send = await asyncio.to_thread(input)
        if message_for_send:
            await loop.sock_sendall(s, message_for_send.encode())
            print(f'send: {message_for_send}')


async def main():
    pass


if __name__ == '__main__':
    if 1 < len(sys.argv) < 4:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            if len(sys.argv) == 3:
                login = sys.argv[1]
                password = sys.argv[2]
                s.sendall(f'{login}:{password}'.encode())
            else:
                login = sys.argv[1]
                password = ''
                s.sendall(f'{login}:{password}'.encode())
                server_answer = s.recv(1024)
                print(str(server_answer.decode()))
                password_for_new_login = input('>>')
                s.sendall(password_for_new_login.encode())

            # связываем обработчик Ctrl+C
            #signal.signal(signal.SIGINT, shotdown())
            loop = asyncio.get_event_loop()
            main_task = asyncio.wait([client_recv(), client_send()])
            try:
                loop.run_until_complete(main_task)
            except asyncio.CancelledError:
                loop.run_until_complete(main_task)

    print(help())
