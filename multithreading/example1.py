import time
import requests
from threading import Thread

SYMBOLS = ('USD', 'EUR', 'UAH', 'RUB', 'GEL')
BASES = ('USD', 'EUR', 'UAH', 'RUB', 'GEL')


def fetch_rates(base):
    response = requests.get(
        f"https://v6.exchangerate-api.com/v6/8acdaf3c53445751d9c11943/latest/{base}"
    )
    response.raise_for_status()
    rates = response.json()["conversion_rates"]
    rates[base] = 1.
    rates_line = ", ".join(
        [f"{rates[symbol]:7.03} {symbol}" for symbol in SYMBOLS]
    )
    print(f"1 {base} = {rates_line}")


def main():
    # for base in BASES:
    #    fetch_rates(base)

    threads = [Thread(target=fetch_rates, args=(base,)) for base in BASES]
    print('start all')
    for thread in threads:
        thread.start()


if __name__ == "__main__":
    started = time.time()
    main()
    elapsed = time.time() - started
    print()
    print("Времени затрачено: {:.2f}s".format(elapsed))
