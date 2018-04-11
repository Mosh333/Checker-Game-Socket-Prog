#!/usr/bin/env python3

########################################################################

import socket
import argparse
import sys
import threading
import time
import queue
import tkinter as tk

# By Moshiur Howlader
# Use the standard echo client.
# from EchoClient import Client



########################################################################
# GUI Server class
########################################################################
class Server_Gui:
    def __init__(self, master, queue, endCommand):
        self.queue = queue
        self.master = master
        self.endCommand = endCommand
        self.labe1_text1 = tk.StringVar()
        self.label_text1Count = 0

        # Set up the GUI
        #self.myFrame = tk.Frame(master)
        self.init_board_GUI()
        self.disp_info_GUI()
        self.disp_menubar_GUI()
        # self.doneButton = tk.Button(master, text='Done', command=endCommand)
        # self.doneButton.pack()
        # self.testButton = tk.Button(master, text='Hello', command=self.printHello)
        # self.testButton.pack()
        # self.testIOdata = tk.Label(master, textvariable = self.labe1_text1)
        # self.testIOdata.pack()
        #self.labe1_text1.set("Hello Idiot")
        # Add more GUI stuff here depending on your specific needs
    def init_board_GUI(self):
        print("Placeholder")
        self.rows = 8
        self.columns = 8
        self.size = 40 #size is the size of a square, in pixels 40 x 40
        self.color1 = "cornsilk1"
        self.color2 = "grey"
        self.pieces = {}
        self.canvas_width = self.columns * self.size
        self.canvas_height = self.rows * self.size
        self.canvas = tk.Canvas(borderwidth=0, highlightthickness=0,
                                width=self.canvas_width, height=self.canvas_height,
                                background="goldenrod3")
        self.canvas.pack(side="top", fill="both", expand=True, padx=2, pady=2)
        self.draw_board()
        self.populate_pieces()
        self.game_on()
        
    def draw_board(self):
        self.canvas.delete("square")
        color = self.color2
        for row in range(self.rows):
            color = self.color1 if color == self.color2 else self.color2
            for col in range(self.columns):
                x1 = (col * self.size)
                y1 = (row * self.size)
                x2 = x1 + self.size
                y2 = y1 + self.size
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill=color, tags="square")
                color = self.color1 if color == self.color2 else self.color2
        # self.canvas.tag_raise("blackpiecetag")
        # self.canvas.tag_lower("square")
        
    def populate_pieces(self):
        #Tkinter compatible data (gif)
        blackking = tk.PhotoImage(file="blackking.gif")
        blackpiece = tk.PhotoImage(file="blackpiece.gif")
        redking = tk.PhotoImage(file="redking.gif")
        redpiece = tk.PhotoImage(file="redpiece.gif")
        #initial population of all the pieces for server side
        init_coordArrayX = {(0,1),(0,3),(0,5),(0,7), 
                        (1,0), (1,2), (1,4), (1,6),
                        (2,1),(2,3),(2,5),(2,7)}
        init_coordArrayO = {(5,0),(5,2),(5,4),(5,6), 
                        (6,1), (6,3), (6,5), (6,7),
                        (7,0),(7,2),(7,4),(7,6)}
        pieceCounter = 1
        # self.canvas.create_image(0,0, image=blackpiece, tags=("player1", "blackpiecetag"))                
        # self.placepiece("player1", 0, 0)
        #My Approach will be more brute force, non of this "elegant" automated solution with passing index values
        #create image or delete image approach
        # self.canvas.create_image(60,20, image=blackpiece, tags=("piece1", "blackpiecetag"),anchor="c")
        # self.canvas.create_image(100,20, image=blackpiece, tags=("piece2", "blackpiecetag"),anchor="c")        
        # self.placepiece(blackpiece, 0, 0)
        #self.canvas.delete("piece2")
        
        for row in range(8):
            for col in range(8):
                if (row,col) in init_coordArrayX:
                    xCoord = (col * self.size) + int(self.size/2)
                    yCoord = (row * self.size) + int(self.size/2)
                    self.canvas.create_image(xCoord,yCoord,image=blackpiece, tags=("piece"+str(pieceCounter), "blackpiecetag"),anchor="c")
                    pieceCounter = pieceCounter + 1
                elif (row,col) in init_coordArrayO:
                    xCoord = (col * self.size) + int(self.size/2)
                    yCoord = (row * self.size) + int(self.size/2)
                    self.canvas.create_image(xCoord,yCoord, image=redpiece, tags=("piece"+str(pieceCounter), "redpiecetag"),anchor="c")
                    pieceCounter = pieceCounter + 1
        self.placepiece(blackpiece, 0, 0)
        self.placepiece(redpiece, 0, 0)
        # for i in range(8):
            # print("server checkerboard is at: ", Server.checkerboard[i])
        
        #time.sleep(4)
        #self.movepiece("piece2", 7, 7)
        #self.movepiece("piece13", 0, 3)
        #self.canvas.create_image(300,300, image=blackpiece, tags=("piece2", "blackpiecetag"),anchor="c")

        
                
    def placepiece(self, name, row, column): #this does not do what you think it does, magically makes everything appear
        '''Place a piece at the given row/column'''
        self.pieces[name] = (row, column) #dictionary to place the pieces
        x0 = (column * self.size) + int(self.size/2)
        y0 = (row * self.size) + int(self.size/2)
        self.canvas.coords(name, x0, y0)
        print("coordinates x0 and y0: ", x0, y0)
        
    def removepiece(self, name):
        #just remove from board
        print("Placeholder")
        oldCoordX = 5
        oldCoordY = 5
        Server.numCaptured = Server.numCaptured + 1
        self.canvas.gettags(name)
    def movepiece(self, name, destRow, destCol): 
        #remove and place aka move piece
        
        # blackpiece = tk.PhotoImage(file="blackpiece.gif")
        # self.canvas.delete(name)
        # self.canvas.create_image(300,300, image=blackpiece, tags=("piece2", "blackpiecetag"),anchor="c")
        # self.placepiece(blackpiece, 0, 0)
        
        #GUI Portion of movepiece (frontend)
        #Store data
        myList = self.canvas.gettags(name)
        #find current location in the board
        for sublist in Server.coordArrayX:
            if(sublist[0]==name):
                oldCoordX = sublist[1]
                oldCoordY = sublist[2]
        for sublist in Server.coordArrayO:
            if(sublist[0]==name):
                oldCoordX = sublist[1]
                oldCoordY = sublist[2]
        print(oldCoordX)
        print(oldCoordY)
        image_name = myList[1][0:-3]
        print("image_name is", image_name)
        tag_name1 = myList[0]
        tag_name2 = myList[1]
        image_name = image_name + ".gif"
        print(image_name)
        print(tag_name1)
        print(tag_name2)
        image_name = tk.PhotoImage(file=image_name) #blackpiece, technically can just hard code it
        #Remove piece
        self.canvas.delete(name)
        xCoord = (destCol * self.size) + int(self.size/2)
        yCoord = (destRow * self.size) + int(self.size/2)
        print("xCoord, yCoord", xCoord, yCoord)
        self.canvas.create_image(xCoord,yCoord,image=image_name, tags=(tag_name1, tag_name2),anchor="c")
        self.placepiece(image_name, 0, 0)
        
        #Data Struct Portion of movepiece (backend)
        Server.checkerboard[oldCoordX][oldCoordY] = 's'
        if(tag_name2 == "blackpiecetag"):
            Server.checkerboard[destRow][destCol] = 'o'
        elif(tag_name2 == "redpiecetag"):
            Server.checkerboard[destRow][destCol] = 'x'
            
        # print("Test if data struct alteration worked...")    
        # for i in range(8):
            # print("server checkerboard is at: ", Server.checkerboard[i])

    def enable_callback(self):
        self.canvas.bind("<Button-1>", self.server_game_callback)
        self.canvas.bind("<Button-3>", self.server_game_callback)
        
    def server_game_callback(self, event):
        #basically binding of the O pieces and its movement from GUI are handled
        print("clicked at", event.x, event.y)
        #if(Server.turn%2 == 1):
        if(self.click_counter == 0):
            #pick a red piece
            self.old_x_coord = event.x
            self.old_y_coord = event.y
            #use self.compute_indices() to find the piece name
            #self.old_O_piece_clicked = piece_name
            my_index = self.compute_indices(event.x, event.y)
            for my_piece_O in range(len(Server.coordArrayO)):
                if(my_index[0] == Server.coordArrayO[my_piece_O][1]):
                    if(my_index[1] == Server.coordArrayO[my_piece_O][2]):
                        self.old_O_piece_clicked = Server.coordArrayO[my_piece_O][0]
            self.click_counter = 1
            return
        if(self.click_counter == 1):
            self.click_counter = 0
            #use self.old_x_coord and self.old_y_coord
            #to determine piece name
            #self.movepiece(name, destRow, destCol)
            my_index = self.compute_indices(event.x, event.y)
            #validate the red piece movement here
            self.movepiece(self.old_O_piece_clicked, my_index[0], my_index[1])
            self.disp_info_GUI()
            self.disp_menubar_GUI()
            #Server.numCaptured = Server.numCaptured + 1
            return
        # elif(Server.turn%2 == 1):
            # #redraw GUI based on info from client
        # elif(Server.numCaptured == 12 and Server.numRemaining == 0)
            # print("Gameover")

            

        
    def game_on(self):
        self.click_counter = 0
        self.old_x_coord = 0
        self.old_y_coord = 0
        self.old_O_piece_clicked = ""
        self.enable_callback()
        #we want to bind player presses to the board and act accordingly
        
    def compute_indices(self, x_coord, y_coord):
        #given pixel values, return row and y  values as tuple
        if(y_coord <40):
            if(x_coord <40):
                return (0,0)
            elif(x_coord <80):
                return (0,1)
            elif(x_coord <120):
                return (0,2)
            elif(x_coord <160):
                return (0,3)
            elif(x_coord <200):
                return (0,4)
            elif(x_coord <240):
                return (0,5)
            elif(x_coord <280):
                return (0,6)
            else:               
                return (0,7)
        elif(y_coord < 80):
            if(x_coord <40):
                return (1,0)
            elif(x_coord <80):
                return (1,1)
            elif(x_coord <120):
                return (1,2)
            elif(x_coord <160):
                return (1,3)
            elif(x_coord <200):
                return (1,4)
            elif(x_coord <240):
                return (1,5)
            elif(x_coord <280):
                return (1,6)
            else:               
                return (1,7)
                
        elif(y_coord < 120):
            if(x_coord <40):
                return (2,0)
            elif(x_coord <80):
                return (2,1)
            elif(x_coord <120):
                return (2,2)
            elif(x_coord <160):
                return (2,3)
            elif(x_coord <200):
                return (2,4)
            elif(x_coord <240):
                return (2,5)
            elif(x_coord <280):
                return (2,6)
            else:               
                return (2,7)

        elif(y_coord < 160):
            if(x_coord <40):
                return (3,0)
            elif(x_coord <80):
                return (3,1)
            elif(x_coord <120):
                return (3,2)
            elif(x_coord <160):
                return (3,3)
            elif(x_coord <200):
                return (3,4)
            elif(x_coord <240):
                return (3,5)
            elif(x_coord <280):
                return (3,6)
            else:               
                return (3,7)

        elif(y_coord < 200):
            if(x_coord <40):
                return (4,0)
            elif(x_coord <80):
                return (4,1)
            elif(x_coord <120):
                return (4,2)
            elif(x_coord <160):
                return (4,3)
            elif(x_coord <200):
                return (4,4)
            elif(x_coord <240):
                return (4,5)
            elif(x_coord <280):
                return (4,6)
            else:               
                return (4,7)

        elif(y_coord < 240):
            if(x_coord <40):
                return (5,0)
            elif(x_coord <80):
                return (5,1)
            elif(x_coord <120):
                return (5,2)
            elif(x_coord <160):
                return (5,3)
            elif(x_coord <200):
                return (5,4)
            elif(x_coord <240):
                return (5,5)
            elif(x_coord <280):
                return (5,6)
            else:               
                return (5,7)
                
        elif(y_coord < 280):
            if(x_coord <40):
                return (6,0)
            elif(x_coord <80):
                return (6,1)
            elif(x_coord <120):
                return (6,2)
            elif(x_coord <160):
                return (6,3)
            elif(x_coord <200):
                return (6,4)
            elif(x_coord <240):
                return (6,5)
            elif(x_coord <280):
                return (6,6)
            else:               
                return (6,7)
                
        else:
            if(x_coord <40):
                return (7,0)
            elif(x_coord <80):
                return (7,1)
            elif(x_coord <120):
                return (7,2)
            elif(x_coord <160):
                return (7,3)
            elif(x_coord <200):
                return (7,4)
            elif(x_coord <240):
                return (7,5)
            elif(x_coord <280):
                return (7,6)
            else:               
                return (7,7)

    def disp_info_GUI(self):
        print("disp_info_GUI Placeholder")
        self.doneButton = tk.Button(self.canvas, text='Done', command=self.endCommand)
        self.doneButton.grid(padx = 450, pady = 50)#(side=tk.RIGHT)
        # self.testButton = tk.Button(self.master, text='Hello', command=self.printHello)
        # self.testButton.pack()
        # self.testIOdata = tk.Label(self.master, textvariable = self.labe1_text1)
        # self.testIOdata.pack()
        # self.labe1_text1.set("Hello Idiot")
    def disp_menubar_GUI(self):
        print("disp_menubar_GUI Placeholder") 
    def printHello(self):
        self.label_text1Count+=1
        print("Hello World!")
        if(self.label_text1Count%2 == 1):
            self.labe1_text1.set("Test")
        else:
            self.labe1_text1.set("Not Test")
            
        print("Set new text")
        
    def processIncoming(self):
        """Handle all messages currently in the queue, if any."""
        while self.queue.qsize():
            try:
                msg = self.queue.get(0)
                # Check contents of message and do whatever is needed. As a
                # simple test, print it (in real life, you would
                # suitably update the GUI's display in a richer fashion).
                print("Printing my message", msg)
                self.labe1_text1.set(msg)
            except queue.Empty:
                # just on general principles, although we don't
                # expect this branch to be taken in this case
                pass


