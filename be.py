import socket
import sys

def start_backend_server(host='0.0.0.0', port=8081):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(5)
    print(f'Backend server listening on {host}:{port}')

    while True:
        conn, addr = sock.accept()
        data = conn.recv(1024)
        request_line = data.decode().split('\r\n')[0]
        method, path, _ = request_line.split()

        if path == '/health':
            response_body = 'OK'
            response = 'HTTP/1.1 200 OK\r\n'
            response += 'Content-Type: text/plain\r\n'
            response += f'Content-Length: {len(response_body)}\r\n'
            response += 'Connection: close\r\n'
            response += '\r\n'
            response += response_body
        else:
            response_body = 'Hello From Backend Server @port= '+str(port)
            response = 'HTTP/1.1 200 OK\r\n'
            response += 'Content-Type: text/plain\r\n'
            response += f'Content-Length: {len(response_body)}\r\n'
            response += 'Connection: close\r\n'
            response += '\r\n'
            response += response_body

        conn.sendall(response.encode('utf-8'))
        conn.close()

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8081
    start_backend_server(port=port)
