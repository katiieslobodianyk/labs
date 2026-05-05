import socket
import json
import sys

def send_request(req_dict):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(('localhost', 25002))
        sock.sendall(json.dumps(req_dict).encode())
        if req_dict.get('action') == 'bw_image':
            data = b''
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                data += chunk
            return data
        else:
            data = sock.recv(8192).decode()
            return json.loads(data)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'bw':
        req = req = {'action': 'bw_image', 'url': 'https://kor.ill.in.ua/m/1200x0/2824384.jpg'}
        img_bytes = send_request(req)
        with open('output_gray.jpg', 'wb') as f:
            f.write(img_bytes)
        print('Grayscale image saved as output_gray.jpg')
    else:
        req = {'action': 'fetch', 'url': 'https://example.com', 'regex': '<title>.*</title>'}
        resp = send_request(req)
        print('Headers:', resp['headers'])
        print('Matched lines:', resp['matched_lines'])
