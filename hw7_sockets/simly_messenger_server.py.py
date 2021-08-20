import asyncio
import signal
import socket
import sys


HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432        # The port used by the server

# создаем список в который будут помещаться все сообщения которые нужно отправить
local_send_message_list = []
local_output_list = []


def shotdown():
    # гасим все задачи кроме основной
    print('it is shutdown')
    for task in asyncio.all_tasks():
        if task is not asyncio.current_task():
            task.cancel(f'task {task} is cancelled')


async def user_io():
    # Ждём действия от пользователя
    while True:
        # Запускаем input() в отдельном потоке и ждём его завершения
        command = await asyncio.to_thread(input, 'input message: ')
        if command:
            local_send_message_list.append(command)
            print(local_send_message_list)


async def message_handler():
    if len(sys.argv) == 3:
        login = sys.argv[1]
        password = sys.argv[2]
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            await loop.sock_sendall(s, f'{login}:{password}'.encode())
            while True:
                local_output_list.append((await loop.sock_recv(s, 1024)).decode())
                await user_output()
                if local_send_message_list:
                    for _ in len(local_send_message_list):
                        await loop.sock_sendall(s, local_send_message_list.pop().encode())
    elif len(sys.argv) == 2:
        login = sys.argv[1]
        password = ''
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            await loop.sock_sendall(s, f'{login}:{password}'.encode())
            print(str((await loop.sock_recv(s, 1024)).decode()))
            s.sendall(input('>>').encode())
            print('password recived')
            while True:
                #print('I`m in loop')
                # data = (await loop.sock_recv(s, 1024))
                #print('Received', repr(data.decode()))
                if local_send_message_list:
                    for i in range(len(local_send_message_list)):
                        print(local_send_message_list)
                        await loop.sock_sendall(s, local_send_message_list.pop().encode())
                        print(f'after send {local_send_message_list}')
    else:
        print('when starting the client, specify your username and password (if you are registered in the system) or just the username otherwise')

if __name__ == '__main__':
    # связываем обработчик Ctrl+C
    #signal.signal(signal.SIGINT, shotdown())

    # стартуем цикл событий
    loop = asyncio.get_event_loop()

    # формируем главную задачу которая содержит в себе обработчик и ввод в другом поиттоке
    main_task = asyncio.wait([user_io(), message_handler()])
    try:
        loop.run_until_complete(main_task)
    except asyncio.CancelledError:
        loop.run_until_complete(main_task)
    print('stop client')
