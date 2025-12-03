import socket
import threading
from datetime import datetime

HOST = "0.0.0.0"
PORT = 5000

clients = {}  # socket -> username
users = []
PasswordProtected = False
server_password = "test"
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
# ---------------- USER-BROADCAST ---------------- #

def user_broadcast(message, user):
    """Send message to Single Client connected ."""
    try:
        user.send(message.encode())
    except:
        user.close()
        del clients[user]

# ---------------- HANDLE CLIENT ---------------- #

def handle_client(sock, addr):
    if PasswordProtected == True:
        sock.send("PasswordProtect".encode())
        if sock.recv(1024).decode().strip() != server_password:
            sock.send("[SERVER]Incorrect password. Connection closed.".encode())
            sock.close()
            return
        else:
            sock.send("[SERVER]Password accepted. Joining room.".encode())
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
            users.append(username)
            print(f"[+] {username} connected from {addr}")
            log_message("[:SERVER:]", f"**{username} connected from {addr} **")
            break

    # Listen for messages
    while True:
        try:
            msg = sock.recv(1024)
            if not msg:
                break
#Commands
            text = msg.decode().strip()
            if text == "//:list":
                user_broadcast(f"[Server]Current users are :-\n{users}\nIn total there are {len(users)}",sock)
            
#Normal            
            else:
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
    log_message("SERVER:", f"**{username} disconnected **")
    users.remove(username)
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
