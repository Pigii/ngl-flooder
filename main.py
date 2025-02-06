import argparse
import os
import threading
import requests
import time

sent = 0
thread_count = 0
being_used = []
# A lock for safely modifying the proxies dictionary
proxy_lock = threading.Lock()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0",
    "Accept": "*/*",
    "Accept-Language": "en-US, en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://ngl.link",
    "DNT": "1",
    "Sec-GPC": "1",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Priority": "u=0",
    "TE": "trailers"
}

# Use a flag --use-proxies to enable proxies.
# By default proxies are disabled.
parser = argparse.ArgumentParser(
    prog='ngl-flooder',
    description='Floods ngl.link with a given text and user.',
    epilog='Example: python3 ngl-flooder -u "username" -m "Hello"'
)
parser.add_argument('-u', '--user', type=str, help='Target NGL user', required=True)
parser.add_argument('-m', '--message', type=str, help='Message to send', required=True)
parser.add_argument('-p', '--proxy', type=str, help='File containing HTTP proxies (used only with --use-proxies)', default='proxies.txt')
parser.add_argument('--use-proxies', action='store_true', help='Enable proxy usage (default is direct requests)')
parser.add_argument('-t', '--threads', type=int, help='Max number of threads', default=200)

def send_ngl(text: str, target: str, p: str) -> int:
    """Send a message to a target user using a proxy or directly.
    
    :param text: Message to send
    :param target: Target user
    :param p: Proxy (or None for direct request)
    :return: HTTP status code from the request
    """
    payload = (
        f"username={target}&question={text}"
        "&deviceId=2d2967e3-a19b-49bf-9a63-c3954a592d61"
        "&gameSlug=&referrer=https%3A%2F%2Fl.instagram.com%2F"
    )
    url = "https://ngl.link/api/submit"
    
    try:
        if p:
            r = requests.post(url, data=payload, headers=HEADERS,
                              proxies={"http": p, "https": p}, timeout=10)
        else:
            r = requests.post(url, data=payload, headers=HEADERS, timeout=10)
        return r.status_code
    except Exception as e:
        # Only print error messages when not using proxies.
        if not (p and args.use_proxies):
            print(f"Request failed: {e}")
        return 500

def send_ngl_thread(text: str, target: str, p: str) -> None:
    global sent, thread_count
    try:
        thread_count += 1
        being_used.append(p)
        
        # If proxies are not used, force p to None
        if not args.use_proxies:
            p = None
            
        status = send_ngl(text, target, p)
        
        if status == 200:
            sent += 1
        elif status == 429:
            # Rate limited: wait for a minute
            time.sleep(60)
        else:
            # If using proxies and the request was not successful,
            # increase the failure count and remove proxy if too many failures.
            if args.use_proxies and p:
                with proxy_lock:
                    if p in proxies:
                        proxies[p] += 1
                        if proxies[p] > 10:
                            del proxies[p]
                            
    except Exception as e:
        # Only print error messages when not using proxies.
        if not (p and args.use_proxies):
            print(f"Thread failed: {e}")
    finally:
        thread_count -= 1
        try:
            being_used.remove(p)
        except ValueError:
            pass  # In case p was not in the list

def print_thread() -> None:
    while True:
        os.system('cls||clear')
        print(f'User: {args.user}')
        print(f'Message: {args.message}')
        print(f'\nThread count: {thread_count}')
        elapsed = time.time() - start_time
        mps = round(sent / elapsed, 2) if elapsed > 0 else 0
        print(f'\nMessages sent: {sent}')
        print(f'Messages per second: {mps}')
        
        if args.use_proxies:
            with proxy_lock:
                total = len(proxies)
                timed_out = len([i for i in proxies.values() if i > 10])
            print(f'Loaded proxies: {total}')
            print(f'Proxies timed out: {timed_out}')
            
        print('\nPress CTRL+C to stop')
        time.sleep(1)

def main():
    while True:
        try:
            if not args.use_proxies:
                # Direct request mode: always spawn a thread with no proxy.
                p = None
                threading.Thread(target=send_ngl_thread, args=(args.message, args.user, p), daemon=True).start()
                time.sleep(0.1)
            else:
                # Using proxies: iterate over available proxies.
                with proxy_lock:
                    proxy_keys = list(proxies.keys())
                if not proxy_keys:
                    # If no proxies remain, wait before trying again.
                    time.sleep(1)
                    continue
                for proxy_str in proxy_keys:
                    # Limit the number of threads.
                    if thread_count < args.threads:
                        threading.Thread(target=send_ngl_thread, args=(args.message, args.user, proxy_str), daemon=True).start()
                    else:
                        time.sleep(0.1)
        except Exception as e:
            print(f"Main loop failed: {e}")

if __name__ == '__main__':
    args = parser.parse_args()
    
    if args.use_proxies:
        try:
            with open(args.proxy) as f:
                # Read each nonempty stripped line from the file.
                proxies = {line.strip(): 0 for line in f if line.strip()}
        except FileNotFoundError:
            print(f"Proxy file '{args.proxy}' not found. Using an empty proxy list.")
            proxies = {}
    else:
        proxies = {}  # Ensure no proxies are used when not enabled.
    
    start_time = time.time()
    threading.Thread(target=print_thread, daemon=True).start()
    
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopping...")
