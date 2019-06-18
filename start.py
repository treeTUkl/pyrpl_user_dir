from pyrpl import pyrpl
from pyrpl import sshshell
import socket
import sys



class pyrplserver(object):

    def __init__(self, p=None):
        self.connection = False
        self.client_address = 0
        self.mypyrpl = p
        self.data= None
        self.sock = 0
        if self.mypyrpl is None:
            print("WARNING: No pyrpl, going to fake mode...")

    def client_connect(self):
        if not self.connection:
            try:
                # jetzt auf ip tcp hören und voltage schicken

                """This sample program, based on the one in the standard library documentation, receives incoming messages and echos them back to the sender. It starts by creating a TCP/IP socket."""
                # Create a TCP/IP socket
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                """Pyrpl verbindet sich auf Redpitaya über Ip + Port 2222
                    Pyrpl verwendet als kumminikation ssh mit dem Port 22
                    Port Freiwählbar also 54545"""
                LOCALHOST = 'localhost'
                PORT = 54545

                """ Then bind() is used to associate the socket with the server address. In this case, the address is localhost, referring to the current server, and the port number is 10000."""
                # sock.setblocking(0)
                # Bind the socket to the port
                server_address = (LOCALHOST, PORT)
                print('starting up on %s port %s' % server_address)
                self.sock.bind(server_address)
                self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                """Calling listen() puts the socket into server mode, and accept() waits for an incoming connection."""
                # Listen for incoming connections
                self.sock.listen(1)
                print("Server started")
                print("Server listening...")
                print("Waiting for client request..")
                # Wait for a connection
                print('waiting for a connection')
                self.connection, self.client_address = self.sock.accept()
                print('connection from', self.client_address)
                print('read_connection')
                self.read_connection()
            except OSError:
                print('OS Error catched')

    def client_close(self):
        # Clean up the connection
        print('closing')
        self.sock.close()
        self.connection = False
        self.client_address = 0
        self.sock = 0
        #kill all
        sys.exit()
    def read_connection(self):
        if not self.connection == False:
            while self.connection:
                """accept() returns an open connection between the server and client, along with the address of the client.
                 The connection is actually a different socket on another port (assigned by the kernel).
                  Data is read from the connection with recv() and transmitted with sendall()."""
                try:
                    # Receive the data in small chunks and retransmit it

                    self.data = self.connection.recv(16)  # we might need more than 4? but labview sagt 4

                    print('received "%s"' % self.data)
                    self.data = self.data.decode() #TODO # might not needed if data ist already in string format

                    if self.data[:] == "voltage1":
                        if self.mypyrpl is not None:
                            voltage1 = self.mypyrpl.rp.scope.voltage_in1
                        else:
                            voltage1 = 1.5
                            print("WARNING: No pyrpl connected, reading fake value!!!")
                        voltage1 = str(voltage1)
                        print('voltage1: ' + voltage1)
                        print('sending data back to the client')
                        self.connection.sendall(voltage1.encode())
                        self.data = ""
                    elif self.data[:] == "voltage2":
                        if self.mypyrpl is not None:
                            voltage2 = self.mypyrpl.rp.scope.voltage_in2
                        else:
                            voltage2 = -2
                            print("WARNING: No pyrpl connected, reading fake value!!!")

                        voltage2=str(voltage2)
                        print('voltage2 ' + voltage2)
                        print('sending data back to the client')
                        self.connection.sendall(voltage2.encode())
                        self.data = ""
                    elif self.data[:] == "close":
                        print('close received')
                        self.client_close()
                        break
                    elif self.data[:] == '':
                        print('no data..  keep reading')
                    else:
                        print('got strange self.data' + self.data + 'do nothing with it')
                        self.data = ""
                except socket.error:
                    print("Error Occured")
                    break
            if not self.data == "close":
                self.client_close()


if __name__ == "__main__":
    sshshell.paramiko.util.log_to_file("paramikologsit.log")
    p = pyrpl.Pyrpl(config='test19_05_03')
    p.lockbox.classname = "AG_Lockbox"
    #Auskommentierte Zeilen werden über die Config abgearbeitet, daher kommentiert lassen!
    # p.lockbox.is_locked_threshold = 0.04
    # p.lockbox.signals.pop('piezo').sweep_frequency=2.5
    # p.lockbox.signals.pop('piezo').sweep_amplitude=0.2
    # p.lockbox.signals.pop('piezo').sweep_offset=0.5
    # p.lockbox.signals.pop('piezo').sweep_waveform='sin'
    # p.lockbox.signals.pop('piezo').pid.setpoint=1234
    # p.lockbox.signals.pop('piezo').pid.p=0.1
    # p.lockbox.signals.pop('piezo').pid.i=100
    p.lockbox.sweep()
    p.lockbox.calibrate_all()
    p.lockbox.unlock()
    p.lockbox.lock()
    print("p.lockbox.is_locked():" + str(p.lockbox.is_locked()))
    # p = None
    if p.lockbox.is_locking():
        print('starting pyrplclient')
        myClient = pyrplserver(p)
        myClient.client_connect()

