import socket
import threading
import sys
import time
import requests

BACKEND_SERVERS = ["localhost:8081", "localhost:8082", "localhost:8083"]
NUM_SERVERS = 3
i = 0

def health_check(backend_servers, interval):
    while True:
        for server in list(backend_servers.keys()):
            try:
                response = requests.get(f'http://{server}/health')
                if response.status_code == 200:
                    backend_servers[server] = True  # Server is healthy
                else:
                    backend_servers[server] = False  # Server is unhealthy
            except requests.exceptions.RequestException:
                backend_servers[server] = False  # Connection failed

            print(f"Health Check: {server} - {'Healthy' if backend_servers[server] else 'Unhealthy'}")
        time.sleep(interval)

def handle_client(connection, client_address, backend_address):
    backend_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    backend_sock.connect(backend_address)
    print(f"Connected to backend server at {backend_address}")

    try:
        # Forward request from client to backend server
        client_data = connection.recv(1024)
        if client_data:
            print(f"Received from client:\n{client_data.decode()}")
            backend_sock.sendall(client_data)

        # Receive full response from backend
        response_data = b''
        while True:
            backend_data = backend_sock.recv(1024)
            if not backend_data:
                break
            response_data += backend_data
            print(f"Received from backend:\n{backend_data.decode()}")

        connection.sendall(response_data)
        print("Response sent to client")

    finally:
        backend_sock.close()
        connection.close()

def start_load_balancer(host='0.0.0.0', port=8080, interval=10):
    backend_servers = {server: True for server in BACKEND_SERVERS}
    health_thread = threading.Thread(target=health_check, args=(backend_servers, interval))
    health_thread.start()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(5)
    print(f'Load balancer listening on {host}:{port}')

    while True:
        conn, addr = sock.accept()
        print(f"New connection from {addr}")

        servers = [(server, healthy) for server, healthy in backend_servers.items()]

        global i
        server = ""
        j = 0
        for _ in range(NUM_SERVERS):
            server = servers[i]  # Simple round-robin selection
            i = (i + 1) % NUM_SERVERS
            if server[1]:
                break
            j = j + 1

        if (j == NUM_SERVERS):
            print("No available servers")
            conn.close()
            continue
            
        backend_host, backend_port = server[0].split(':')

        print(backend_host, backend_port)

        client_thread = threading.Thread(target=handle_client, args=(conn, addr, (backend_host, int(backend_port))))
        client_thread.start()

if __name__ == '__main__':
    interval = int(sys.argv[1]) if len(sys.argv) > 1 else 10  # Default to 30 seconds if not specified
    start_load_balancer(interval=interval)