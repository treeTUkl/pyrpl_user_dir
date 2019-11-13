import socket
import time
import queue
import threading
import start_pyrpl


#class client(threading.Thread):
class readConnection(threading.Thread):  # todo make thread
    def __init__(self):
        threading.Thread.__init__(self)
        # from  xxxxx import PIStage.py
        LOCALHOST = ""
        PORT = 2161 #tera port

        #PORT = 54545 #gui port
        # LOCALHOST = 'localhost'

        # Initialize ppyrpl:


        """This sample program, based on the one in the standard library documentation, receives incoming messages and echos them back to the sender. It starts by creating a TCP/IP socket."""
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        """ Then bind() is used to associate the socket with the server address. In this case, the address is localhost, referring to the current server, and the port number is 10000."""
        # Bind the socket to the port
        server_address = (LOCALHOST, PORT)
        print('starting up on %s port %s' % server_address)

        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(server_address)
        """Calling listen() puts the socket into server mode, and accept() waits for an incoming connection."""
        # Listen for incoming connections
        sock.listen(1)
        print("Server started")
        print("Server listening...")
        print("Waiting for client request..")

        # Wait for a connection
        print('waiting for a connection')
        readConnection.connection, readConnection.client_address = sock.accept()
        """accept() returns an open connection between the server and client, along with the address of the client.
         The connection is actually a different socket on another port (assigned by the kernel).
          Data is read from the connection with recv() and transmitted with sendall()."""
        print('connection from', readConnection.client_address)
        readConnection.pyrplQueue = queue.Queue()
        readConnection.run = True
        y = threading.Thread(target=self.readQueue).start()
        x= threading.Thread(target=self.recvQueue).start()

    def recvQueue(self):
        connection=readConnection.connection
        run = readConnection.run
        pyrplQueue = readConnection.pyrplQueue

        while connection:

            try:
                if run==False:
                    break
                # Receive the data in small chunks and retransmit it
                #connection.settimeout(1)
                data = connection.recv(4)  #
                data = data.decode()

                #data= str(data)
                print('\nreceived "%s"' %data)
                print("\n\n")

                pyrplQueue.put(data)
                if data[:]=="close":
                    break
            except socket.timeout:
                continue
            except socket.error:

                print("Error Occured")
                run = False
                sock.close()
                break

            finally:
                # Clean up the connection
                #clear thread
                if run== False:
                    if not pyrplQueue.empty():
                        while not pyrplQueue.empty():
                            try:
                                pyrplQueue.get(False)
                            except Empty:
                                continue
                            pyrplQueue.task_done()
                    pyrplQueue.put("close")


    def readQueue(self):#todo make thread
        ppyrpl = start_pyrpl.pyrpl_p()
        ppyrpl.connect()
        connection = readConnection.connection
        pyrplQueue = readConnection.pyrplQueue
        run= readConnection.run
        while run:
            if pyrplQueue.empty() == False:
                data = pyrplQueue.get()
                print(data)
                if data[:] == "a1":
                    result =ppyrpl.get_voltage(data)
              
                    message = "!+"+'Voltage1' + "-> " + str(result) + "+!"
                    message = message.encode()
                    connection.sendall(message)

                elif data[:] == "a2":
                    result = ppyrpl.get_voltage(data)
                    message = "!+" + 'Voltage2' + "-> " + str(result) + "+!"
                    message = message.encode()
                    connection.sendall(message)

                elif data[:] == "close":
                    message = "close"
                    message = message.encode()
                    connection.sendall(message)
                    connection.close()
                    result = ppyrpl.stop_pyrpl()
                    if not result:
                        time.sleep(1)
                    connection = False
                    run= False          

                else:
                    print('got strange data: ' + data + ' do nothing with it')
                print("task done")
                pyrplQueue.task_done()

if __name__ == "__main__":

    readConnection()

