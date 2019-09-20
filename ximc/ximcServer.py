import socket
import ximcStage
import time
import queue
import threading
# import sys


#class client(threading.Thread):
class readConnection(threading.Thread):  # todo make thread
    def __init__(self):
        threading.Thread.__init__(self)
        # from  xxxxx import PIStage.py
        LOCALHOST = ""
        # PORT = 2161

        PORT = 54545
        # LOCALHOST = 'localhost'

        # Initialize stage:


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
        readConnection.ximcStageQueue = queue.Queue()
        readConnection.run = True
        y = threading.Thread(target=self.readQueue).start()
        x= threading.Thread(target=self.recvQueue).start()

    def recvQueue(self):
        connection=readConnection.connection
        run = readConnection.run
        ximcStageQueue = readConnection.ximcStageQueue

        while connection:

            try:
                if run==False:
                    break
                # Receive the data in small chunks and retransmit it
                #connection.settimeout(1)
                data = connection.recv(150)  #
                #connection.settimeout(None)
                data = data.decode('utf-8')  # might not needed if data ist already in string format
                print('\nreceived "%s"' % data)

                ximcStageQueue.put(data)
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
                    if not ximcStageQueue.empty():
                        while not ximcStageQueue.empty():
                            try:
                                ximcStageQueue.get(False)
                            except Empty:
                                continue
                            ximcStageQueue.task_done()
                    ximcStageQueue.put("close")


    def readQueue(self):#todo make thread
        stage = ximcStage.StandaStage()
        stage.connect()
        connection = readConnection.connection
        ximcStageQueue = readConnection.ximcStageQueue
        run= readConnection.run
        while run:
            if ximcStageQueue.empty() == False:
                data = ximcStageQueue.get()
                # if data[:3] == "POS":
                #     if data[:] == "POSS":
                #         POS = "!+" + "POSS" + ", "
                #         stage.position_get()
                #         POS = POS + str(stage.position["position_current_Steps"]) + ", " + str(
                #             stage.position["position_current_uSteps"])+ "+!"
                #         POS = POS.encode()
                #         print('got ' + data[:4] + ' send data back to the client')
                #         connection.sendall(POS)
                #     else:
                #         #print('got ' + data[:3] + ' send data back to the client')
                #         POS = stage.POS
                #         print('pos in as: ' + str(POS))
                #         print('sending data back to the client')
                #         POS = "!+" +"POS" + ", " + str(POS) + "+!"
                #         POS = POS.encode()
                #         connection.sendall(POS)
                if data[:] == "STATE":
                    """
                    ("MoveSts", c_uint),
                    ("MvCmdSts", c_uint),
                    ("PWRSts", c_uint),
                    ("EncSts", c_uint),
                    ("WindSts", c_uint),
                    ("CurPosition", c_int),
                    ("uCurPosition", c_int),
                    ("EncPosition", c_longlong),
                    ("CurSpeed", c_int),
                    ("uCurSpeed", c_int),
                    ("Ipwr", c_int),
                    ("Upwr", c_int),
                    ("Iusb", c_int),
                    ("Uusb", c_int),
                    ("CurT", c_int),
                    ("Flags", c_uint),
                    ("GPIOFlags", c_uint),
                    ("CmdBufFreeSpace", c_uint),
                    """
                    print('got ' + data[:] + ' send data back to the client')
                    result = stage.Standa_Status()
                    POS = "!+"+'STATE' + ", "
                    POS = POS + "MoveSts" + "-> " + str(result.MoveSts) + ", "
                    POS = POS + "CurSpeed" + "-> " + str(result.CurSpeed) + ", "
                    POS = POS + "uCurSpeed" + "-> " + str(result.uCurSpeed) + ", "
                    POS = POS + "CurPosition" + "-> " + str(result.CurPosition) + ", "
                    POS = POS + "uCurPosition" + "-> " + str(result.uCurPosition) + ", "
                    result = stage.POS
                    POS = POS + "asPosition" + "-> " + str(result) + "+!"
                    POS = POS.encode()
                    connection.sendall(POS)
                elif data[:4] == "Mess":  # TODO make some thread becouse movv 50000 will run very long
                    new_position_in_as = float(data[4:])
                    print('Mess' + str(new_position_in_as))
                    stage.move_absolute_in_as(new_position_in_as)

                    POS = "!+" + "Mess" + "+!"
                    POS = POS.encode()
                    connection.sendall(POS)

                elif data[:3] == "MOV":
                    if data[:4] == "MOVV":
                        result = data[4:].split(', ')
                        print('MOVV ' + str(result[0]) + ', ' + str(result[1]))
                        stage.move_absolute_in_steps(int(result[0]),
                                                     int(result[1]))  # TODO make some thread becouse movv 50000 will run very long
                        print('got ' + data[:4] + ' send data back to the client')
                        POS = "!+"+data[:4]+ "+!"
                        POS = POS.encode()
                        connection.sendall(POS)
                    else:
                        new_position_in_as = float(data[3:])
                        print('MOV' + str(new_position_in_as))
                        stage.move_absolute_in_as(new_position_in_as)
                        print('got ' + data[:3] + ' send data back to the client')
                        POS = "!+"+ data[:3]+"+!"
                        POS = POS.encode()
                        connection.sendall(POS)

                elif data[:3] == "MVR":
                    if data[:4] == "MVRR":  # TODO make some thread becouse morr 50000 will run very long
                        result = data[4:].split(', ')
                        print(data[:4] + ' ' + str(result[0]) + ', ' + str(result[1]))
                        stage.move_relative_in_steps(int(result[0]), int(result[1]))
                        print('got ' + data[:4] + ' send data back to the client')
                        POS = "!+"+data[:4]+"+!"
                        POS = POS.encode()
                        connection.sendall(POS)
                    else:
                        new_position_in_as = float(data[3:])
                        print('MVR: ' + str(new_position_in_as))
                        stage.move_relative_in_as(new_position_in_as)
                        print('got ' + data[:3] + ' send data back to the client')
                        POS ="!+"+ data[:3]+"+!"
                        POS = POS.encode()
                        connection.sendall(POS)

                elif data[:3] == "GOH":
                    print('GOH')
                    stage.go_home()
                    print('got ' + data[:3] + ' send data back to the client')
                    POS = "!+"+data[:3]+"+!"
                    POS = POS.encode()
                    connection.sendall(POS)

                elif data[:3] == "DEH":
                    print('DEH')
                    stage.set_zero_position()
                    print('got ' + data[:3] + ' send data back to the client')
                    POS ="!+"+ data[:3]+ "+!"
                    POS = POS.encode()
                    connection.sendall(POS)

                elif data[:3] == "SDN":
                    print('SDN')
                    stage.in_case_terra_sends_SDN()
                    POS = stage.POS
                    print('got ' + data[:3] + ' send data back to the client')
                    POS = "!+"+data[:3]+ "+!"
                    POS = POS.encode()
                    connection.sendall(POS)

                elif data[:] == "close":
                    POS = "close"
                    POS = POS.encode()
                    connection.close()
                    result = stage.disconnect()
                    if not result:
                        time.sleep(1)
                    connection = False
                    run= False

                elif data[:] == "LMOVE":
                    stage.move_left()
                    POS = "!+"+"LMOVE" + "+!"
                    print('got ' + data[:] + ' send data back to the client')
                    POS = POS.encode()
                    connection.sendall(POS)

                elif data[:] == "RMOVE":
                    stage.move_right()
                    POS ="!+"+ "RMOVE"+ "+!"
                    print('got ' + data[:] + ' send data back to the client')
                    POS = POS.encode()
                    connection.sendall(POS)

                elif data[:] == "STOPMOVE":

                    stage.stop_move()
                    POS = "!+"+"STOPMOVE"+ "+!"
                    print('got ' + data[:] + ' send data back to the client')
                    POS = POS.encode()
                    connection.sendall(POS)

                elif data[:] == "STOPFAST":
                    POS = stage.fast_stop()
                    print('got ' + data[:] + ' send data back to the client')
                    POS ="!+"+ data[:] + POS+ "+!"
                    POS = POS.encode()
                    connection.sendall(POS)
                #########################################################
                # gui control stuff
                # elif data[:] == "POSS":
                #     POS= "POSS"+ ", "
                #     stage.position_get()
                #     POS = POS + str(stage.position["position_current_Steps"]) + ", " + str(stage.position["position_current_uSteps"])
                #     POS = POS.encode()
                #     print(' sending data back to the client')
                #     connection.sendall(POS)

                elif data[:4] == "MSET":

                    MSET = data[4:].split(', ')
                    result = stage.Standa_set_settings(int(MSET[0]), int(MSET[1]), int(MSET[2]), int(MSET[3]))
                    POS ="!+"+ "MSET" + ", " + result+ "+!"
                    POS = POS.encode()
                    print('got ' + str(data[:]) + ' send data back to the client')
                    connection.sendall(POS)

                elif data[:4] == "MGET":

                    """' 
                    move_settings.Speed = Speed
                    move_settings.Accel = Accel
                    move_settings.Decel = Decel
                    engine_settings.MicrostepMode = MicroMode
                    '"""

                    POS ="!+"+ "MGET" + ", "
                    y_status = stage.Standa_get_motor_settings()
                    POS = POS + "Speed" + "-> " + str(y_status.Speed) + ", "
                    POS = POS + "Accel" + "-> " + str(y_status.Accel) + ", "
                    POS = POS + "Decel" + "-> " + str(y_status.Decel) + ", "

                    result = stage.Standa_get_engine_settings()
                    POS = POS + "MicroStepMode" + "-> " + str(result.MicrostepMode)+ "+!"
                    POS = POS.encode()
                    print(' sending data back to the client')
                    connection.sendall(POS)

                else:
                    print('got strange data: ' + data + ' do nothing with it')
                    # counter = counter + 1
                    # if counter >= 20:
                    #    connection.close()
                    #    stage.disconnect()
                    #    break
                    data = 0
                ximcStageQueue.task_done()

if __name__ == "__main__":

    readConnection()

