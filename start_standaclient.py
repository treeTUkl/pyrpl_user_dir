import socket
import queue
import threading
import time

class client():
    #clientsendqueue = queue.Queue()
    #clientprintqueue = queue.Queue()
    def __init__(self, host, port, GUI):
    #def __init__(self, host, port):
        #threading.Thread.__init__(self)
        self.sock = 0
        self.HOST = host
        self.PORT = int(port)
        self.GUI = GUI
        self.stopconnect = False
        self.connect()

    def connect(self):
        if self.sock == 0 or self.sock._closed == True:
            # HOST = 'localhost'
            # PORT = 54545
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            try:
                self.sock.connect((self.HOST, self.PORT))
                #client.clientprintqueue.put(['printme', 'connected to server'])#ToDO befor that the queue should be empty
                #client.clientprintqueue.put(['Standa_Connected_check', True])
                #client.clientsendqueue.put(["POSS", ""])

            except ConnectionRefusedError:
                self.GUI.windowprintqueue.put(['printme', 'Connection Refused! Server might not ready'])
                self.GUI.windowprintqueue.put(["printme", "Code to start on rp-f053d1:\n"
                                                          "cd /root/ximc/ximc-2.9.8\npython3 ximcServer.py"])
                self.GUI.standa_live_control = False
                self.GUI.Standa_Connected_check(False)
                self.GUI.standaclient = False
                self.stopconnect =True

            except OSError:
                self.GUI.windowprintqueue.put(['printme', 'Connection Refused! Server might not ready'])
                #self.QMessageBox.about(self, "Connect where to?", "Standa IP is seems invalid!")
                self.GUI.windowprintqueue.put(['printme', 'stopping....'])
                self.stopconnect = True
            finally:
                if self.stopconnect == False:
                    client.clientsendqueue = queue.Queue()
                    client.clientprintqueue = queue.Queue()
                    client.clientprintqueue.put(['printme', 'connected to server'])#ToDO befor that the queue should be empty
                    client.clientprintqueue.put(['Standa_Connected_check', True])
                    client.clientsendqueue.put(["STATE", ""])
                    self.GUI.Standa_Connected = True
                    self.handleThread=threading.Thread(target=self.handleClientQueue).start()
                    self.recvThread=threading.Thread(target=self.recv).start()
                else:
                    self.sock.close()


    def handleClientQueue(self):#TODO when will i arrive here?

        while True:
            if client.clientsendqueue.empty() == False:

                clientsend = client.clientsendqueue.get()

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
                client.clientsendqueue.task_done()
        print("handleClientQueue died")


    def recv(self):
        t = threading.currentThread()
        buff=""
        while getattr(t, "do_run", True):
            try:

                data = self.sock.recv(150)

                data = data.decode()
                if not data:
                    client.clientprintqueue.put(
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
                #     client.clientprintqueue.put(['POSS', data[6:]])
                # elif data[:3] == "POS":
                #     client.clientprintqueue.put(['POS', data[5:]])
                if data[:4] == "MOVV":
                    client.clientprintqueue.put(['MOVV', ''])
                elif data[:3] == "MOV":
                    client.clientprintqueue.put(['MOV', ''])
                elif data[:5] == "STATE":
                    client.clientprintqueue.put(['STATE', data[7:]])
                elif data[:4] == "MVRR":
                    client.clientprintqueue.put(['MVRR', ''])
                elif data[:3] == "MVR":
                    client.clientprintqueue.put(['MVR', ''])
                elif data[:3] == "DEH":
                    client.clientprintqueue.put(['DEH', ''])
                elif data[:3] == "SDN":
                    client.clientprintqueue.put(['SDN', ''])
                elif data[:] == "close":
                    client.clientprintqueue.put(['close', 'server client called close!'])
                    break
                elif data[:] == "LMOVE":
                    client.clientprintqueue.put(['LMOVE', ''])
                elif data[:] == "RMOVE":
                    client.clientprintqueue.put(['RMOVE', ''])
                elif data == "STOPMOVE":
                    client.clientprintqueue.put(['STOPMOVE', ''])
                elif data[:4] == "MGET":
                    client.clientprintqueue.put(['MGET', data[6:]])
                elif data[:4] == "MSET":
                    client.clientprintqueue.put(['MSET', data[6:]])
                elif data[:4] == "Mess":
                    client.clientprintqueue.put(['Mess', ""])
                    #client.clientprintqueue.put(['Mess', data[6:]])
                elif data[:] == "ClearList":
                    while not client.clientsendqueue.empty():
                        try:
                            client.clientsendqueue.get()
                        except Empty:
                            continue
                        client.clientsendqueue.task_done()
                    if client.clientsendqueue.empty():
                        client.clientprintqueue.put(['printme', 'Cleaned send quueue (Debugging Info)'])#TODO

                else:
                    client.clientprintqueue.put(['printme', data])
                time.sleep(0.01)

            except socket.error:
                client.clientprintqueue.put(['printme', 'Error Occured.->closing socket'])
                self.sock.close()
                client.clientprintqueue.put(['cclose', ""])
                break
        if not client.clientsendqueue.empty():
            while not client.clientsendqueue.empty():
                try:
                    client.clientsendqueue.get(False)
                except Empty:
                    continue
                client.clientsendqueue.task_done()
        client.clientprintqueue.put(['cclose', ""])

        self.sock.close()
        self.GUI.Standa_Connected = False
        print("clientprintqueue died")


    def send(self, message):
        if self.sock == 0 or self.sock._closed == True:
            client.clientprintqueue.put(['printme', 'no socked, try connect first..'])
        else:
            # Send data
            client.clientprintqueue.put(['printme', 'sending:' + message])
            try:
                if message == "close":
                    client.clientprintqueue.put(['printme', 'closing socket'])
                    message = message.encode()
                    self.sock.sendall(message)
                else:
                    message = message.encode()
                    self.sock.sendall(message)  # TODO  add case for timeout from server??

            except (ConnectionAbortedError, EOFError, AttributeError):
                client.clientprintqueue.put(
                    ['printme', 'Sending Error: seems to be an error on server->closing socket'])
                self.sock.close()

    def close(self):
        client.clientprintqueue.put(['printme', 'closing socket'])
        client.clientsendqueue.put(['close',""])
        #self.send("close")