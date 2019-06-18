import socket
import sys


class pyrplclient:

    def __init__(self):
        self.sock = 0
        self.connect()

    def connect(self):
        if self.sock == 0:
            HOST = 'localhost'
            PORT = 54545
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                # self.sock.setblocking(0)
                self.sock.connect((HOST, PORT))
                print('connected to server')

            except ConnectionRefusedError:
                print('ConnectionRefused! Server might not ready')
                i = 0
                while i == 0:
                    q = input(
                        "Do you want to try again? (Y/N)")
                    if q == "N" or q == "n":
                        print("stopping....")
                        i = 1
                        self.sock.close()
                        sys.exit()
                    elif q == "Y" or q == "y":
                        print("then, keep runnig.")
                        self.sock=0
                        self.connect()
                        i = 1
                    else:
                        print("Invalid answer. Try again.")

    def send(self, message):
        if self.sock == 0:
            print('no socked, try connect first..')
        else:
            # Send data
            print('sending:' + message)
            message = message.encode()
            self.sock.sendall(message)
            message= message.decode()
            # reciveing
            if not message == "close":
                data = self.sock.recv(16)
                data = data.decode()
                print('received: ', data)

            elif message ==" ":
                print('nothing received.\nseems to be an error on server')
                self.sock.close()

            elif message == "close":
                print('\nclosing socket')
                self.sock.close()

    def close(self):
        print('closing socket')
        self.send("close")


if __name__ == "__main__":
    c = pyrplclient()
    c.send("voltage2")
    c.send("voltage1")
    c.close()
    print("finish")