########################################################################
# Echo Server class
########################################################################
class Server:
    # We will make the server threaded so that GUI and network socket I/O can run
    # concurrently!
    HOSTNAME = "0.0.0.0" # socket.gethostname()
    PORT = 50000

    RECV_SIZE = 1024
    BACKLOG = 10
    
    MSG_ENCODING = "utf-8"


    def __init__(self):
        Server.checkerboard = [[], [], [], [], [], [], [], []] #{} we want class variable not instance variable! Can define above
        Server.numCaptured = 0
        Server.numRemaining = 12
        self.turn_count = 1
        self.init_board()
        self.setup_Gui()
        
    def init_board(self):
        #we will define [0,0] to be top left corner
        #we will define [7,7] to be bottom right corner
        #s is space, o is server checker, x is client checker
        # capital O means king checker, capital X means king checker
        # | s x s x s x s x
        # | x s x s x s x s
        # | s x s x s x s x
        # | s s s s s s s s
        # | s s s s s s s s
        # | s o s o s o s o
        # | o s o s o s o s
        # | s o s o s o s o
        
        # a sublist has [piece number, its x coord, its y coord]
        Server.coordArrayX = [["piece1",0,1],["piece2",0,3],["piece3",0,5],["piece4",0,7], 
                        ["piece5",1,0], ["piece6",1,2], ["piece7",1,4], ["piece8",1,6],
                        ["piece9",2,1],["piece10",2,3],["piece11",2,5],["piece12",2,7]]
        Server.coordArrayO = [["piece13",5,0],["piece14",5,2],["piece15",5,4],["piece16",5,6], 
                        ["piece17",6,1], ["piece18",6,3], ["piece19",6,5], ["piece20",6,7],
                        ["piece21",7,0],["piece22",7,2],["piece23",7,4],["piece24",7,6]]
        init_coordArrayX = {(0,1),(0,3),(0,5),(0,7), 
                        (1,0), (1,2), (1,4), (1,6),
                        (2,1),(2,3),(2,5),(2,7)}
        init_coordArrayO = {(5,0),(5,2),(5,4),(5,6), 
                        (6,1), (6,3), (6,5), (6,7),
                        (7,0),(7,2),(7,4),(7,6)}
                        
        for row in range(8):
            for col in range(8):
                Server.checkerboard[row].append('s')
                
        for row in range(8):
            for col in range(8):
                if((row,col) in init_coordArrayX):
                    Server.checkerboard[row][col] = 'x'
                elif((row,col) in init_coordArrayO):
                    Server.checkerboard[row][col] = 'o'
                else:
                    Server.checkerboard[row][col] = 's'
        #####################################################
 
    def setup_Gui(self):
        self.master = tk.Tk() #master = root
        self.master.title("Checkers: Server")
        self.master.minsize(width=640, height=320)
        self.master.maxsize(width=640, height=320)
        self.master.iconbitmap('fireball.ico')
        #Create Queue for I/O communication
        self.queue = queue.Queue() #Queue() class
        
        #Setup GUI here (includes the Checkerboard)
        self.gui = Server_Gui(self.master, self.queue, self.endGame)
        
        # Set up the thread to do asynchronous I/O
        # More threads can also be created and used, if necessary
        # ie if we were to extend this to be a multiplayer game
        self.running = 1
        self.server_thread = threading.Thread(target=self.server_thread)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        # Start the periodic call in the GUI to check if the queue contains
        # anything
        self.periodicCall()
        self.master.mainloop()
        
    def periodicCall(self):
        """
        Check every 200 ms if there is something new in the queue.
        """
        self.gui.processIncoming()
        if not self.running:
            # This is the brutal stop of the system. You may want to do
            # some cleanup before actually shutting it down.
            import sys
            sys.exit(1)
        self.master.after(200, self.periodicCall)
        
    def create_listen_socket(self):
        try:
            # Create an IPv4 TCP socket.
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Get socket layer socket options.
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Bind socket to socket address, i.e., IP address and port.
            self.socket.bind( (Server.HOSTNAME, Server.PORT) )

            # Set socket to listen state.
            self.socket.listen(Server.BACKLOG)
            print("Listening on port {} ...".format(Server.PORT))

        except Exception as msg:
            print(msg)
            sys.exit(1)

    def process_connections_forever(self):
        try:
            while True:
                # Block while waiting for accepting incoming
                # connections. When one is accepted, pass the new
                # (cloned) socket reference to the connection handler
                # function.
                self.connection_handler(self.socket.accept())

        except Exception as msg:
            print(msg)
        except KeyboardInterrupt:
            print()
        finally:
            print("Closing server socket ...")
            self.socket.close()
            sys.exit(1)

    def connection_handler(self, client):
        connection, address_port = client
        print("-" * 72)
        print("Connection received from {}.".format(address_port))

        while True:
            # Receive bytes over the TCP connection. This will block
            # until "at least 1 byte or more" is available.
            recvd_bytes = connection.recv(Server.RECV_SIZE)
            
            # If recv returns with zero bytes, the other end of the
            # TCP connection has closed (The other end is probably in
            # FIN WAIT 2 and we are in CLOSE WAIT.). If so, close the
            # server end of the connection and get the next client
            if len(recvd_bytes) == 0:
                print("Closing {} client connection ... ".format(address_port))
                connection.close()
                break
                
            # Decode the received bytes back into strings. Then output
            # them.
            recvd_str = recvd_bytes.decode(Server.MSG_ENCODING)
            print("Received and storing into queue to disp on GUI: ", recvd_str)
            #msg should be the game data that you want to send to the server!!!!!
            self.queue.put(recvd_str) #msg
                
            # Send the received bytes back to the client.
            connection.sendall(recvd_bytes)
            print("Sent: ", recvd_str)
    def server_thread(self):
        #We will handle our asynchronous I/O of socket communication here.
        self.create_listen_socket()
        #while self.running:
        #insert socket comm here
        self.process_connections_forever()
        #msg should be the game data that you want to send to the server!!!!!
        #put this in the process_connections_forever()
        #self.queue.put(msg)
            
    def endGame(self):
        print("Ending Game")
        self.running = 0
        sys.exit(0)
    
    def one_sec_counter(self):
        self.gameTime = 0
        while True:
            self.gameTime = self.gameTime + 1
            time.sleep(1)

            
