import socket
import queue
import threading
import time

class client():


    #def __init__(self, host, port, GUI):
        # \*----Mutliprozess------*/
    def __init__(self, host, port,clientsendqueue,clientprintqueue ):
        #threading.Thread.__init__(self)
        self.sock = 0
        self.HOST = host
        self.PORT = int(port)
        #self.GUI = GUI
        self.stopconnect = False
        self.clientsendqueue=clientsendqueue
        self.clientprintqueue=clientprintqueue
        self.connect()

    def connect(self):
        if self.sock == 0 or self.sock._closed == True:
            # HOST = 'localhost'
            # PORT = 54545
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            try:
                self.sock.connect((self.HOST, self.PORT))
                self.clientprintqueue.put(['printme', 'connected to server'])#ToDO befor that the queue should be empty
                self.clientprintqueue.put(['Standa_Connected_check', True])
                self.clientsendqueue.put(["POSS", ""])

            except ConnectionRefusedError:
                self.clientprintqueue.put(['printme', 'Connection Refused! Server might not ready'])
                self.clientprintqueue.put(["printme", "Code to start on rp-f053d1:\n"
                                                           "cd /root/ximc/ximc-2.9.8\npython3 ximcServer.py"])
                self.clientprintqueue.put(["Standa_Refused",""])
               # self.GUI.standa_live_control = False
               # self.GUI.Standa_Connected_check(False)
                #self.GUI.standaclient = False
                self.stopconnect =True

            except OSError:
                #self.GUI.windowprintqueue.put(['printme', 'Connection Refused! Server might not ready'])
                #self.QMessageBox.about(self, "Connect where to?", "Standa IP is seems invalid!")
                #self.GUI.windowprintqueue.put(['printme', 'stopping....'])
                self.stopconnect = True
            finally:
                if self.stopconnect == False:
                    self.clientprintqueue.put(['printme', 'connected to server'])#ToDO befor that the queue should be empty
                    self.clientprintqueue.put(['Standa_Connected_check', True])
                    self.clientsendqueue.put(["STATE", ""])
                    #self.GUI.Standa_Connected = True
                    self.handleThread=threading.Thread(target=self.handleClientQueue).start()
                    self.recvThread=threading.Thread(target=self.recv).start()
                else:
                    self.sock.close()


    def handleClientQueue(self):#TODO when will i arrive here?

        while True:
            if self.clientsendqueue.empty() == False:

                clientsend = self.clientsendqueue.get()

                string=str(clientsend[0]+clientsend[1])
                if clientsend[0]=="cclose":
                    break
                else:
                    if clientsend[0]=="close":
                        self.send(string)
                        break
                    self.send(string)
                    string=""
                    #time.sleep(0.03)
                self.clientsendqueue.task_done()
        print("handleClientQueue died")


    def recv(self):
        t = threading.currentThread()
        buff=""
        while getattr(t, "do_run", True):
            try:

                data = self.sock.recv(150)

                data = data.decode()
                if not data:
                    self.clientprintqueue.put(
                        ['printme', 'nothing received.\nseems to be an error on server\nnothing '
                                    'received.\nseems to be an error on server\nmight need to call'
                                    ' close socket here?'])
                    self.sock.close()
                    break
                if not data[:2] == "!+":
                    datasplit = data.split("+!")
                    data = datasplit[0]
                    data = buff + data
                    #datalist.append(data)
                    buff = datasplit[1]
                else:
                    datasplit = data.split("+!")
                    data = datasplit[0]
                    buff=datasplit[1]

                data = data[2:]

                # if data[:4] == "POSS":
                #     self.clientprintqueue.put(['POSS', data[6:]])
                # elif data[:3] == "POS":
                #     self.clientprintqueue.put(['POS', data[5:]])
                if data[:4] == "MOVV":
                    self.clientprintqueue.put(['MOVV', ''])
                elif data[:3] == "MOV":
                    self.clientprintqueue.put(['MOV', ''])
                elif data[:5] == "STATE":
                    self.clientprintqueue.put(['STATE', data[7:]])
                elif data[:4] == "MVRR":
                    self.clientprintqueue.put(['MVRR', ''])
                elif data[:3] == "MVR":
                    self.clientprintqueue.put(['MVR', ''])
                elif data[:3] == "DEH":
                    self.clientprintqueue.put(['DEH', ''])
                elif data[:3] == "SDN":
                    self.clientprintqueue.put(['SDN', ''])
                elif data[:] == "close":
                    self.clientprintqueue.put(['close', 'server client called close!'])
                    break
                elif data[:] == "LMOVE":
                    self.clientprintqueue.put(['LMOVE', ''])
                elif data[:] == "RMOVE":
                    self.clientprintqueue.put(['RMOVE', ''])
                elif data == "STOPMOVE":
                    self.clientprintqueue.put(['STOPMOVE', ''])
                elif data[:4] == "MGET":
                    self.clientprintqueue.put(['MGET', data[6:]])
                elif data[:4] == "MSET":
                    self.clientprintqueue.put(['MSET', data[6:]])
                elif data[:4] == "Mess":
                    self.clientprintqueue.put(['Mess', ""])
                    #self.clientprintqueue.put(['Mess', data[6:]])
                elif data[:] == "ClearList":
                    while not self.clientsendqueue.empty():
                        try:
                            self.clientsendqueue.get()
                        except Empty:
                            continue
                        self.clientsendqueue.task_done()
                    if self.clientsendqueue.empty():
                        self.clientprintqueue.put(['printme', 'Cleaned send quueue (Debugging Info)'])#TODO

                else:
                    self.clientprintqueue.put(['printme', data])
                time.sleep(0.01)

            except socket.error:
                self.clientprintqueue.put(['printme', 'Error Occured.->closing socket'])
                self.sock.close()
                self.clientprintqueue.put(['cclose', ""])
                break
        if not self.clientsendqueue.empty():
            while not self.clientsendqueue.empty():
                try:
                    self.clientsendqueue.get(False)
                except Empty:
                    continue
                self.clientsendqueue.task_done()
        self.clientprintqueue.put(['cclose', ""])

        self.sock.close()
        #self.GUI.Standa_Connected = False
        print("clientprintqueue died")


    def send(self, message):
        if self.sock == 0 or self.sock._closed == True:
            self.clientprintqueue.put(['printme', 'no socked, try connect first..'])
        else:
            # Send data
            self.clientprintqueue.put(['printme', 'sending:' + message])
            try:
                if message == "close":
                    self.clientprintqueue.put(['printme', 'closing socket'])
                    message = message.encode()
                    self.sock.sendall(message)
                else:
                    message = message.encode()
                    self.sock.sendall(message)  # TODO  add case for timeout from server??

            except (ConnectionAbortedError, EOFError, AttributeError):
                self.clientprintqueue.put(
                    ['printme', 'Sending Error: seems to be an error on server->closing socket'])
                self.sock.close()

    def close(self):
        self.clientprintqueue.put(['printme', 'closing socket'])
        self.clientsendqueue.put(['close',""])
        client.terminate()
        #self.send("close")