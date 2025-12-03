import socket
import threading

SERVER = "YOURIP" 
PORT = 5000
PASSWORD = "YOURPASSWORD"  

def listen(sock):
    while True:
        try:
            msg = sock.recv(1024).decode()
            if not msg:
                print("Disconnected from server.")
                break
            
            print(msg)  # Print server message

            # Automatically send password if server asks for it
            if "PasswordProtect" in msg:
                print("THIS SERVER IS PASSWORD PROTECTED, SENDING PASSWORD")
                sock.send(PASSWORD.encode())

        except Exception as e:
            print("Error:", e)
            break

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER, PORT))

    # Start listening thread
    threading.Thread(target=listen, args=(sock,), daemon=True).start()

    while True:
        try:
            message = input()
            if message.lower() == "//:quit":
                print("Exiting...")
                break
            sock.send(message.encode())
        except Exception as e:
            print("Error:", e)
            break

if __name__ == "__main__":
    main()