########################################################################
# GUI Client class
########################################################################
class Client_Gui:
    def __init__(self, master, queue, endCommand):
        self.queue = queue
        self.labe1_text1 = tk.StringVar()
        # Set up the GUI
        self.init_board_GUI()
        self.init_info_GUI()
        self.init_menubar_GUI()
        # doneButton = tk.Button(master, text='Done', command=endCommand)
        # doneButton.pack()
        # testButton = tk.Button(master, text='Hello', command=self.printHello)
        # testButton.pack()
        # self.testIOdata = tk.Label(master, textvariable = self.labe1_text1)
        # self.testIOdata.pack()
        # Add more GUI stuff here depending on your specific needs
        
    def init_board_GUI(self):
        print("Placeholder")
        self.rows = 8
        self.columns = 8
        self.size = 40
        self.color1 = "cornsilk1"
        self.color2 = "grey"
        self.pieces = {}
        self.canvas_width = self.columns * self.size
        self.canvas_height = self.rows * self.size
        self.canvas = tk.Canvas(borderwidth=0, highlightthickness=0,
                                width=self.canvas_width, height=self.canvas_height,
                                background="goldenrod3")
        self.canvas.pack(side="top", fill="both", expand=True, padx=2, pady=2)
        self.draw_board()
        self.populate_pieces()
        
    def draw_board(self):
        color = self.color2
        for row in range(self.rows):
            color = self.color1 if color == self.color2 else self.color2
            for col in range(self.columns):
                x1 = (col * self.size)
                y1 = (row * self.size)
                x2 = x1 + self.size
                y2 = y1 + self.size
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill=color, tags="square")
                color = self.color1 if color == self.color2 else self.color2
                
    def populate_pieces(self):
        print("Placeholder")
    def init_info_GUI(self):
        print("Placeholder")
    def init_menubar_GUI(self):
        print("Placeholder")
        
    def printHello(self):
        print("Hello World!")
        
        
    def processIncoming(self):
        """Handle all messages currently in the queue, if any."""
        while self.queue.qsize():
            try:
                msg = self.queue.get(0)
                # Check contents of message and do whatever is needed. As a
                # simple test, print it (in real life, you would
                # suitably update the GUI's display in a richer fashion).
                print("Printing my message", msg)
                self.labe1_text1.set(msg)
            except queue.Empty:
                # just on general principles, although we don't
                # expect this branch to be taken in this case
                pass

