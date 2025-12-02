import socket
import threading

SERVER = "YOUR.SERVER.IP"
PORT = 5000

def listen(sock):
    while True:
        try:
            msg = sock.recv(1024).decode()
            if not msg:
                break
            print(msg)
        except:
            print("Disconnected from server.")
            break

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER, PORT))

    threading.Thread(target=listen, args=(sock,), daemon=True).start()

    while True:
        message = input("")
        sock.send(message.encode())

if __name__ == "__main__":
    main()
