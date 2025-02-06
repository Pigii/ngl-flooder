# NGL Flooder

A simple tool to flood [ngl.link](https://ngl.link) with messages using direct requests or proxies.

## Usage

- **Direct Mode (default):**  
  ```bash
  python3 flooder.py -u "username" -m "Your message here"
  ```
- Proxy Mode:
  ```bash
  python3 flooder.py -u "username" -m "Your message here" --use-proxies -p proxies.txt
  ```
- Additional Options:
  Use `-t` to set the maximum number of threads (default is 200).

  Press `CTRL+C` to stop.
