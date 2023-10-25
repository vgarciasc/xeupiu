import socket
import time

def main():
    # Set the server address and port to match the display script
    server_address = ("127.0.0.1", 12345)

    try:
        # Create a socket connection to the display script
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(server_address)

        # Send sequential numbers and update the display every second
        count = 1
        while True:
            data = str(count)
            client_socket.send(data.encode('utf-8'))
            print("Sent:", data)
            time.sleep(1)
            count += 1

    except Exception as e:
        print("Error:", e)
    finally:
        client_socket.close()

if __name__ == "__main__":
    main()