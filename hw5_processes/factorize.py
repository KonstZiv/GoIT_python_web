from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Process, Pool
import time


def factorize_singl(*number) -> tuple:
    # gets integers in an iterable object, finds for them all existing integer divisors \
    # which it returns in the lists placed in a tuple (the sequence of results corresponds\
    # to the sequence of initial numbers in the function argument)
    # Important! The function uses the most inefficient integer divisor search algorithm. \
    # The task of this program is to investigate the efficiency of multiprocessing with \
    # "CPU-bound" code.
    return tuple([x for x in range(1, num + 1) if num % x == 0] for num in number)


MAX_PROCESS = 6  # maximum number of process


if __name__ == "__main__":
    # collection of original numbers. Important! For a clear observation of the \
    # efficiency of multiprocessing, use approximately the same number in the list
    number = (12345678, 90876543, 10009876, 87651234,
              34566543, 12340987, 23450987, 98761234)
    # singl procecc mode
    start = time.time()
    res = factorize_singl(*number)
    duration = time.time() - start
    print(f'time result of singl process: {duration}\n {"-" * 80}')
# --------------------------------------------------------------------------------------------------
    # multiprocess mode - ProcessPoolExecutor

    print('Use ProcessPoolExecutor: ')
    for process in range(1, MAX_PROCESS + 1):
        start_multi = time.time()
        with ProcessPoolExecutor(process) as executor:
            res = zip(number, executor.map(factorize_singl, number))

        duration = time.time() - start_multi
        print(f'for {process} process computation time is {duration}')
    print(f'{"-" * 80}')

# --------------------------------------------------------------------------------------------------
    # multiprocess mode - Process
    print('Use multiprocessing.Process (start one Process for each number in task): ')
    start_Process = time.time()
    proсesses = []
    for i, num in enumerate(number):
        proсesses.append(Process(target=factorize_singl, args=(num, )))
        proсesses[i].start()
    for elem in proсesses:
        elem.join()
    duration_Process = time.time() - start_Process
    print(f'for {len(proсesses)} Process time is {duration_Process}')
    print(f'{"-" * 80}')

# --------------------------------------------------------------------------------------------------
    # multiprocess mode - Pool
    print(f'Use multiprocess.Pool 1...{MAX_PROCESS} processes:')
    for process in range(1, MAX_PROCESS + 1):
        start_multi_Pool = time.time()
        with Pool(process) as pool:
            res = zip(number, pool.map(factorize_singl, number))

        duration = time.time() - start_multi_Pool
        print(f'for {process} process computation time is {duration}')
    print(f'{"-" * 80}')

# --------------------------------------------------------------------------------------------------
    print('final divisor lists')
    for num, dividers in res:
        print(f'number: {num} dividers: {dividers}')
