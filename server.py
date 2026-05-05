import socket
import json
import requests
import re
import cv2
import numpy as np

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('localhost', 25002))
sock.listen(5)
print('Server listening on port 25002')

while True:
    conn, addr = sock.accept()
    data = conn.recv(8192).decode()
    req = json.loads(data)
    action = req['action']

    if action == 'fetch':
        url = req['url']
        regex = req.get('regex')
        resp = requests.get(url)
        headers = dict(resp.headers)
        text = resp.text
        lines = text.splitlines()
        matched = []
        if regex:
            pattern = re.compile(regex)
            for line in lines:
                if pattern.search(line):
                    matched.append(line)
        result = {'headers': headers, 'matched_lines': matched[:100]}
        conn.sendall(json.dumps(result).encode())

    elif action == 'bw_image':
        url = req['url']
        img_resp = requests.get(url)
        img_array = np.frombuffer(img_resp.content, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, encoded = cv2.imencode('.jpg', gray)
        conn.sendall(encoded.tobytes())

    conn.close()
