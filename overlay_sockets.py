import threading
import tkinter as tk
import socket

class DisplayWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Display Window")

        self.label = tk.Label(self.root, text="", font=("Arial", 16))
        self.label.pack(expand=True, fill='both')

    def update_display_text(self, new_text):
        self.label.config(text=new_text)

    def start(self):
        self.root.mainloop()

def receive_and_update_display(display, conn):
    while True:
        try:
            data = conn.recv(1024).decode('utf-8')
            if not data:
                break
            display.root.after(0, display.update_display_text, data)  # Use after to update the GUI
        except ConnectionAbortedError:
            break
    conn.close()

if __name__ == "__main__":
    display_root = tk.Tk()
    display = DisplayWindow(display_root)
    display_process = threading.Thread(target=display.start)  # Use the threading module
    display_process.daemon = True
    display_process.start()

    # Set up a socket server for receiving text updates from the translation process
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("127.0.0.1", 12345))
    server_socket.listen(1)

    print("Waiting for connections...")
    conn, addr = server_socket.accept()
    print("Connected by", addr)

    update_display_text(display, conn)