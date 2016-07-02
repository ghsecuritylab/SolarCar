import socket, threading, argparse
#####Custom Libs#####
from ClientHandler import ClientHandler #what clients are passed off too
from ServerDatabase import Database

class Server(threading.Thread): #inherits from threading so that you can run multiple servers on the same computer
    
    def __init__(self, host = "127.0.0.1", port= 5000, backlogs= 100, banFile= None):
        self.host = host #IP to run on
        self.port = port #Port to run on, make sure this is forwarded on your local network router
        self.backlogs = backlogs #Queued connections limit until all more incoming clients are rejected

        if banFile is not None: #a list of client ip addresses that will automatically be rejected when coming onto the server, entered as a text file with each ip on its own line
            self.banFile = open(banFile, 'w+')
            bannedClients = file.readlines()
        else:
            self.banFile = None
        
        self.openServerCon()
        self.currentConnections = []
        
        self.inputMonitor = threading.Thread(target= lambda: monitorUserInput()) #seperate thread for the server admins input from the console
        self.userCommand = ""
        self.inputMonitor.start()
        
        self.printLock = threading.Lock() #used to prevent competing threads from printing at once
        self.connnectionLock = threading.Lock() #used to prevent multiple threads from messing with the servers status or connections list at once to avoid confusion

        self.con = Database
        
        super(Server, self).__init__() #calls the constructor for the thread class it inherits from as well

    #####Main Server Loop#####
    def run(self): #main autonmous server loop, just waits for connections then if they aren't banned, passes them onto a connection handler
        self.serverCon.listen(self.backlogs)
        
        while self.userCommand != "wq": #only quits if the admin inputs the wq command from the console
            con, addr = self.serverCon.accept()

            while self.pause: #used to pause the server accepting connections if too many people are incoming or maintenance is to be done, but current connections dont want to be dropped
                pass

            banned = False
            for ban in self.bannedClients:
                if addr in ban:
                    banned = True
                    break

            if not banned:
                newClient = ClientHandler(con, addr, port, self) #here the new client is passed off to a connection handler
                self.currentConnections.append(newClient)
                newClient.start()
        
        print("Closing Server")
        self.serverCon.close()

    def checkPassword(self, password)
        return self.con.passwordStatus(password)

    #####User Input and displaying functions#####
    def showMessage(msg): #called instead of print to 
        self.printLock.acquire()
        print('\n' + str(msg))
        self.printLock.release()

    #Allows the user to enter in commands in the command prompt even while the server is busy accepting and passing off clients
    def monitorUserInput(self):
        while True:
            self.userCommand = str(input(">>"))

            #just a long if else statement running through all possible user commands, view the help function for a description on any input, and __init__ for variable descriptions
            if '=' in self.userCommand:
                if self.userCommand[:8] == 'backlogs' or self.userCommand[:3] == '-bl':
                    self.backlogs = self.userCommand[self.userCommand.index('=') + 1:]
                elif self.userCommand[:4] == "host" or self.userCommand[:3] == '-ho':
                    self.host = self.userCommand[self.userCommand.index('=') + 1:]
                elif self.userCommand[:4] == "port" or self.userCommand[:2] == '-p':
                    self.port = self.userCommand[self.userCommand.index('=') + 1:]

                self.showMessage("You must restart the server for the changes to take effect")
                answer = ''
                while True: #will restart the server so the change to the server paramter can be put in
                    answer = str(input('Would you like to restart now(Y/N): '))
                    if answer.upper() == "Y" or answer.upper() == "YES":
                        self.restartServer()
                    elif answer.upper() == "N" or answer.upper() == "NO":
                        self.showMessage("\nRestart Canceled")
                    else:
                        self.showMessage('Command Not Recgonized')
                        
            elif self.userCommand[:3] == "-cl": #close a specified connection
                try:
                    client = int(self.userCommand[4:])
                except:
                    client = ""
                    while not isinstance(client, int) and int(client) < len(self.currentConnections):
                        try:
                            client = int(input('Client to delete: '))
                        except:
                            self.showMessage('Please enter an integer')
                finally:
                    self.closeConnection(client)
                    
            elif self.userCommand[:4] == "-clr": #close connections in a specified range
                try:
                    startRange = self.userCommand[5:6]
                    endRange = self.userCommand[7:8]
                except:
                    startRange = ""
                    while not isinstance(startrange, int) and not (int(startRange) < 0 and int(startRange) >= len(self.currentConnections)):
                        try:
                            startRange = int(input('Start of the range: '))
                            if startRange >= len(self.currentConnections) or startRange < 0:
                                raise
                        except:
                            self.showMessage("Please enter in a valid number within the number of current clients")

                    endRange = ""
                    while not isinstance(endRange, int) and not (endRange >= len(self.currentConnections and endRange < 0):
                        try:
                            endRange = int(input('End of the Range: '))
                            if endRange >= len(self.currentConnections) or endRange < 0:
                                raise
                        except:
                            self.showMessage("Please enter in a valid number within the number of current clients")
                finally:
                    self.closeConnectionRange(startRange, endRange)
                                                                 
            elif self.userCommand[:4] == "-cla": #close all connections
                answer = ""
                while True:
                    answer = str(input("Are you sure you would like to close all client connections(Y/N): "))
                    answer = answer.upper()
                    if answer == "Y" or answer == "YES":
                        self.closeAllConnections()
                        break;
                    elif answer == 'N' or answer == "NO":
                        self.showMessage("Canceling closing all client proccesses")
                        break;
                                                                 
            elif self.userCommand[:3] == "-pa": #pause the server
                self.pauseServer()
                                                                 
            elif self.userCommand[:3] == "-upa": #unpause the server
                self.unpauseServer()
                                                                 
            elif self.userCommand[:3] == "-cls": #closes the server to incoming connections
                self.closeServerCon()
                                                                 
            elif self.userCommand[:3] == "-ops": #opens up the server to connections
                self.openServerCon()
                                                                 
            elif self.userCommand[:3] == "-rs": #resets the server
                self.restartServer()
                                                                 
            elif self.userCommand[:4] == "-bci": # bans a client in the specified connection index
                try:
                    client = self.userCommand[5:]
                except:
                    client = ""
                    while '.' is not in client:
                        client = str(input("Enter the client IP: "))
                        if '.' in client:
                            break
                        self.showMessage('Not a valid IP')
                finally:
                    self.banClientIP(client)

            elif self.userCommand[:3] == '-bc': #bans a specified ip
                try:
                    client = self.userCommand[4:]
                except:
                    client = ""
                    while not isinstance(client, int) and client >= len(self.currentConnections):
                        try:
                            client = int(input('Client Connection Number: '))
                            if client >= len(self.currentConnections):
                                raise
                        except:
                            self.showMessage("Enter a valid client number within the client connection range")
                                        
                finally:
                    self.banClient(client)
            
            elif self.userCommand[:4] == "-ubc": #unban a client
                try:
                    client = self.userCommand[5:]
                except:
                    client = str(input("Client IP: "))           
                finally:
                    self.unbanClient(client)
                                                                 
            elif self.userCommand[:3] == "-wq": #ends the server and program
                self.endServer()
                                                                 
            elif self.userCommand[:2] == "-h": #displays all server commands
                self.displayHelp()

            elif self.userCommand[:2] == "-p": #displays server parameters
                self.showMessage('Server Backlogs: ' + self.backlogs)
                self.showMessage('Server Host: ' + self.host)
                self.showMessage('Server port: ' + self.port)

            else:
                self.showMessage('Command not recgonized')

    #####Closing current connections#####                
    def closeConnection(self, con, remove= True): #closes the connection and removes it from the connection list
        con.quit = True
        if remove:
            self.currentConnections.remove(con)
        
    def closeConnectionRange(self, start, last):
        for x in range(start, last + 1):
            self.closeConnection(self.currentConnections[x])
            
    def closeAllConnections(self):
        if not self.paused(): #pauses accepting any more incoming connections so that the list size wont change during iteration
            self.pause()
        for con in self.currentConnections:
            self.closeConnection(con, False) #avoids removing any connections until after the iteration through the list is complete
        self.currentConnections = []
        self.unpause()

    #####Banning/Unbanning Clients#####
    #All banned client ips are kept in a text file that the server reads from
    def banClient(self, clientNum): #bans the ip associated with the connection in the specified number index on the connections list
        clientIp = self.currentConnections[clientNum].addr
        self.bannedClients.append(clientIp + '\n') #adds the ip to the list of banned ips and then below that writes it to the file
        self.banFile.write('\n' + clientIp)

    def banClientIP(self, clientIP): #bans a client ip by both putting them in the ban list and in the ban file
        self.bannedClients.append(clientIP + '\n')
        self.banFile.write('\n' + clientIP)
        
    def unbanClient(self, clientIP): #to unban a client they must be both removed from the ban list and the ban file
        for client in self.bannedClients:
            if clientIP in client:
                self.bannedClients.remove(clientIP + '\n')
                return True
        self.showMessage("No client banned with that IP")
        return False

    def updateBanfile(): #does this whenever the server is closed to make sure the ban list is updated for next start up
        for line in self.bannedClients:
            self.banFile.write(line)

    #####Changing Server Status#####
    def pause(self): #triggers a loop in the main thread that waits until unpaused
        if not self.pause:
            self.pause = True
        else:
            self.showMessage("Server Already Paused")
            
    def unpause(self):
        if self.pause: #breaks the loop the main thread can enter when paused
            self.pause = False
        else:
            self.showMessage("Server Already Unpaused")

    def paused(self):
        return self.pause
        
    def closeServerCon(self): #temporarily shutsdown the server until told to open
        self.closeAllConnections()
        self.serverCon.close()
        
    def openServerCon(self): #reopens the server
        self.serverCon = socket.socket()
        self.serverCon = socket.bind((self.host, self.port))
        self.serverCon.listen(self.backlogs)

    def restartServer(self): #restarts teh server, used to update changed parameters
        self.showMessage("Restarting Server")
        self.closeServerCon()
        self.openServerCon()

    def endServer(self): #shutdowns the server and the program
        self.closeAllConnections()
        self.serverCon.close()
        self.updateBanfile()
        sys.exit(0)

    def displayHelp(self): #used to list off all server commands
        msg += '-cl\t\tCloses a specified client connection\n'
        msg += '-clr\t\tCloses a specified range of clients\n'
        msg += '-cla\t\tCloses all connections\n'
        msg += '-pa\t\tPauses the server\n'
        msg += '-upa\t\tUnpauses the server\n'
        msg += '-cls\t\tCloses the server\n'
        msg += '-ops\t\tReopens the server if closed\n'
        msg += '-rs\t\tRestarts the server\n'
        msg += '-bci\t\tBans a specified IP\n' 
        msg += '-bc\t\tBans a specified client from the current connection list\n'
        msg += "-ubc\t\tUnbans a specified IP"
        msg += "-p\t\tDisplays the paramters of the server that can be changed by the user\n"
        msg += '-wq\t\tShutsdown the server\n'
        msg += "*****You can change any of the server parameters by typing the paramter name, and an equals sign  with the new value*****\n"
        msg += "*****EX: backlogs = 2500, would change the backlogged connection limit to 2500*****\n"
        self.showMessage(msg)

#####For testing the server#####
if __name__ == "__main__":
    #All command line arguments are optional and will revert to default values if not entered
    parser = argparse.ArgumentParser()
    parser.add_argument("-ho", "--host", help= "host the test clients will connect to", type= str)
    parser.add_argument("-p", "--port", help= "port the clients will connect to", type= int)
    parser.add_argument("-bl", "--backlogs", help= "the max number of clients on hold until all new clients past the threshold will be rejected", type= int)
    parser.add_argument('-bf', "--banfile", help= "list of ips to reject", type= str)
    
    args = parser.parse_args()

    if args.host is not None:
        host = args.host
    else:
        host = "127.0.0.1" 
        
    if args.port is not None:
        port = args.port
    else:
        port = 5000

    if args.backlogs is not None:
        backlogs = args.backlogs
    else:
        backlogs = 100

    if args.banfile is not None:
        banFile = args.banFile
    else:
        banFile = None

    #starts the server based off of command line arguments or default values if none were entered, and gets it running
    server = Server(host, port, backlogs, banFile)
    server.start()
    
