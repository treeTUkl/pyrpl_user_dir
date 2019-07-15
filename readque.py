def readQueue(self):
    clientqueue = queue.Queue()
    if Window.clientqueue.empty() == False:
        clientstatus = Window.clientqueue.get()
        Window.clientqueue.task_done()
        if clientstatus[0] == "printme":
            string= str(clientstatus[1])
            self.print_list.addItem(string)
            self.print_list.scrollToBottom()
        elif clientstatus[0] == "Standa_Connected_check":
            mybool = bool(clientstatus[1])
            Standa_Connected_check(mybool)
        elif clientstatus[0] == "POSS":
            result = clientstatus[1].split(', ')
            self.Pos_Number.display(result[0])
            self.uPos_Number.display(result[1])
        elif clientstatus[0] == "close":
            self.print_list.addItem('\nclosing socket')
            self.print_list.scrollToBottom()
            self.sock.close()
        elif clientstatus[0] == "received":
            self.print_list.addItem('received: ' + clientstatus[1])
            self.print_list.scrollToBottom()