########################################################################
# Echo Client class
########################################################################

class Client:
    # We will make the client threaded so that GUI and network socket I/O can run
    # concurrently!
    # Set the server hostname to connect to. If the server and client
    # are running on the same machine, we can use the current
    # hostname.
    SERVER_HOSTNAME = socket.gethostname()

    RECV_BUFFER_SIZE = 1024

    def __init__(self):
        self.checkerboard = {}
        self.init_board()
        self.turn_count = 1
        self.setup_GUI()

    def init_board(self):
        #we will define [0,0] to be top left corner
        #we will define [7,7] to be bottom right corner
        #s is space, o is client checker, x is server checker
        # capital O means king checker, capital X means king checker
        # | s x s x s x s x
        # | x s x s x s x s
        # | s x s x s x s x
        # | s s s s s s s s
        # | s s s s s s s s
        # | s o s o s o s o
        # | o s o s o s o s
        # | s o s o s o s o
        # *** Note we will need to flip what is seen from client side on GUI
        coordArrayX = {(0,1),(0,3),(0,5),(0,7), 
                        (1,0), (1,2), (1,4), (1,6),
                        (2,1),(2,3),(2,5),(2,7)}
        coordArrayO = {(5,1),(5,3),(5,5),(5,7), 
                        (6,0), (6,2), (6,4), (6,6),
                        (7,1),(7,3),(7,5),(7,7)}
        for row in range(8):
            for col in range(8):
                if((row,col) in coordArrayX):
                    self.checkerboard[(row,col)] = 'x'
                elif((row,col) in coordArrayO):
                    self.checkerboard[(row,col)] = 'o'
                else:
                    self.checkerboard[(row,col)] = 's'   
        #####################################################

    def setup_GUI(self):
        self.master = tk.Tk() #master = root
        self.master.title("Checkers: Client")
        self.master.minsize(width=640, height=320)
        self.master.maxsize(width=640, height=320)
        self.master.iconbitmap('fireball.ico')
        #Create Queue for I/O communication
        self.queue = queue.Queue() #Queue() class
        
        #Setup GUI here (includes the Checkerboard)
        self.gui = Client_Gui(self.master, self.queue, self.endGame)
        
        # Set up the thread to do asynchronous I/O
        # More threads can also be created and used, if necessary
        self.running = 1
        self.client_thread = threading.Thread(target=self.client_thread)
        self.client_thread.daemon = True
        self.client_thread.start()
        
        # Start the periodic call in the GUI to check if the queue contains
        # anything
        self.periodicCall()
            
        self.master.mainloop()
        
    def periodicCall(self):
        """
        Check every 200 ms if there is something new in the queue.
        """
        self.gui.processIncoming()
        if not self.running:
            # This is the brutal stop of the system. You may want to do
            # some cleanup before actually shutting it down.
            import sys
            sys.exit(1)
        self.master.after(200, self.periodicCall)
        
    def get_socket(self):
        try:
            # Create an IPv4 TCP socket.
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except Exception as msg:
            print(msg)
            sys.exit(1)

    def connect_to_server(self):
        try:
            # Connect to the server using its socket address tuple.
            self.socket.connect((Client.SERVER_HOSTNAME, Server.PORT))
        except Exception as msg:
            print(msg)
            sys.exit(1)

    def get_console_input(self):
        # In this version we keep prompting the user until a non-blank
        # line is entered.
        while True:
            self.input_text = input("Input: ")
            if self.input_text != "":
                break
    
    def send_console_input_forever(self):
        while True:
            try:
                self.get_console_input()
                self.connection_send()
                self.connection_receive()
            except (KeyboardInterrupt, EOFError):
                print()
                print("Closing server connection ...")
                self.socket.close()
                sys.exit(1)
                
    def connection_send(self):
        try:
            # Send string objects over the connection. The string must
            # be encoded into bytes objects first.
            self.socket.sendall(self.input_text.encode(Server.MSG_ENCODING))
        except Exception as msg:
            print(msg)
            sys.exit(1)

    def connection_receive(self):
        try:
            # Receive and print out text. The received bytes objects
            # must be decoded into string objects.
            recvd_bytes = self.socket.recv(Client.RECV_BUFFER_SIZE)

            # recv will block if nothing is available. If we receive
            # zero bytes, the connection has been closed from the
            # other end. In that case, close the connection on this
            # end and exit.
            if len(recvd_bytes) == 0:
                print("Closing server connection ... ")
                self.socket.close()
                sys.exit(1)

            print("Received: ", recvd_bytes.decode(Server.MSG_ENCODING))
            #msg should be the game data that you want to send to the server!!!!!
            self.queue.put(recvd_bytes.decode(Server.MSG_ENCODING))

        except Exception as msg:
            print(msg)
            sys.exit(1)    
            
    def client_thread(self):
        #We will handle our asynchronous I/O of socket communication here.
        self.get_socket()
        self.connect_to_server()
        while self.running:
            #insert socket comm here
            self.send_console_input_forever()
            #msg should be the game data that you want to send to the server!!!!!
            #self.queue.put(msg)
        
    def endGame(self):
        print("Ending Game")
        self.running = 0
        sys.exit(0)
    
    def one_sec_counter(self):
        self.gameTime = 0
        while True:
            self.gameTime = self.gameTime + 1
            time.sleep(1)


########################################################################
# Process command line arguments if run directly.
########################################################################

if __name__ == '__main__':
    roles = {'client': Client,'server': Server}
    parser = argparse.ArgumentParser()

    parser.add_argument('-r', '--role',
                        choices=roles, 
                        help='server or client role',
                        required=True, type=str)

    args = parser.parse_args()
    roles[args.role]()

########################################################################




