import socket
import threading
from datetime import datetime

HOST = "0.0.0.0"
PORT = 5000

clients = {}  # socket -> username


# ---------------- LOGGING ---------------- #

def get_log_filename():
    return "Log" + datetime.now().strftime("%Y-%m-%d") + ".txt"

def log_message(username, message):
    filename = get_log_filename()
    timestamp = datetime.now().strftime("%H:%M:%S")
    entry = f"[{timestamp}] {username}: {message}\n"

    with open(filename, "a", encoding="utf-8") as f:
        f.write(entry)


# ---------------- BROADCAST ---------------- #

def broadcast(message, sender_socket=None):
    """Send message to all connected clients."""
    for client in list(clients.keys()):
        if client != sender_socket:
            try:
                client.send(message.encode())
            except:
                client.close()
                del clients[client]


# ---------------- HANDLE CLIENT ---------------- #

def handle_client(sock, addr):
    # Ask for username
    sock.send("Enter username: ".encode())

    while True:
        username = sock.recv(1024).decode().strip()

        if username in clients.values():
            sock.send("Username already taken. Try another: ".encode())
        elif len(username) == 0:
            sock.send("Invalid username. Try again: ".encode())
        else:
            clients[sock] = username
            sock.send(f"Welcome, {username}!\n".encode())
            broadcast(f"** {username} has joined the chat **", sock)
            print(f"[+] {username} connected from {addr}")
            break

    # Listen for messages
    while True:
        try:
            msg = sock.recv(1024)
            if not msg:
                break

            text = msg.decode().strip()
            formatted = f"{username}: {text}"

            # Print to server console
            print(formatted)

            # Log to file
            log_message(username, text)

            # Send to other clients
            broadcast(formatted, sock)

        except:
            break

    # Handle disconnect
    print(f"[-] {username} disconnected")
    broadcast(f"** {username} has left the chat **", sock)
    del clients[sock]
    sock.close()


# ---------------- MAIN ---------------- #

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(10)

    print(f"Server running on {HOST}:{PORT}")

    while True:
        client_socket, addr = server.accept()
        threading.Thread(target=handle_client, args=(client_socket, addr), daemon=True).start()


if __name__ == "__main__":
    main()
