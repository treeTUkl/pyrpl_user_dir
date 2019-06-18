import socket
import sys
import time


class client():

    def __init__(self, host, port):
        self.sock = 0
        self.HOST = host
        self.PORT = port
        self.connect()

    def connect(self):
        if self.sock == 0:
            # HOST = 'localhost'
            # PORT = 54545
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                # self.sock.setblocking(0)
                self.sock.connect((self.HOST, self.PORT))
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
                        self.sock = 0
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
            message = message.decode()
            # reciveing
            if not message == "close":
                data = self.sock.recv(16)
                data = data.decode()
                print('received: ', data)

            elif message == " ":
                print('nothing received.\nseems to be an error on server')
                self.sock.close()

            elif message == "close":
                print('\nclosing socket')
                self.sock.close()
            return data

    def close(self):
        print('closing socket')
        self.send("close")


def diodenmessung(pyrplclient, bnc1o2):

    volt = False
    if bnc1o2 == "bnc1":
        volt = "voltage1"
    elif bnc1o2 == "bnc2":
        volt = "voltage2"
    else:
        print("\nKein gültiger Anschluß am redpitaya gewählt! Wählen Sie bnc1 oder bnc1")
        return False
    if not volt:
        print('\nSpannungsmessung an: ' + bnc1o2)
        diodendata = 0.0
        for i in range(10):
            diodendata = diodendata + pyrplclient.send(volt)
            time.sleep(.5)
        return diodendata / 10


if __name__ == "__main__":  # TODO:debug this
    pyrplclient = client('localhost', 54545)  # pyrpl_client läuft local auf dem selben rechner.
    #   standaclient= client('127.127.127.2', 22222)#standa_client über ssh auf redpitaya
    # standa_freie suche:
    # besser ne vernünftige control machen
    #    standaclient.send("LMOVE")
    #    time.sleep(1)
    #    standaclient.send("STOPMOVE")  # stops with deceleration speed
    #    standaclient.send("POS")
    #    standaclient.send("RMOVE")
    #    standaclient.send("STOPMOVE")#stops with deceleration speed
    #    standaclient.send("POS")
    #    standaclient.send("POS")
    #    standaclient.send("POS")
    #    standaclient.send("STOPFAST")#immediatley stop engine
    #    standaclient.send("POS")
    #    standaclient.send("POS")
    #    standaclient.send("POS")

    # messung ala :
    #    standaclient.send("POS")
    #    standaclient.send("GOH")
    #    standaclient.send("POS")
    #    standaclient.send("MOV6000")

    pyrplclient.send("voltage1")
    #    standaclient.send("MOR1000")
    diodenmessung(pyrplclient, 'bnc1')

    #    standaclient.send("MOR1000")
    diodenmessung(pyrplclient, 'bnc2')

    #    standaclient.colse()
    pyrplclient.close()
    print("finish")
