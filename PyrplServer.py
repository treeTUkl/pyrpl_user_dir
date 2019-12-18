import socket
import time
import queue
import threading
import start_pyrpl
import sys


#class client(threading.Thread):
class readConnection():  # todo make thread
    def __init__(self):

        # from  xxxxx import PIStage.py
        self.LOCALHOST = ""
        self.PORT = 54545 #gui port
        self.sock = None

        #PORT = 2161 #tera port
        # LOCALHOST = 'localhost'

        # Initialize ppyrpl:
        self.ppyrpl = start_pyrpl.pyrpl_p()

        tcp_stuff = threading.Thread(target=self.build_tcp_connection, daemon=True)
        tcp_stuff.start()

    def build_tcp_connection(self):
        while True:
            """This sample program, based on the one in the standard library documentation, receives incoming messages and echos them back to the sender. It starts by creating a TCP/IP socket."""
            # Create a TCP/IP socket
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            """ Then bind() is used to associate the socket with the server address. In this case, the address is localhost, referring to the current server, and the port number is 10000."""
            # Bind the socket to the port
            server_address = (self.LOCALHOST, self.PORT)
            print('starting up on %s port %s' % server_address)

            #sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            self.sock.bind(server_address)
            """Calling listen() puts the socket into server mode, and accept() waits for an incoming connection."""
            # Listen for incoming connections
            self.sock.listen(1)
            print("Server started")
            print("Server listening...")
            print("Waiting for client request..")

            # Wait for a connection
            print('waiting for a connection')
            readConnection.connection, readConnection.client_address = self.sock.accept()
            self.sock.settimeout(3)
            """accept() returns an open connection between the server and client, along with the address of the client.
             The connection is actually a different socket on another port (assigned by the kernel).
              Data is read from the connection with recv() and transmitted with sendall()."""
            print('connection from', readConnection.client_address)
            readConnection.pyrplQueue = queue.Queue()
            readConnection.run = True
            y = threading.Thread(target=self.readQueue)
            y.start()
            x = threading.Thread(target=self.recvQueue)
            x.start()
            x.join()
            y.join()

    def recvQueue(self):
        connection=readConnection.connection
        run = readConnection.run
        pyrplQueue = readConnection.pyrplQueue

        time_since_last_good_message = time.time()
        while connection:
            try:
                if run==False:
                    break
                # Receive the data in small chunks and retransmit it
                #connection.settimeout(1)
                data = connection.recv(25)  #
                data = data.decode()
                time.sleep(0.01)

                #data= str(data)
                if data.strip() != "":
                    time_since_last_good_message = time.time()
                    print('\nreceived "%s"' % data)
                    print("\n")
                    pyrplQueue.put(data)
                if data == "close":
                    break

                if time.time() - time_since_last_good_message >= 5:  # 5 second dead man switch
                    print("dead man switch activated")
                    run = False
                    time.sleep(1)
                    self.sock.close()
                    break
            except socket.timeout:
                print("Timeout Occured")
                run = False
                self.sock.close()
                break
            except socket.error:
                print("Error Occured")
                run = False
                self.sock.close()
                break
            except OSError as error:
                print("OSError! Server might not ready %s" % error)
                run = False
                self.sock.close()
                break

            finally:
                # Clean up the connection
                #clear thread
                if run == False:
                    if not pyrplQueue.empty():
                        while not pyrplQueue.empty():
                            try:
                                pyrplQueue.get(False)
                            except Empty:
                                continue
                            pyrplQueue.task_done()
                    pyrplQueue.put("close")


    def readQueue(self):#todo make thread
        connection = readConnection.connection
        pyrplQueue = readConnection.pyrplQueue
        run= readConnection.run
        while run:
            if pyrplQueue.empty() == False:
                data = pyrplQueue.get()
                print(data)
                result = False
                if data[:] == "a1":
                    result =self.ppyrpl.get_voltage(data)

                    message = str(result)
                    message = message.encode()
                    connection.sendall(message)

                elif data[:] == "a2":
                    result = self.ppyrpl.get_voltage(data)
                    message = str(result)
                    message = message.encode()
                    connection.sendall(message)

                elif data[:] == "close":
                    message = "close"
                    message = message.encode()
                    connection.sendall(message)
                    connection.close()
                    if not result:
                        time.sleep(1)
                    connection = False
                    run= False          

                else:
                    print('got strange data: ' + data + ' do nothing with it')
                print("task done")
                pyrplQueue.task_done()
            else:
                time.sleep(0.5)

if __name__ == "__main__":

    readConnection()

