from threading import Thread
from time import sleep


class MyThread(Thread):

    def __init__(self, second_num, name=None):
        super().__init__(name=name)
        self.delay = second_num

    def run(self):
        sleep(self.delay)
        print(f'wake up! {self.name}')


def another_thread(second_num, name):
    print(f'I`m started. My name {name}')
    sleep(second_num)
    print(f'I`m finished. My  name {name}')


if __name__ == '__main__':
    threads = [Thread(target=another_thread, args=(2, i)) for i in range(3)]
    print('start all')
    for thread in threads:
        thread.start()
