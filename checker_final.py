#!/usr/bin/env python3

########################################################################

import socket
import argparse
import sys
import threading
import time
import queue
import tkinter as tk
from tkinter import messagebox
import os
import pickle
from itertools import count
import multiprocessing.pool
import functools

# By Moshiur Howlader
# Use the standard echo client.
# from EchoClient import Client



########################################################################
# GUI Server class
########################################################################
class Server_Gui:
    def __init__(self, master, recv_queue, send_queue, endCommand):
        Server_Gui.msg_to_send = []
        Server_Gui.selected_piece = ""
        Server_Gui.moveflag = 0
        self.recv_queue = recv_queue
        
        self.master = master
        self.endCommand = endCommand
        self.label_text1 = tk.StringVar()
        self.label_text1Count = 0
        self.label_text2 = tk.StringVar()
        self.label_text3 = tk.StringVar()
        self.gameTime = 0
        # Set up the GUI
        #self.myFrame = tk.Frame(master)
        self.init_board_GUI()
        self.init_info_GUI()
        self.one_sec_counter(self.TIMER_Label)
        # Add more GUI stuff here depending on your specific needs
    def init_board_GUI(self):
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
        #self.canvas.delete("square")
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

        
        #self.movepiece("piece2", 7, 7)
        #self.movepiece("piece13", 0, 3)
        #self.canvas.create_image(300,300, image=blackpiece, tags=("piece2", "blackpiecetag"),anchor="c")
        #self.removepiece("piece5")
        
                
    def placepiece(self, name, row, column): #this does not do what you think it does, magically makes everything appear
        '''Place a piece at the given row/column'''
        self.pieces[name] = (row, column) #dictionary to place the pieces
        x0 = (column * self.size) + int(self.size/2)
        y0 = (row * self.size) + int(self.size/2)
        self.canvas.coords(name, x0, y0)
        
    def removepiece(self, name):
        #completely remove from board/game
        i = 0
        for sublist in Server.coordArrayX:
            if(sublist[0]==name):
                del Server.coordArrayX[i]
                Server.numCaptured = Server.numCaptured + 1
            i = i + 1
        i = 0
        for sublist in Server.coordArrayO:
            if(sublist[0]==name):
                del Server.coordArrayO[i]
            i = i + 1
        self.canvas.delete(name)
        #self.canvas.gettags(name)
        
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
        #also find piece in Server.coordArrayO        
        #replace the coordinates for that piece
        for sublist in Server.coordArrayX:
            if(sublist[0]==name):
                oldCoordX = sublist[1]
                oldCoordY = sublist[2]
                sublist[1] = destRow
                sublist[2] = destCol
                break
        for sublist in Server.coordArrayO:
            if(sublist[0]==name):
                oldCoordX = sublist[1]
                oldCoordY = sublist[2]
                sublist[1] = destRow
                sublist[2] = destCol
                break
        
        # print("new coordinates are: ", sublist[1], sublist[2])
        # print("old coordinates are: ", oldCoordX, oldCoordY)
        # print("Server.coordArrayX is: ", Server.coordArrayX)
        # print("Server.coordArrayO is: ", Server.coordArrayO)
        image_name = myList[1][0:-3]
        #print("image_name is", image_name)
        tag_name1 = myList[0]
        tag_name2 = myList[1]
        image_name = image_name + ".gif"
        #image_name = "redpiece.gif"
        # print(image_name)
        # print(tag_name1)
        # print(tag_name2)
        image_name = tk.PhotoImage(file=image_name) #blackpiece, technically can just hard code it
        #Relocate piece, not completely remove from board
        self.canvas.delete(name)
        xCoord = (destCol * self.size) + int(self.size/2)
        yCoord = (destRow * self.size) + int(self.size/2)
        #print("xCoord, yCoord", xCoord, yCoord)
        self.canvas.create_image(xCoord,yCoord,image=image_name, tags=(tag_name1, tag_name2),anchor="c")
        self.placepiece(image_name, 0, 0)
        # print("Server.coordArrayX is: ", Server.coordArrayX)
        # print("Server.coordArrayO is: ", Server.coordArrayO)          
        print("Exit movepiece")        
        


    def enable_callback(self):
        self.canvas.bind("<Button-1>", self.server_game_callback) #left-click
        self.canvas.bind("<Button-3>", self.server_game_callback) #right-click
    

        
    def server_game_callback(self, event):
        #basically binding of the O pieces and its movement from GUI are handled
        #print("clicked at", event.x, event.y)
        if((Server.turn_count)%2==1):
            if(self.click_counter == 0):
                if(Server_Gui.selected_piece == ""):
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
                                Server_Gui.selected_piece = Server.coordArrayO[my_piece_O][0]
                    self.click_counter = 1
                    return
                else:
                    print("MULTIPLE HOPS OCCURING RIGHT NOW!!! DEBUG THIS!")
                    #make sure the clicked piece is the same piece as Server_Gui.selected_piece
                    #if doing multiple hops
                    print("Server.coordArrayO is: ", Server.coordArrayO)
                    print(event.x, event.y)
                    self.old_x_coord = event.x
                    self.old_y_coord = event.y
                    #use self.compute_indices() to find the piece name
                    #self.old_O_piece_clicked = piece_name
                    my_index = self.compute_indices(event.x, event.y)
                    print(Server_Gui.selected_piece)
                    for my_piece_O in range(len(Server.coordArrayO)):
                        print("WE ARE HERE")
                        print(Server.coordArrayO[my_piece_O])
                        print(Server.coordArrayO[my_piece_O])
                        if(Server_Gui.selected_piece == Server.coordArrayO[my_piece_O][0]): #user smart
                           print("self.click_counter is 1 now")
                           self.click_counter = 1
                           return                                    
                    return #user dumb

                                
            if(self.click_counter == 1):
                self.click_counter = 0
                #use self.old_x_coord and self.old_y_coord
                #to determine piece name
                #self.movepiece(name, destRow, destCol)
                
                my_old_index = self.compute_indices(self.old_x_coord, self.old_y_coord) 
                my_index = self.compute_indices(event.x, event.y) #intention to move to
                
                
                #validate the red piece movement here
                #print("self.check_valid_move(Server_Gui.selected_piece,my_index, my_old_index) is: ", self.check_valid_move(Server_Gui.selected_piece,my_index, my_old_index))
                check_valid_move_result = self.check_valid_move(Server_Gui.selected_piece,my_index, my_old_index)
                if(check_valid_move_result!=0):
                    self.movepiece(Server_Gui.selected_piece, my_index[0], my_index[1])
                    if(check_valid_move_result[0]=="hop"):
                        print("Hoppity Hoppomus")
                        #print("my_index[0] my_index[1]: ", my_index)
                        #print(check_valid_move_result[1])
                        Server.pieces_to_remove.append(self.return_piece_name(check_valid_move_result[1]))
                        #print(Server.coordArrayX)
                        #print(Server.pieces_to_remove)
                        self.removepiece(self.return_piece_name(check_valid_move_result[1]))
                    if(my_index[0] == 0):
                        #delete the piece and replace with king piece
                        print("Making king piece now!")
                        myTags = self.canvas.gettags(Server_Gui.selected_piece)
                        #self.removepiece(Server_Gui.selected_piece)
                        self.canvas.delete(Server_Gui.selected_piece) #delete only the image
                        redking = tk.PhotoImage(file="redking.gif")
                        col = my_index[1]
                        row = my_index[0]
                        xCoord = (col * self.size) + int(self.size/2)
                        yCoord = (row * self.size) + int(self.size/2)
                        #inherit same piece name but replace second tag with "redkingtag"
                        self.canvas.create_image(xCoord,yCoord,image=redking, tags=(myTags[0], "redkingtag"),anchor="c")                        
                        self.placepiece(redking, 0, 0)
                        #store it in the data structure as well
                    print("Before sending it off!")        
                    if(self.has_valid_hops_left(Server_Gui.selected_piece, my_index, check_valid_move_result) == 0):
                        print("Sending it off now!")    
                        Server_Gui.moveflag = 1
                #self.movepiece(self.old_O_piece_clicked, my_index[0], my_index[1])
                
                # and Server_Gui.moveflag == 1
                # if(self.has_valid_hops_left(Server_Gui.selected_piece) == 0 and Server_Gui.moveflag == 1)
                #  self.check_valid_move(Server_Gui.selected_piece,my_index, my_old_index)==0
                #once that piece can no longer move, send the data over to other side
                if(Server_Gui.moveflag == 1):
                    print("******************************")
                    print("Sending Data Over Now!")
                    print("******************************")
                    Server_Gui.moveflag = 0
                    self.update_info_GUI()
                    Server_Gui.msg_to_send = [Server_Gui.selected_piece, [my_index[0], my_index[1]], Server.pieces_to_remove]
                    Server_Gui.selected_piece = ""
                    Server.pieces_to_remove = []                    
                    #Python Queue class are synchronized so we can
                    #"put" from any threads and it will be synchronized
                    #Server. or Server_Gui. Server_Queue.put(Server_Gui.msg_to_send)
                    Server.send_queue.put(Server_Gui.msg_to_send)
                    #Server.send_queue.join() This means that the queue is never being emptied
                    print("Contents in the queue:", Server.send_queue.qsize())
                    print("Server.coordArrayO", Server.coordArrayO)
                    print("Server.coordArrayX", Server.coordArrayX)                    
                    if(Server.numCaptured==12):
                        messagebox.showinfo("Congratulations!", "You won!")
                        self.running = 0
                        time.sleep(4)
                        sys.exit(0)
                return

    def check_valid_move(self, name, my_index, my_old_index): #I think first half works
        #checks if my_index is a valid move (as in if another hop is available), then return 1
        #if there is no valid move return 0
        #Algorithm:
        #check if two diagonal space is full, if so hop is not possible for that path
        #check if two diagonal space if empty and one diagonal space is appropriate piece, then return valid move
        #else check if one space traversal is possible, if so return valid move
        #else return 0
        result = 0
        list_of_possible_moves = [] #apply algorithm for max one hop length or one space traversal for that piece
                                    #check if my_index is in this list of possible moves, if so return 1, else return 0
        #print("Debugging check_valid_move")
        #print("my_index is: ", my_index)
        piece_type = self.return_piece_type(my_old_index)
        #print("piece_type is: ", piece_type)
        print("name of the piece is: ", name)
        if(piece_type == "redpiece"): #regular piece
            #print("In the if statement branch: ")
            index_array = []
            index_flag = []
            #  2    3
            #   0  1
            #    ||
            #print("x coord        , y_coord        : ")
            #print("my_old_index[1], my_old_index[0]: ", my_old_index[1], my_old_index[0])
            index0 = (my_old_index[1]-1, my_old_index[0]-1) #four possible moves for piece
            index1 = (my_old_index[1]+1, my_old_index[0]-1) #note [1] is col or x coord
            index2 = (my_old_index[1]-2, my_old_index[0]-2) #note [0] is row or y coord
            index3 = (my_old_index[1]+2, my_old_index[0]-2)
            index_array.append(index0)
            index_array.append(index1)
            index_array.append(index2)
            index_array.append(index3)
            #print("index_array is: ", index_array)
            for i in range(0,4):
                #set to be true until proven otherwise
                index_flag.append(1) #respective index corresponds to valid more or not
                
            for i in range(0,4): #determine all the illegal moves here
                #index out of bound
                # if(index_array[i][0]<0 or index_array[i][0]>7 or index_array[i][1]<0 or index_array[i][1]>7):
                    # index_flag[i] = 0
                
                if(i==0):                    #left side is ally piece
                    print("we are at i==0")
                    if(self.check_if_vacant(index_array[i]) == 0):
                        test_index = (index_array[i][1],index_array[i][0])   #way I wrote return_piece_type() expect flipped tuple                     
                        if((self.return_piece_type(test_index) == "redpiece") or (self.return_piece_type(test_index) == "redking")):
                            print("self.return_piece_type(index_array[i] is: ", self.return_piece_type(test_index))
                            print("branch 1 index0 index2: ", index0, index2)
                            index_flag[i] = 0
                            index_flag[i+2] = 0
                    #left side is completely blocked
                    if(self.check_if_vacant(index_array[i]) == 0 and self.check_if_vacant(index_array[i+2]) == 0):
                        print("branch2 index0 index2: ", index0, index2)
                        index_flag[i] = 0
                        index_flag[i+2] = 0
                    print("index_flag is: ", index_flag)
                
                if(i==1):
                    print("we are at i==1")
                    #right side is ally piece
                    if(self.check_if_vacant(index_array[i]) == 0):
                        #print("index_array[i] is: ", index_array[i])
                        test_index = (index_array[i][1],index_array[i][0])   #way I wrote return_piece_type() expect flipped tuple
                        if((self.return_piece_type(test_index) == "redpiece") or (self.return_piece_type(test_index) == "redking")):
                            #print("We get here xxxxxxxxxxxxx") #this branch is problem, why????
                            index_flag[i] = 0
                            index_flag[i+2] = 0
                    #right side is completely blocked                        
                    if(self.check_if_vacant(index_array[i]) == 0 and self.check_if_vacant(index_array[i+2]) == 0):
                        #print("We get here yyyyyyyyyyyyyy")
                        index_flag[i] = 0
                        index_flag[i+2] = 0  
                    print("index_flag is: ", index_flag)
                #left most side is not vacant
                if(i==2):
                    print("we are at i==2")
                    if(self.check_if_vacant(index_array[i]) == 0):
                        index_flag[i] = 0
                    if(self.check_if_vacant(index_array[i-2]) == 1): #if preceding space is empty can't hop to this
                        index_flag[i] = 0
                    print("index_flag is: ", index_flag)
                #right most side is not vacant
                if(i==3):
                    print("we are at i==3")
                    if(self.check_if_vacant(index_array[i]) == 0):
                        index_flag[i] = 0
                    if(self.check_if_vacant(index_array[i-2]) == 1): #if preceding space is empty can't hop to this
                        index_flag[i] = 0                    
                    print("index_flag is: ", index_flag)
                    
            print("index_flag is: ", index_flag)
            #print("Expected index_flag is:  [1, 1, 0, 0]")
            for i in range(0,4): #check all valid moves
                print("entered loop")
                if(index_flag[i] == 1):
                    list_of_possible_moves.append(index_array[i])
                    print("index_array[i], my_index[1], my_index[0]", index_array[i], my_index[1], my_index[0])
                    if(index_array[i] == (my_index[1], my_index[0])): #is the requested move one of the valid moves?
                        #and which move type?
                        if(i<2):
                            result = "move"
                        if(i==2): #leftmost to center
                            num1 = my_index[0]+1
                            num2 = my_index[1]+1
                            result = ("hop",(num1, num2)) #values which are index of piece to remove
                        if(i==3): #rightmost to center
                            num3 = my_index[0]+1
                            num4 = my_index[1]-1
                            result = ("hop",(num3, num4))                        
            #print("my_index[0], my_index[1]: ", my_index[0], my_index[1])
            #print("index_array: ", index_array)
            #print("We made it to the end of check_valid_move()! ")
            print("result is: ", result)
        elif(piece_type == "redking"): #king piece
            print("Detected redking movement!")
            index_array = []
            index_flag = []
            #  2    3
            #   0  1
            #    ||
            #   4  5
            #  6    7
            #index 0 to 3 are upward moves wrt piece user
            #index 4 to 7 are downword moves wrt piece user
            index0 = (my_old_index[1]-1, my_old_index[0]-1) #eight possible moves for piece
            index1 = (my_old_index[1]+1, my_old_index[0]-1)
            index2 = (my_old_index[1]-2, my_old_index[0]-2)
            index3 = (my_old_index[1]+2, my_old_index[0]-2)
            index4 = (my_old_index[1]-1, my_old_index[0]+1)
            index5 = (my_old_index[1]+1, my_old_index[0]+1)
            index6 = (my_old_index[1]-2, my_old_index[0]+2)
            index7 = (my_old_index[1]+2, my_old_index[0]+2) 
            index_array.append(index0)
            index_array.append(index1)
            index_array.append(index2)
            index_array.append(index3)
            index_array.append(index4)
            index_array.append(index5)
            index_array.append(index6)
            index_array.append(index7)
            for i in range(0,8):
                #set to be true until proven otherwise
                index_flag.append(1) #respective index corresponds to valid more or not
            for i in range(0,8):
                if(i==0):                    #upward, left side is ally piece
                    #print("we are at i==0")
                    if(self.check_if_vacant(index_array[i]) == 0):
                        test_index = (index_array[i][1],index_array[i][0])   #way I wrote return_piece_type() expect flipped tuple
                        if((self.return_piece_type(test_index) == "redpiece") or (self.return_piece_type(test_index) == "redking")):
                            index_flag[i] = 0
                            index_flag[i+2] = 0
                    #left side is completely blocked
                    if(self.check_if_vacant(index_array[i]) == 0 and self.check_if_vacant(index_array[i+2]) == 0):
                        index_flag[i] = 0
                        index_flag[i+2] = 0
                    #print("index_flag is: ", index_flag)
                if(i==1):                    #upward, right side is ally piece
                    #print("we are at i==1")
                    #right side is ally piece
                    if(self.check_if_vacant(index_array[i]) == 0):
                        #print("index_array[i] is: ", index_array[i])
                        test_index = (index_array[i][1],index_array[i][0])   #way I wrote return_piece_type() expect flipped tuple
                        if((self.return_piece_type(test_index) == "redpiece") or (self.return_piece_type(test_index) == "redking")):
                            #print("We get here xxxxxxxxxxxxx") #this branch is problem, why????
                            index_flag[i] = 0
                            index_flag[i+2] = 0
                    #right side is completely blocked                        
                    if(self.check_if_vacant(index_array[i]) == 0 and self.check_if_vacant(index_array[i+2]) == 0):
                        #print("We get here yyyyyyyyyyyyyy")
                        index_flag[i] = 0
                        index_flag[i+2] = 0  
                    #print("index_flag is: ", index_flag)                    
                if(i==2):                    #upward, left most side is not vacant
                    #print("we are at i==2")     
                    if(self.check_if_vacant(index_array[i]) == 0):
                        index_flag[i] = 0
                    if(self.check_if_vacant(index_array[i-2]) == 1): #if preceding space is empty can't hop to this
                        index_flag[i] = 0
                    #print("index_flag is: ", index_flag)
                if(i==3):                    #upward, right most side is not vacant
                    #print("we are at i==3")    
                    if(self.check_if_vacant(index_array[i]) == 0):
                        index_flag[i] = 0
                    if(self.check_if_vacant(index_array[i-2]) == 1): #if preceding space is empty can't hop to this
                        index_flag[i] = 0                    
                    #print("index_flag is: ", index_flag)                    
                if(i==4):                    #downward, left side is ally piece
                    #print("we are at i==4")     
                    if(self.check_if_vacant(index_array[i]) == 0):
                        test_index = (index_array[i][1],index_array[i][0])   #way I wrote return_piece_type() expect flipped tuple
                        if((self.return_piece_type(test_index) == "redpiece") or (self.return_piece_type(test_index) == "redking")):
                            index_flag[i] = 0
                            index_flag[i+2] = 0
                    #left side is completely blocked
                    if(self.check_if_vacant(index_array[i]) == 0 and self.check_if_vacant(index_array[i+2]) == 0):
                        index_flag[i] = 0
                        index_flag[i+2] = 0
                    #print("index_flag is: ", index_flag)
                if(i==5):                    #downward, right side is ally piece
                    #print("we are at i==5")
                    #right side is ally piece
                    if(self.check_if_vacant(index_array[i]) == 0):
                        #print("index_array[i] is: ", index_array[i])
                        test_index = (index_array[i][1],index_array[i][0])   #way I wrote return_piece_type() expect flipped tuple
                        if((self.return_piece_type(test_index) == "redpiece") or (self.return_piece_type(test_index) == "redking")):
                            #print("We get here xxxxxxxxxxxxx") #this branch is problem, why????
                            index_flag[i] = 0
                            index_flag[i+2] = 0
                    #right side is completely blocked                        
                    if(self.check_if_vacant(index_array[i]) == 0 and self.check_if_vacant(index_array[i+2]) == 0):
                        #print("We get here yyyyyyyyyyyyyy")
                        index_flag[i] = 0
                        index_flag[i+2] = 0  
                    #print("index_flag is: ", index_flag)                     
                if(i==6):                    #downward, left most side is not vacant
                    print("we are at i==6")     
                    if(self.check_if_vacant(index_array[i]) == 0):
                        index_flag[i] = 0
                    if(self.check_if_vacant(index_array[i-2]) == 1): #if preceding space is empty can't hop to this
                        index_flag[i] = 0
                    #print("index_flag is: ", index_flag)
                if(i==7):                    #downward, right most side is not vacant
                    print("we are at i==7")   
                    if(self.check_if_vacant(index_array[i]) == 0):
                        index_flag[i] = 0
                    if(self.check_if_vacant(index_array[i-2]) == 1): #if preceding space is empty can't hop to this
                        index_flag[i] = 0                    
                    #print("index_flag is: ", index_flag)   

            for i in range(0,8): #check all valid moves        
                if(index_flag[i] == 1):
                    list_of_possible_moves.append(index_array[i])
                    if(index_array[i] == (my_index[1], my_index[0])): #is the requested move one of the valid moves?
                        #and which move type?
                        if(i==0 or i==1):
                            result = "move"
                        if(i==2): #leftmost to center
                            num1 = my_index[0]+1
                            num2 = my_index[1]+1
                            result = ("hop",(num1, num2)) #values which are index of piece to remove
                        if(i==3): #rightmost to center
                            num1 = my_index[0]+1
                            num2 = my_index[1]-1
                            result = ("hop",(num1, num2))
                        if(i==4 or i == 5):
                            result = "move"
                        if(i==6):
                            num1 = my_index[0]-1
                            num2 = my_index[1]+1
                            result = ("hop",(num1, num2)) #values which are index of piece to remove
                        if(i==7):
                            num1 = my_index[0]-1
                            num2 = my_index[1]-1
                            result = ("hop",(num1, num2))
        print("result is: ", result)             
        print("Exitting check_valid_move()")
        return result
    
    def has_valid_hops_left(self, name, my_index, prev_move_type):
        #checks from the current location of the piece whether it has any valid hops left
        #returns a boolean 0 or 1
        print("has_valid_hops_left() current location: ", my_index)
        result = 0
        piece_type = self.return_piece_type(my_index)
        if(piece_type == "redpiece"): #regular piece
            index_array = []
            index_flag = []
            #  2    3
            #   h  h
            #    ||
            #print("x coord        , y_coord        : ")
            #print("my_index[1], my_index[0]: ", my_index[1], my_index[0])
            index0 = (my_index[1]-1, my_index[0]-1) #four possible moves for piece
            index1 = (my_index[1]+1, my_index[0]-1) #note [1] is col or x coord, note [0] is row or y coord
            index2 = (my_index[1]-2, my_index[0]-2) #hop #1
            index3 = (my_index[1]+2, my_index[0]-2) #hop #2
            index_array.append(index0)
            index_array.append(index1)
            index_array.append(index2)
            index_array.append(index3)
            #print("index_array is: ", index_array)
            for i in range(0,4):
                #set to be true until proven otherwise
                index_flag.append(1) #respective index corresponds to valid more or not            

            for i in range(0,4): #determine all the illegal moves here
                #index out of bound
                # if(index_array[i][0]<0 or index_array[i][0]>7 or index_array[i][1]<0 or index_array[i][1]>7):
                    # index_flag[i] = 0
                
                if(i==0):                    #left side is ally piece
                    index_flag[i] = 0
                if(i==1):
                    index_flag[i] = 0
                if(i==2):
                    #print("we are at i==2")
                    if(self.check_if_vacant(index_array[i]) == 0):
                        index_flag[i] = 0
                    if(self.check_if_vacant(index_array[i-2]) == 1): #if preceding space is empty can't hop to this
                        index_flag[i] = 0
                    #print("index_flag is: ", index_flag)
                #right most side is not vacant
                if(i==3):
                    #print("we are at i==3")
                    if(self.check_if_vacant(index_array[i]) == 0):
                        index_flag[i] = 0
                    if(self.check_if_vacant(index_array[i-2]) == 1): #if preceding space is empty can't hop to this
                        index_flag[i] = 0                    
                    #print("index_flag is: ", index_flag)
                    
            #print("index_flag is: ", index_flag)
            #print("Expected index_flag is:  [1, 1, 0, 0]")
            for i in range(0,4): #check all valid moves        
                result = result + index_flag[i]                    
            #print("my_index[0], my_index[1]: ", my_index[0], my_index[1])
            #print("index_array: ", index_array)
            #print("We made it to the end of has_valid_hops_left()! ")
            if(prev_move_type=="move"):
                result = 0
            

        elif(piece_type == "redking"): #king piece
            print("Detected redking movement!")
            index_array = []
            index_flag = []
            #  2    3
            #   0  1
            #    ||
            #   4  5
            #  6    7
            index0 = (my_index[1]-1, my_index[0]-1) #four possible moves for piece
            index1 = (my_index[1]+1, my_index[0]-1)
            index2 = (my_index[1]-2, my_index[0]-2)
            index3 = (my_index[1]+2, my_index[0]-2)
            index4 = (my_index[1]-1, my_index[0]+1)
            index5 = (my_index[1]+1, my_index[0]+1)
            index6 = (my_index[1]-2, my_index[0]+2)
            index7 = (my_index[1]+2, my_index[0]+2) 
            index_array.append(index0)
            index_array.append(index1)
            index_array.append(index2)
            index_array.append(index3)
            index_array.append(index4)
            index_array.append(index5)
            index_array.append(index6)
            index_array.append(index7)
            
            for i in range(0,8):
                #set to be true until proven otherwise
                index_flag.append(1) #respective index corresponds to valid more or not            

            for i in range(0,8): #determine all the illegal moves here
                #index out of bound
                # if(index_array[i][0]<0 or index_array[i][0]>7 or index_array[i][1]<0 or index_array[i][1]>7):
                    # index_flag[i] = 0
                
                if(i==0):                    #left side is ally piece
                    index_flag[i] = 0
                if(i==1):
                    index_flag[i] = 0
                if(i==2):   #upward, left most side is not vacant
                    #print("we are at i==2")
                    if(self.check_if_vacant(index_array[i]) == 0):
                        index_flag[i] = 0
                    if(self.check_if_vacant(index_array[i-2]) == 1): #if preceding space is empty can't hop to this
                        index_flag[i] = 0
                    test_index = (index_array[i-2][1],index_array[i-2][0])   #way I wrote return_piece_type() expect flipped tuple
                    if((self.return_piece_type(test_index) == "redpiece") or (self.return_piece_type(test_index) == "redking")):
                        index_flag[i] = 0
                    #print("index_flag is: ", index_flag)
                #right most side is not vacant
                if(i==3):   #upward, right most side is not vacant
                    #print("we are at i==3")
                    if(self.check_if_vacant(index_array[i]) == 0):
                        index_flag[i] = 0
                    if(self.check_if_vacant(index_array[i-2]) == 1): #if preceding space is empty can't hop to this
                        index_flag[i] = 0
                    test_index = (index_array[i-2][1],index_array[i-2][0])   #way I wrote return_piece_type() expect flipped tuple
                    if((self.return_piece_type(test_index) == "redpiece") or (self.return_piece_type(test_index) == "redking")):
                        index_flag[i] = 0                        
                    #print("index_flag is: ", index_flag)
                if(i==4):
                    index_flag[i] = 0
                if(i==5):
                    index_flag[i] = 0
                if(i==6):   #downward, left most side is not vacant
                    print("we are at i==6")
                    print(self.check_if_vacant(index_array[i]))
                    if(self.check_if_vacant(index_array[i]) == 0):
                        index_flag[i] = 0
                    print(self.check_if_vacant(index_array[i-2]))    
                    if(self.check_if_vacant(index_array[i-2]) == 1): #if preceding space is empty can't hop to this
                        index_flag[i] = 0
                    test_index = (index_array[i-2][1],index_array[i-2][0])   #way I wrote return_piece_type() expect flipped tuple
                    if((self.return_piece_type(test_index) == "redpiece") or (self.return_piece_type(test_index) == "redking")):
                        index_flag[i] = 0
                    #print("index_flag is: ", index_flag)                
                if(i==7):
                    print("we are at i==7")
                    if(self.check_if_vacant(index_array[i]) == 0):
                        index_flag[i] = 0
                    if(self.check_if_vacant(index_array[i-2]) == 1): #if preceding space is empty can't hop to this
                        index_flag[i] = 0
                    test_index = (index_array[i-2][1],index_array[i-2][0])   #way I wrote return_piece_type() expect flipped tuple
                    if((self.return_piece_type(test_index) == "redpiece") or (self.return_piece_type(test_index) == "redking")):
                        index_flag[i] = 0                        
                    #print("index_flag is: ", index_flag)
                    
            #print("index_flag is: ", index_flag)
            #print("Expected index_flag is:  [1, 1, 0, 0]")
            for i in range(0,8): #check all valid moves        
                result = result + index_flag[i]                    
            #print("my_index[0], my_index[1]: ", my_index[0], my_index[1])
            #print("index_array: ", index_array)
            #print("We made it to the end of has_valid_hops_left()! ")            
            if(prev_move_type=="move"):
                result = 0
        print("prev_move_type is: ", prev_move_type)
        print("result is: ", result, "index_flag is: ", index_flag)
        print("Exitting has_valid_hops_left()")         
        return result
        
        
    def return_piece_name(self, my_index):
        #print("return_piece_name")
        #print("my_index is: ", my_index)
        result = "" #no piece exists
        #print("my_index[0], my_index[1]", my_index[0], my_index[1])
        for my_piece_O in range(len(Server.coordArrayO)):
            if((my_index[0]) == Server.coordArrayO[my_piece_O][1]):
                if(my_index[1] == Server.coordArrayO[my_piece_O][2]):
                    result = Server.coordArrayO[my_piece_O][0]    #returns piece# like piece15
                    print("piece_name is:", result)
                    break
        for my_piece_X in range(len(Server.coordArrayX)):
            if((my_index[0]) == Server.coordArrayX[my_piece_X][1]):
                if(my_index[1] == Server.coordArrayX[my_piece_X][2]):
                    result = Server.coordArrayX[my_piece_X][0]    #returns piece# like piece4
                    print("piece_name is:", result)
                    break
        return result
                    
    def return_piece_type(self, my_index):
        #print("return_piece_type")
        #print("my_index is: ", my_index)
        name = self.return_piece_name(my_index)
        temp = self.canvas.gettags(name)
        
        #print("temp is: ", temp)
        #print("temp[1] is: ", temp[1])
        result = "" #no piece exists
        if(len(temp)==2):
            if(temp[1] == "blackpiecetag"):
                result = "blackpiece"
            if(temp[1] == "redpiecetag"):
                result = "redpiece"
            if(temp[1] == "blackkingtag"):
                result = "blackking"
            if(temp[1] == "redkingtag"):
                result = "redking"
        
        return result        
        
    def check_if_vacant(self, my_index):
        vacant_flag = 1
        #my_index[1] my_index[0] is row col
        #print("my_index: ", my_index)
        for my_piece_O in range(len(Server.coordArrayO)):
            #print(Server.coordArrayO[my_piece_O][1], Server.coordArrayO[my_piece_O][2])
            if(my_index[1] == Server.coordArrayO[my_piece_O][1]):
                if(my_index[0] == Server.coordArrayO[my_piece_O][2]):
                    vacant_flag = 0
                    return vacant_flag
                    
        for my_piece_X in range(len(Server.coordArrayX)):
            #print(Server.coordArrayX[my_piece_X][1], Server.coordArrayX[my_piece_X][2])
            if(my_index[1] == Server.coordArrayX[my_piece_X][1]):
                if(my_index[0] == Server.coordArrayX[my_piece_X][2]):
                    vacant_flag = 0
                    return vacant_flag    
        return vacant_flag    
        
    def game_on(self):
        self.click_counter = 0
        self.old_x_coord = 0
        self.old_y_coord = 0
        self.old_O_piece_clicked = ""
        self.enable_callback()
        #we want to bind player presses to the board and act accordingly
    
    #Alternatively
    # def compute_indices(self, x_coord, y_coord):
        # #given pixel values, return row and y  values as tuple
        # x_val = 0
        # y_val = 0
        # for i in range(8, 0, -1):
            # if(y_coord < 40*i):
                # y_val = i
            # if(x_coord < 40*i):
                # x_val = i
        
        # return(y_val, x_val)    
    def compute_indices(self, x_coord, y_coord):
        #given pixel values, return y and x values as tuple
        #unfortunately, it is more appropriate for make it a x and y tuple
        #but due to functions that have (row, col) as parameter,
        #we decided to match the order
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
    def init_info_GUI(self):
        #instantiate the components 
        self.label_text1 = "Timer: " + str(self.gameTime)
        self.label_text2 = "Turn Counter: " + str(Server.turn_count)
        self.label_text3 = "Num Pieces Captured: " + str(Server.numCaptured)

        self.GUI_Button1 = tk.Button(self.canvas, text='Rules', command=self.printRules)
        self.GUI_Button1.grid(padx = 450, pady = 0, row = 1, column = 1)
        self.TIMER_Label = tk.Label(self.canvas, text=self.label_text1)
        self.TIMER_Label.grid(padx = 0, row = 2, column = 1)
        self.GUI_Label2 = tk.Label(self.canvas, text=self.label_text2)
        self.GUI_Label2.grid(padx = 0, row = 3, column = 1)
        self.GUI_Label3 = tk.Label(self.canvas, text=self.label_text3)
        self.GUI_Label3.grid(padx = 0, row = 4, column = 1)

        self.GUI_Button = tk.Button(self.canvas, text='Exit', command=self.endCommand)
        self.GUI_Button.grid(padx = 0, row = 10, column = 1)#(side=tk.RIGHT)
        
        # self.testButton = tk.Button(self.master, text='Hello', command=self.printHello)
        # self.testButton.pack()
        # self.testIOdata = tk.Label(self.master, textvariable = self.label_text1)
        # self.testIOdata.pack()
        # self.label_text1.set("Hello Idiot")
        
    def update_info_GUI(self):
        self.label_text2 = "Turn Counter: " + str(Server.turn_count)
        self.label_text3 = "Num Pieces Captured: " + str(Server.numCaptured)
        
        self.GUI_Label2.config(text = self.label_text2)
        self.GUI_Label3.config(text = self.label_text3)


    def printHello(self):
        self.label_text1Count+=1
        print("Hello World!")
        if(self.label_text1Count%2 == 1):
            self.label_text1.set("Test")
        else:
            self.label_text1.set("Not Test")
            
        print("Set new text")
    
    def printRules(self):
        messagebox.showinfo("Rules", "Move your checker pieces diagonally\n and capture their pieces!")
        os.startfile('images\Rules.png')
        
    def one_sec_counter(self, label):
        counter = count(0)
        def update_func():
            label.config(text="Timer: " + str(next(counter)) + " sec")
            label.after(1100, update_func) #after 1 sec or 1000 ms
            #this uses recursion
        update_func()
        
    def processIncoming(self):
        """Handle all messages currently in the queue, if any."""
        #print("Server.recv_queue.qsize() is: ", Server.recv_queue.qsize())
        while Server.recv_queue.qsize():
            try:
                msg = self.recv_queue.get(0)
                # Check contents of message and do whatever is needed. As a
                # simple test, print it (in real life, you would
                # suitably update the GUI's display in a richer fashion).
                decoded_msg = pickle.loads((msg))
                #print("decoded_msg is: ", decoded_msg)
                self.client_moved_piece = decoded_msg[0]
                self.client_new_piece_coord = decoded_msg[1]
                self.client_removed_pieces = decoded_msg[2]
                # print("Printing my message", self.client_moved_piece)
                # print("Printing my message", self.client_new_piece_coord)
                # print("Printing my message", self.client_removed_pieces)
                self.movepiece(self.client_moved_piece, 7 - self.client_new_piece_coord[0], 7 - self.client_new_piece_coord[1])
                #print("We are here")
                if(len(self.client_removed_pieces)>0):
                    #print("Trying to remove content")
                    for piece_name in self.client_removed_pieces:
                        self.removepiece(piece_name)
                        Server.numRemaining = Server.numRemaining - 1
                if(self.client_new_piece_coord[0] == 0):
                    myTags = self.canvas.gettags(self.client_moved_piece)
                    #self.removepiece(self.client_moved_piece)
                    self.canvas.delete(self.client_moved_piece)
                    #print("Time to make a king piece!!!")                    
                    blackking = tk.PhotoImage(file="blackking.gif")
                    col = 7 - self.client_new_piece_coord[1]
                    row = 7 - self.client_new_piece_coord[0]
                    #print("col row is: ", col, row)
                    xCoord = (col * self.size) + int(self.size/2)
                    yCoord = (row * self.size) + int(self.size/2)
                    self.canvas.create_image(xCoord,yCoord,image=blackking, tags=(self.client_moved_piece, "blackkingtag"),anchor="c")
                    self.placepiece(blackking, 0, 0)
                #print("Server.coordArrayX is: ", Server.coordArrayX)
                #print("Server.coordArrayO is: ", Server.coordArrayO)                
                self.GUI_Label2.config(text="Turn Counter: " + str(Server.turn_count))
                if(Server.numRemaining==0):
                    messagebox.showinfo("You Lost.", "Good Luck Next Time!")
                    self.running = 0
                    time.sleep(4)
                    sys.exit(0)
                print("Server.coordArrayO", Server.coordArrayO)
                print("Server.coordArrayX", Server.coordArrayX)                    
                print("Exitted processIncoming()")
            except:
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
        
        Server.numCaptured = 0
        Server.numRemaining = 12
        Server.turn_count = 1
        Server.pieces_to_remove = []
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
        # also note this initialization is done in GUI side
        Server.coordArrayX = [["piece1",0,1],["piece2",0,3],["piece3",0,5],["piece4",0,7], 
                        ["piece5",1,0], ["piece6",1,2], ["piece7",1,4], ["piece8",1,6],
                        ["piece9",2,1],["piece10",2,3],["piece11",2,5],["piece12",2,7]]
        Server.coordArrayO = [["piece13",5,0],["piece14",5,2],["piece15",5,4],["piece16",5,6], 
                        ["piece17",6,1], ["piece18",6,3], ["piece19",6,5], ["piece20",6,7],
                        ["piece21",7,0],["piece22",7,2],["piece23",7,4],["piece24",7,6]]

                        

        #####################################################
 
    def setup_Gui(self):
        self.master = tk.Tk() #master = root
        self.master.title("Checkers: Server")
        self.master.minsize(width=640, height=320)
        self.master.maxsize(width=640, height=320)
        self.master.iconbitmap('fireball.ico')
        #Create Queue for I/O communication
        Server.recv_queue = queue.Queue() #Queue() class
        Server.send_queue = queue.Queue()
        #Setup GUI here (includes the Checkerboard)
        self.gui = Server_Gui(self.master, Server.recv_queue, Server.send_queue, self.endGame)
        
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
        #print("Size of recv_queue is: ", Server.recv_queue.qsize())
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
            Server.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Get socket layer socket options.
            Server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Bind socket to socket address, i.e., IP address and port.
            Server.socket.bind( (Server.HOSTNAME, Server.PORT) )

            # Set socket to listen state.
            Server.socket.listen(Server.BACKLOG)
            
            #Set socket to non-blocking
            #Server.socket.setblocking(False)
            
            #Set socket timeout to 0.2 sec or 200 ms
            #Server.socket.settimeout(0.2)

            print("Listening on port {} ...".format(Server.PORT))

        except Exception as msg:
            print(msg)
            sys.exit(1)

    def process_connections_forever(self):
        while True:
            try:
                while True:
                    # Block while waiting for accepting incoming
                    # connections. When one is accepted, pass the new
                    # (cloned) socket reference to the connection handler
                    # function.
                    self.connection_handler(Server.socket.accept())

            except Exception as msg:
                print(msg)
            except KeyboardInterrupt:
                print()
            except TimeoutError:
                print("TimeoutError! That's good passing")
                pass
            finally:
                print("just casually passing from finally block")
                pass
                print("Closing server socket ...")
                self.socket.close()
                sys.exit(1)

    def connection_handler(self, client):
        connection, address_port = client
        print("-" * 72)
        print("Connection received from {}.".format(address_port))
        while True:
            #print("In process_connections_forever()!!!")
            if(Server.send_queue.qsize()): #aka Server_queue
                # here we need to make another queue just for the
                # server gui class and server to be able to communicate
                # this block is for sending only!!!
                # other queue is for receiving only!!!
                #elif(Server_Gui.send_msg_flag == 1): #sending
                #Here we want to send the checker data
                #print("Sending Server data to Client!")
                data_to_send = Server.send_queue.get() #ie: list = ["piece5",[2,4],["piece5","piece9"],5]
                
                #below cannot work for decode(utf-8)
                #since it only supports strings, not dynamic data type like above
                pickled_byte_msg = pickle.dumps(data_to_send) #pickled into byte object
                # Send the received bytes back to the client.
                connection.sendall(pickled_byte_msg)
                print("Sent: ", data_to_send)
                print("Contents in the queue: ", Server.send_queue.qsize())
                Server.turn_count = Server.turn_count + 1
            elif((Server.turn_count)%2==0): #I CAN CHEAT THE SYSTEM AND AVOID DEALING WITH THREADING BY DOING BASIC BOOKKEEPING PROPERLY LUL
                #IF TURN_COUNT%2==0 (EVEN) THEN BLOCK HERE SINCE WE KNOW WE SHOULD EXPECT SOME OUTPUT FROM CLIENT
                #pass
                #print("HELLO WORLD!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                #time.sleep(5)
                print("******************************")
                print("Receiving Data Right Now!!!!!!!!! xDDDDDDDDDD")
                print("******************************")
                pickled_data = connection.recv(1024)
                #print("the unpickled data is: ", pickle.loads(pickled_data))
                Server.recv_queue.put(pickled_data)
                print("Size of Server.recv_queue is: ", Server.recv_queue.qsize())
                Server.turn_count = Server.turn_count + 1
                #time.sleep(1) #delay for a bit so the system bookkeeping variable can sync up
                #break #since we got the data break out forcefully, we can QA later and see if we do need this, we shouldnt i think
                # try:
                    # self.connection_receive(connection)
                # except TimeoutError:
                    # print("Time outy boiiiiiiiiii!")
                    # pass
            
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
    


            
########################################################################
# GUI Client class
########################################################################
class Client_Gui:
    def __init__(self, master, recv_queue, send_queue, endCommand):
        Client_Gui.send_msg_flag = 0
        Client_Gui.msg_to_send = []
        Client_Gui.selected_piece = ""
        Client_Gui.moveflag = 0
        self.recv_queue = recv_queue
        self.master = master
        self.endCommand = endCommand
        self.label_text1 = tk.StringVar()
        self.label_text2 = tk.StringVar()
        self.label_text3 = tk.StringVar()
        self.gameTime = 0
        # Set up the GUI
        self.init_board_GUI()
        self.init_info_GUI()
        self.one_sec_counter(self.TIMER_Label)
        
    def init_board_GUI(self):
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
                
    def populate_pieces(self):
        #Tkinter compatible data (gif)
        blackking = tk.PhotoImage(file="blackking.gif")
        blackpiece = tk.PhotoImage(file="blackpiece.gif")
        redking = tk.PhotoImage(file="redking.gif")
        redpiece = tk.PhotoImage(file="redpiece.gif")
        #initial population of all the pieces for server side
        init_coordArrayX = {(7,6),(7,4),(7,2),(7,0),
                            (6,7),(6,5), (6,3), (6,1),
                            (5,6), (5,4),(5,2),(5,0)}
        init_coordArrayO = {(2,7),(2,5),(2,3),(2,1),
                            (1,6),(1,4),(1,2),(1,0),
                            (0,7), (0,5), (0,3),(0,1),}
        pieceCounter = 24 #this needs to start from max and decrement down since we flipped everything!!!!!
        
        for row in range(8):
            for col in range(8):
                if (row,col) in init_coordArrayX:
                    xCoord = (col * self.size) + int(self.size/2)
                    yCoord = (row * self.size) + int(self.size/2)
                    self.canvas.create_image(xCoord,yCoord,image=blackpiece, tags=("piece"+str(pieceCounter), "blackpiecetag"),anchor="c")
                    pieceCounter = pieceCounter - 1
                elif (row,col) in init_coordArrayO:
                    xCoord = (col * self.size) + int(self.size/2)
                    yCoord = (row * self.size) + int(self.size/2)
                    self.canvas.create_image(xCoord,yCoord, image=redpiece, tags=("piece"+str(pieceCounter), "redpiecetag"),anchor="c")
                    pieceCounter = pieceCounter - 1
        print("Populated pieces, pieceCounter at end is: "+ str(pieceCounter))
        self.placepiece(blackpiece, 0, 0)
        self.placepiece(redpiece, 0, 0)
        
      

    def placepiece(self, name, row, column): #this does not do what you think it does, magically makes everything appear
        '''Place a piece at the given row/column'''
        self.pieces[name] = (row, column) #dictionary to place the pieces
        x0 = (column * self.size) + int(self.size/2)
        y0 = (row * self.size) + int(self.size/2)
        self.canvas.coords(name, x0, y0)
        #print("coordinates x0 and y0: ", x0, y0)       

    def removepiece(self, name):
        #completely remove from board/game
        i = 0
        for sublist in Client.coordArrayX:
            if(sublist[0]==name):
                del Client.coordArrayX[i]
            i = i + 1
        i = 0
        for sublist in Client.coordArrayO:
            if(sublist[0]==name):
                del Client.coordArrayO[i]
                Client.numCaptured = Client.numCaptured + 1                
            i = i + 1
        #print("removepiece() ", name, " from game")
        self.canvas.delete(name)
        #self.canvas.gettags(name)

    def movepiece(self, name, destRow, destCol): 
        #remove and place aka move piece
        
        # blackpiece = tk.PhotoImage(file="blackpiece.gif")
        # self.canvas.delete(name)
        # self.canvas.create_image(300,300, image=blackpiece, tags=("piece2", "blackpiecetag"),anchor="c")
        # self.placepiece(blackpiece, 0, 0)
        
        #GUI Portion of movepiece (frontend)
        #Store data
        #print("name is: "+name)
        myList = self.canvas.gettags(name)
        #find current location in the board
        for sublist in Client.coordArrayX:
            if(sublist[0]==name):
                #print("Match in Client.coordArrayX")
                oldCoordX = sublist[1]
                oldCoordY = sublist[2]
                sublist[1] = destRow
                sublist[2] = destCol
                break
        for sublist in Client.coordArrayO:
            if(sublist[0]==name):
                #print("Match in Client.coordArrayO")
                oldCoordX = sublist[1]
                oldCoordY = sublist[2]
                sublist[1] = destRow
                sublist[2] = destCol
                break
                
        # print("old coordinates are: ", oldCoordX, oldCoordY) 
        # print("new coordinates are: ", sublist[1], sublist[2])
        # print("Client.coordArrayX is: ", Client.coordArrayX)
        # print("Client.coordArrayO is: ", Client.coordArrayO)               

        image_name = myList[1][0:-3]
        # print("image_name is", image_name)
        tag_name1 = myList[0]
        tag_name2 = myList[1]
        image_name = image_name + ".gif"
        # print(image_name)
        # print(tag_name1)
        # print(tag_name2)
        image_name = tk.PhotoImage(file=image_name) #blackpiece, technically can just hard code it
        #Remove piece
        #print("name is:" + name)
        self.canvas.delete(name)
        xCoord = (destCol * self.size) + int(self.size/2)
        yCoord = (destRow * self.size) + int(self.size/2)
        #print("xCoord, yCoord", xCoord, yCoord)
        self.canvas.create_image(xCoord,yCoord,image=image_name, tags=(tag_name1, tag_name2),anchor="c")
        self.placepiece(image_name, 0, 0)
        #print("Client.coordArrayX is: ", Client.coordArrayX)
        #print("Client.coordArrayO is: ", Client.coordArrayO)
        print("Exit movepiece()")
      
            
    def enable_callback(self):
        self.canvas.bind("<Button-1>", self.client_game_callback) #left-click
        self.canvas.bind("<Button-3>", self.client_game_callback) #right-click
        
    def client_game_callback(self, event):
        #basically binding of the X pieces and its movement from GUI are handled
        #print("clicked at", event.x, event.y)
        if(Client.turn_count%2 == 0):
            if(self.click_counter == 0):
                if(Client_Gui.selected_piece == ""):
                    #pick a black piece
                    self.old_x_coord = event.x
                    self.old_y_coord = event.y
                    #use self.compute_indices() to find the piece name
                    #self.old_O_piece_clicked = piece_name
                    my_index = self.compute_indices(event.x, event.y)
                    for my_piece_X in range(len(Client.coordArrayX)):
                        if(my_index[0] == Client.coordArrayX[my_piece_X][1]):
                            if(my_index[1] == Client.coordArrayX[my_piece_X][2]):
                                self.old_X_piece_clicked = Client.coordArrayX[my_piece_X][0]
                                Client_Gui.selected_piece = Client.coordArrayX[my_piece_X][0]
                    self.click_counter = 1
                    return
                else:
                    #make sure the clicked piece is the same piece as Client_Gui.selected_piece
                    #if doing multiple hops
                    self.old_x_coord = event.x
                    self.old_y_coord = event.y
                    #use self.compute_indices() to find the piece name
                    #self.old_O_piece_clicked = piece_name
                    my_index = self.compute_indices(event.x, event.y)
                    for my_piece_X in range(len(Client.coordArrayX)):
                        if(Client_Gui.selected_piece == Client.coordArrayX[my_piece_X][0]): #user smart
                           self.click_counter = 1
                           return
                    return #user dumb                   
            if(self.click_counter == 1):
                self.click_counter = 0
                #use self.old_x_coord and self.old_y_coord
                #to determine piece name
                #self.movepiece(name, destRow, destCol)
                
                my_old_index = self.compute_indices(self.old_x_coord, self.old_y_coord) 
                my_index = self.compute_indices(event.x, event.y) #intention to move to
                
                
                #validate the red piece movement here
                #print("self.check_valid_move(Client_Gui.selected_piece,my_index, my_old_index) is: ", self.check_valid_move(Server_Gui.selected_piece,my_index, my_old_index))
                check_valid_move_result = self.check_valid_move(Client_Gui.selected_piece,my_index, my_old_index)
                if(check_valid_move_result!=0):
                    self.movepiece(Client_Gui.selected_piece, my_index[0], my_index[1])
                    if(check_valid_move_result[0]=="hop"):
                        print("Hoppity Hoppomus")
                        #print("my_index[0] my_index[1]: ", my_index)
                        print(check_valid_move_result[1])
                        Client.pieces_to_remove.append(self.return_piece_name(check_valid_move_result[1]))
                        #print(Client.coordArrayX)
                        #print(Client.pieces_to_remove)
                        self.removepiece(self.return_piece_name(check_valid_move_result[1]))
                    if(my_index[0] == 0):
                        #delete the piece and replace with king piece
                        #print("Making king now!!!!")
                        myTags = self.canvas.gettags(Client_Gui.selected_piece)
                        #self.removepiece(Client_Gui.selected_piece)
                        self.canvas.delete(Client_Gui.selected_piece)
                        blackking = tk.PhotoImage(file="blackking.gif")
                        col = my_index[1]
                        row = my_index[0]
                        xCoord = (col * self.size) + int(self.size/2)
                        yCoord = (row * self.size) + int(self.size/2)
                        #inherit same piece name but replace second tag with "blackkingtag"
                        self.canvas.create_image(xCoord,yCoord,image=blackking, tags=(myTags[0], "blackkingtag"),anchor="c")                        
                        self.placepiece(blackking, 0, 0)
                        #store it in the data structure as well
                    print("Before sending it off!")    
                    if(self.has_valid_hops_left(Client_Gui.selected_piece, my_index, check_valid_move_result) == 0):
                        print("Sending it off now!") 
                        Client_Gui.moveflag = 1
                #self.movepiece(self.old_O_piece_clicked, my_index[0], my_index[1])
                
                # and Client_Gui.moveflag == 1
                # if(self.has_valid_hops_left(Client_Gui.selected_piece) == 0 and Client_Gui.moveflag == 1)
                #  self.check_valid_move(Client_Gui.selected_piece,my_index, my_old_index)==0
                #once that piece can no longer move, send the data over to other side
                if(Client_Gui.moveflag == 1):
                    print("******************************")
                    print("Sending Data Over Now!")
                    print("******************************")                
                    Client_Gui.moveflag = 0
                    self.update_info_GUI()
                    Client_Gui.msg_to_send = [Client_Gui.selected_piece, [my_index[0], my_index[1]], Client.pieces_to_remove]
                    Client_Gui.selected_piece = ""
                    Client.pieces_to_remove = []                    
                    #Python Queue class are synchronized so we can
                    #"put" from any threads and it will be synchronized
                    #Server. or Client_Gui. Server_Queue.put(Client_Gui.msg_to_send)
                    Client.send_queue.put(Client_Gui.msg_to_send)
                    #Client.send_queue.join() This means that the queue is never being emptied
                    print("Contents in the queue:", Client.send_queue.qsize())
                    print("Client.coordArrayO", Client.coordArrayO)
                    print("Client.coordArrayX", Client.coordArrayX)
                    if(Client.numCaptured==12):
                        messagebox.showinfo("Congratulations!", "You won!")
                        self.running = 0
                        time.sleep(4)
                        sys.exit(0)                    
                return

    def check_valid_move(self, name, my_index, my_old_index): #I think first half works
        #checks if my_index is a valid move (as in if another hop is available), then return 1
        #if there is no valid move return 0
        #Algorithm:
        #check if two diagonal space is full, if so hop is not possible for that path
        #check if two diagonal space if empty and one diagonal space is appropriate piece, then return valid move
        #else check if one space traversal is possible, if so return valid move
        #else return 0
        result = 0
        list_of_possible_moves = [] #apply algorithm for max one hop length or one space traversal for that piece
                                    #check if my_index is in this list of possible moves, if so return 1, else return 0
        #print("Debugging check_valid_move")
        #print("my_index is: ", my_index)
        piece_type = self.return_piece_type(my_old_index)
        #print("piece_type is: ", piece_type)
        if(piece_type == "blackpiece"): #regular piece
            #print("In the if statement branch: ")
            index_array = []
            index_flag = []
            #  2    3
            #   0  1
            #    ||
            #print("x coord        , y_coord        : ")
            #print("my_old_index[1], my_old_index[0]: ", my_old_index[1], my_old_index[0])
            index0 = (my_old_index[1]-1, my_old_index[0]-1) #four possible moves for piece
            index1 = (my_old_index[1]+1, my_old_index[0]-1) #note [1] is col or x coord
            index2 = (my_old_index[1]-2, my_old_index[0]-2) #note [0] is row or y coord
            index3 = (my_old_index[1]+2, my_old_index[0]-2)
            index_array.append(index0)
            index_array.append(index1)
            index_array.append(index2)
            index_array.append(index3)
            #print("index_array is: ", index_array)
            for i in range(0,4):
                #set to be true until proven otherwise
                index_flag.append(1) #respective index corresponds to valid more or not
                
            for i in range(0,4): #determine all the illegal moves here
                #index out of bound
                if(index_array[i][0]<0 or index_array[i][0]>7 or index_array[i][1]<0 or index_array[i][1]>7):
                    index_flag[i] = 0
                
                if(i==0):                    #left side is ally piece
                    #print("we are at i==0")
                    if(self.check_if_vacant(index_array[i]) == 0):
                        test_index = (index_array[i][1],index_array[i][0])   #way I wrote return_piece_type() expect flipped tuple
                        if((self.return_piece_type(test_index) == "blackpiece") or (self.return_piece_type(test_index) == "blackking")):
                            index_flag[i] = 0
                            index_flag[i+2] = 0
                    #left side is completely blocked
                    if(self.check_if_vacant(index_array[i]) == 0 and self.check_if_vacant(index_array[i+2]) == 0):
                        index_flag[i] = 0
                        index_flag[i+2] = 0
                    #print("index_flag is: ", index_flag)
                
                if(i==1):
                    #print("we are at i==1")
                    #right side is ally piece
                    if(self.check_if_vacant(index_array[i]) == 0):
                        #print("index_array[i] is: ", index_array[i])
                        test_index = (index_array[i][1],index_array[i][0])   #way I wrote return_piece_type() expect flipped tuple
                        if((self.return_piece_type(test_index) == "blackpiece") or (self.return_piece_type(test_index) == "blackking")):
                            #print("We get here xxxxxxxxxxxxx") #this branch is problem, why????
                            index_flag[i] = 0
                            index_flag[i+2] = 0
                    #right side is completely blocked                        
                    if(self.check_if_vacant(index_array[i]) == 0 and self.check_if_vacant(index_array[i+2]) == 0):
                        #print("We get here yyyyyyyyyyyyyy")
                        index_flag[i] = 0
                        index_flag[i+2] = 0  
                    #print("index_flag is: ", index_flag)
                #left most side is not vacant
                if(i==2):
                    #print("we are at i==2")
                    if(self.check_if_vacant(index_array[i]) == 0):
                        index_flag[i] = 0
                    if(self.check_if_vacant(index_array[i-2]) == 1): #if preceding space is empty can't hop to this
                        index_flag[i] = 0
                    #print("index_flag is: ", index_flag)
                #right most side is not vacant
                if(i==3):
                    #print("we are at i==3")
                    if(self.check_if_vacant(index_array[i]) == 0):
                        index_flag[i] = 0
                    if(self.check_if_vacant(index_array[i-2]) == 1): #if preceding space is empty can't hop to this
                        index_flag[i] = 0                    
                    #print("index_flag is: ", index_flag)
                    
            #print("index_flag is: ", index_flag)
            #print("Expected index_flag is:  [1, 1, 0, 0]")
            for i in range(0,4): #check all valid moves        
                if(index_flag[i] == 1):
                    list_of_possible_moves.append(index_array[i])
                    if(index_array[i] == (my_index[1], my_index[0])): #is the requested move one of the valid moves?
                        #and which move type?
                        if(i<2):
                            result = "move"
                        if(i==2): #leftmost to center
                            num1 = my_index[0]+1
                            num2 = my_index[1]+1
                            result = ("hop",(num1, num2)) #values which are index of piece to remove
                        if(i==3): #rightmost to center
                            num3 = my_index[0]+1
                            num4 = my_index[1]-1
                            result = ("hop",(num3, num4))                        
            #print("my_index[0], my_index[1]: ", my_index[0], my_index[1])
            #print("index_array: ", index_array)
            #print("We made it to the end of check_valid_move()! ")
            #print("result is: ", result)
        elif(piece_type == "blackking"): #king piece
            print("Detected blackking movement!")
            index_array = []
            index_flag = []
            #  2    3
            #   0  1
            #    ||
            #   4  5
            #  6    7
            index0 = (my_old_index[1]-1, my_old_index[0]-1) #four possible moves for piece
            index1 = (my_old_index[1]+1, my_old_index[0]-1)
            index2 = (my_old_index[1]-2, my_old_index[0]-2)
            index3 = (my_old_index[1]+2, my_old_index[0]-2)
            index4 = (my_old_index[1]-1, my_old_index[0]+1)
            index5 = (my_old_index[1]+1, my_old_index[0]+1)
            index6 = (my_old_index[1]-2, my_old_index[0]+2)
            index7 = (my_old_index[1]+2, my_old_index[0]+2) 
            index_array.append(index0)
            index_array.append(index1)
            index_array.append(index2)
            index_array.append(index3)
            index_array.append(index4)
            index_array.append(index5)
            index_array.append(index6)
            index_array.append(index7)
            for i in range(0,8):
                #set to be true until proven otherwise
                index_flag.append(1) #respective index corresponds to valid more or not
            for i in range(0,8):
                if(i==0):                    #upward, left side is ally piece
                    #print("we are at i==0")
                    if(self.check_if_vacant(index_array[i]) == 0):
                        test_index = (index_array[i][1],index_array[i][0])   #way I wrote return_piece_type() expect flipped tuple
                        if((self.return_piece_type(test_index) == "blackpiece") or (self.return_piece_type(test_index) == "blackking")):
                            index_flag[i] = 0
                            index_flag[i+2] = 0
                    #left side is completely blocked
                    if(self.check_if_vacant(index_array[i]) == 0 and self.check_if_vacant(index_array[i+2]) == 0):
                        index_flag[i] = 0
                        index_flag[i+2] = 0
                    #print("index_flag is: ", index_flag)
                if(i==1):                    #upward, right side is ally piece
                    #print("we are at i==1")
                    #right side is ally piece
                    if(self.check_if_vacant(index_array[i]) == 0):
                        #print("index_array[i] is: ", index_array[i])
                        test_index = (index_array[i][1],index_array[i][0])   #way I wrote return_piece_type() expect flipped tuple
                        if((self.return_piece_type(test_index) == "blackpiece") or (self.return_piece_type(test_index) == "blackking")):
                            #print("We get here xxxxxxxxxxxxx") #this branch is problem, why????
                            index_flag[i] = 0
                            index_flag[i+2] = 0
                    #right side is completely blocked                        
                    if(self.check_if_vacant(index_array[i]) == 0 and self.check_if_vacant(index_array[i+2]) == 0):
                        #print("We get here yyyyyyyyyyyyyy")
                        index_flag[i] = 0
                        index_flag[i+2] = 0  
                    #print("index_flag is: ", index_flag)                    
                if(i==2):                    #upward, left most side is not vacant
                    #print("we are at i==2")     
                    if(self.check_if_vacant(index_array[i]) == 0):
                        index_flag[i] = 0
                    if(self.check_if_vacant(index_array[i-2]) == 1): #if preceding space is empty can't hop to this
                        index_flag[i] = 0
                    #print("index_flag is: ", index_flag)
                if(i==3):                    #upward, right most side is not vacant
                    #print("we are at i==3")    
                    if(self.check_if_vacant(index_array[i]) == 0):
                        index_flag[i] = 0
                    if(self.check_if_vacant(index_array[i-2]) == 1): #if preceding space is empty can't hop to this
                        index_flag[i] = 0                    
                    #print("index_flag is: ", index_flag)                    
                if(i==4):                    #downward, left side is ally piece
                    #print("we are at i==4")     
                    if(self.check_if_vacant(index_array[i]) == 0):
                        test_index = (index_array[i][1],index_array[i][0])   #way I wrote return_piece_type() expect flipped tuple
                        if((self.return_piece_type(test_index) == "blackpiece") or (self.return_piece_type(test_index) == "blackking")):
                            index_flag[i] = 0
                            index_flag[i+2] = 0
                    #left side is completely blocked
                    if(self.check_if_vacant(index_array[i]) == 0 and self.check_if_vacant(index_array[i+2]) == 0):
                        index_flag[i] = 0
                        index_flag[i+2] = 0
                    #print("index_flag is: ", index_flag)
                if(i==5):                    #downward, right side is ally piece
                    #print("we are at i==5")
                    #right side is ally piece
                    if(self.check_if_vacant(index_array[i]) == 0):
                        #print("index_array[i] is: ", index_array[i])
                        test_index = (index_array[i][1],index_array[i][0])   #way I wrote return_piece_type() expect flipped tuple
                        if((self.return_piece_type(test_index) == "blackpiece") or (self.return_piece_type(test_index) == "blackking")):
                            #print("We get here xxxxxxxxxxxxx") #this branch is problem, why????
                            index_flag[i] = 0
                            index_flag[i+2] = 0
                    #right side is completely blocked                        
                    if(self.check_if_vacant(index_array[i]) == 0 and self.check_if_vacant(index_array[i+2]) == 0):
                        #print("We get here yyyyyyyyyyyyyy")
                        index_flag[i] = 0
                        index_flag[i+2] = 0  
                    #print("index_flag is: ", index_flag)                     
                if(i==6):                    #downward, left most side is not vacant
                    print("we are at i==6")     
                    if(self.check_if_vacant(index_array[i]) == 0):
                        index_flag[i] = 0
                    if(self.check_if_vacant(index_array[i-2]) == 1): #if preceding space is empty can't hop to this
                        index_flag[i] = 0
                    #print("index_flag is: ", index_flag)
                if(i==7):                    #downward, right most side is not vacant
                    print("we are at i==7")   
                    if(self.check_if_vacant(index_array[i]) == 0):
                        index_flag[i] = 0
                    if(self.check_if_vacant(index_array[i-2]) == 1): #if preceding space is empty can't hop to this
                        index_flag[i] = 0                    
                    #print("index_flag is: ", index_flag)   

            for i in range(0,8): #check all valid moves        
                if(index_flag[i] == 1):
                    list_of_possible_moves.append(index_array[i])
                    if(index_array[i] == (my_index[1], my_index[0])): #is the requested move one of the valid moves?
                        #and which move type?
                        if(i==0 or i==1):
                            result = "move"
                        if(i==2): #leftmost to center
                            num1 = my_index[0]+1
                            num2 = my_index[1]+1
                            result = ("hop",(num1, num2)) #values which are index of piece to remove
                        if(i==3): #rightmost to center
                            num1 = my_index[0]+1
                            num2 = my_index[1]-1
                            result = ("hop",(num1, num2))
                        if(i==4 or i == 5):
                            result = "move"
                        if(i==6):
                            num1 = my_index[0]-1
                            num2 = my_index[1]+1
                            result = ("hop",(num1, num2)) #values which are index of piece to remove
                        if(i==7):
                            num1 = my_index[0]-1
                            num2 = my_index[1]-1
                            result = ("hop",(num1, num2))
        print("result is: ", result)
        print("Exitting check_valid_move()")
        return result
    
    def has_valid_hops_left(self, name, my_index, prev_move_type):
        #checks from the current location of the piece whether it has any valid hops left
        #returns a boolean 0 or 1
        result = 0
        piece_type = self.return_piece_type(my_index)
        if(piece_type == "blackpiece"): #regular piece
            index_array = []
            index_flag = []
            #  2    3
            #   h  h
            #    ||
            #print("x coord        , y_coord        : ")
            #print("my_index[1], my_index[0]: ", my_index[1], my_index[0])
            index0 = (my_index[1]-1, my_index[0]-1) #four possible moves for piece
            index1 = (my_index[1]+1, my_index[0]-1) #note [1] is col or x coord, note [0] is row or y coord
            index2 = (my_index[1]-2, my_index[0]-2) #hop #1
            index3 = (my_index[1]+2, my_index[0]-2) #hop #2
            index_array.append(index0)
            index_array.append(index1)
            index_array.append(index2)
            index_array.append(index3)
            #print("index_array is: ", index_array)
            for i in range(0,4):
                #set to be true until proven otherwise
                index_flag.append(1) #respective index corresponds to valid more or not            

            for i in range(0,4): #determine all the illegal moves here
                #index out of bound
                if(index_array[i][0]<0 or index_array[i][0]>7 or index_array[i][1]<0 or index_array[i][1]>7):
                    index_flag[i] = 0
                
                if(i==0):                    #left side is ally piece
                    index_flag[i] = 0
                if(i==1):
                    index_flag[i] = 0
                if(i==2):
                    #print("we are at i==2")
                    if(self.check_if_vacant(index_array[i]) == 0):
                        index_flag[i] = 0
                    if(self.check_if_vacant(index_array[i-2]) == 1): #if preceding space is empty can't hop to this
                        index_flag[i] = 0
                    #print("index_flag is: ", index_flag)
                #right most side is not vacant
                if(i==3):
                    #print("we are at i==3")
                    if(self.check_if_vacant(index_array[i]) == 0):
                        index_flag[i] = 0
                    if(self.check_if_vacant(index_array[i-2]) == 1): #if preceding space is empty can't hop to this
                        index_flag[i] = 0                    
                    #print("index_flag is: ", index_flag)
                    
            #print("index_flag is: ", index_flag)
            #print("Expected index_flag is:  [1, 1, 0, 0]")
            for i in range(0,4): #check all valid moves        
                result = result + index_flag[i]                    
            #print("my_index[0], my_index[1]: ", my_index[0], my_index[1])
            #print("index_array: ", index_array)
            #print("We made it to the end of has_valid_hops_left()! ")
            if(prev_move_type=="move"):
                result = 0

        elif(piece_type == "blackking"): #king piece
            print("Detected blackking movement!")
            index_array = []
            index_flag = []
            #  2    3
            #   0  1
            #    ||
            #   4  5
            #  6    7
            index0 = (my_index[1]-1, my_index[0]-1) #four possible moves for piece
            index1 = (my_index[1]+1, my_index[0]-1)
            index2 = (my_index[1]-2, my_index[0]-2)
            index3 = (my_index[1]+2, my_index[0]-2)
            index4 = (my_index[1]-1, my_index[0]+1)
            index5 = (my_index[1]+1, my_index[0]+1)
            index6 = (my_index[1]-2, my_index[0]+2)
            index7 = (my_index[1]+2, my_index[0]+2) 
            index_array.append(index0)
            index_array.append(index1)
            index_array.append(index2)
            index_array.append(index3)
            index_array.append(index4)
            index_array.append(index5)
            index_array.append(index6)
            index_array.append(index7)
            
            for i in range(0,8):
                #set to be true until proven otherwise
                index_flag.append(1) #respective index corresponds to valid more or not            

            for i in range(0,8): #determine all the illegal moves here
                #index out of bound
                # if(index_array[i][0]<0 or index_array[i][0]>7 or index_array[i][1]<0 or index_array[i][1]>7):
                    # index_flag[i] = 0
                
                if(i==0):                    #left side is ally piece
                    index_flag[i] = 0
                if(i==1):
                    index_flag[i] = 0
                if(i==2):   #upward, left most side is not vacant
                    #print("we are at i==2")
                    if(self.check_if_vacant(index_array[i]) == 0):
                        index_flag[i] = 0
                    if(self.check_if_vacant(index_array[i-2]) == 1): #if preceding space is empty can't hop to this
                        index_flag[i] = 0
                    test_index = (index_array[i-2][1],index_array[i-2][0])   #way I wrote return_piece_type() expect flipped tuple
                    if((self.return_piece_type(test_index) == "blackpiece") or (self.return_piece_type(test_index) == "blackking")):
                        index_flag[i] = 0
                    #print("index_flag is: ", index_flag)
                #right most side is not vacant
                if(i==3):   #upward, right most side is not vacant
                    #print("we are at i==3")
                    if(self.check_if_vacant(index_array[i]) == 0):
                        index_flag[i] = 0
                    if(self.check_if_vacant(index_array[i-2]) == 1): #if preceding space is empty can't hop to this
                        index_flag[i] = 0
                    test_index = (index_array[i-2][1],index_array[i-2][0])   #way I wrote return_piece_type() expect flipped tuple
                    if((self.return_piece_type(test_index) == "blackpiece") or (self.return_piece_type(test_index) == "blackking")):
                        index_flag[i] = 0                        
                    #print("index_flag is: ", index_flag)
                if(i==4):
                    index_flag[i] = 0
                if(i==5):
                    index_flag[i] = 0
                if(i==6):   #downward, left most side is not vacant
                    print("we are at i==6")
                    if(self.check_if_vacant(index_array[i]) == 0):
                        index_flag[i] = 0
                    if(self.check_if_vacant(index_array[i-2]) == 1): #if preceding space is empty can't hop to this
                        index_flag[i] = 0
                    test_index = (index_array[i-2][1],index_array[i-2][0])   #way I wrote return_piece_type() expect flipped tuple
                    if((self.return_piece_type(test_index) == "blackpiece") or (self.return_piece_type(test_index) == "blackking")):
                        index_flag[i] = 0
                    #print("index_flag is: ", index_flag)                
                if(i==7):
                    print("we are at i==7")
                    if(self.check_if_vacant(index_array[i]) == 0):
                        index_flag[i] = 0
                    if(self.check_if_vacant(index_array[i-2]) == 1): #if preceding space is empty can't hop to this
                        index_flag[i] = 0
                    test_index = (index_array[i-2][1],index_array[i-2][0])   #way I wrote return_piece_type() expect flipped tuple
                    if((self.return_piece_type(test_index) == "blackpiece") or (self.return_piece_type(test_index) == "blackking")):
                        index_flag[i] = 0                        
                    #print("index_flag is: ", index_flag)
                    
            #print("index_flag is: ", index_flag)
            #print("Expected index_flag is:  [1, 1, 0, 0]")
            for i in range(0,8): #check all valid moves        
                result = result + index_flag[i]                    
            #print("my_index[0], my_index[1]: ", my_index[0], my_index[1])
            #print("index_array: ", index_array)
            #print("We made it to the end of has_valid_hops_left()! ")            
            if(prev_move_type=="move"):
                result = 0
        print("prev_move_type is: ", prev_move_type)        
        print("result is: ", result, "index_flag is: ", index_flag)
        print("Exitting has_valid_hops_left()")
        return result
        
        
    def return_piece_name(self, my_index):
        #print("return_piece_name")
        #print("my_index is: ", my_index)
        result = "" #no piece exists
        #print("my_index[0], my_index[1]", my_index[0], my_index[1])
        for my_piece_O in range(len(Client.coordArrayO)):
            if((my_index[0]) == Client.coordArrayO[my_piece_O][1]):
                if(my_index[1] == Client.coordArrayO[my_piece_O][2]):
                    result = Client.coordArrayO[my_piece_O][0]    #returns piece# like piece15
                    #print("result is:", result)
                    break
        for my_piece_X in range(len(Client.coordArrayX)):
            if((my_index[0]) == Client.coordArrayX[my_piece_X][1]):
                if(my_index[1] == Client.coordArrayX[my_piece_X][2]):
                    result = Client.coordArrayX[my_piece_X][0]    #returns piece# like piece4
                    #print("result is:", result)
                    break
        return result
                    
    def return_piece_type(self, my_index):
        #print("return_piece_type")
        #print("my_index is: ", my_index)
        name = self.return_piece_name(my_index)
        temp = self.canvas.gettags(name)
        
        #print("temp is: ", temp)
        #print("temp[1] is: ", temp[1])
        result = "" #no piece exists
        if(len(temp)==2):
            if(temp[1] == "blackpiecetag"):
                result = "blackpiece"
            if(temp[1] == "redpiecetag"):
                result = "redpiece"
            if(temp[1] == "blackkingtag"):
                result = "blackking"
            if(temp[1] == "redkingtag"):
                result = "redking"
        
        return result        
        
    def check_if_vacant(self, my_index):
        vacant_flag = 1
        #my_index[1] my_index[0] is row col
        #print("my_index: ", my_index)
        for my_piece_O in range(len(Client.coordArrayO)):
            #print(Client.coordArrayO[my_piece_O][1], Client.coordArrayO[my_piece_O][2])
            if(my_index[1] == Client.coordArrayO[my_piece_O][1]):
                if(my_index[0] == Client.coordArrayO[my_piece_O][2]):
                    vacant_flag = 0
                    return vacant_flag
                    
        for my_piece_X in range(len(Client.coordArrayX)):
            #print(Client.coordArrayX[my_piece_X][1], Client.coordArrayX[my_piece_X][2])
            if(my_index[1] == Client.coordArrayX[my_piece_X][1]):
                if(my_index[0] == Client.coordArrayX[my_piece_X][2]):
                    vacant_flag = 0
                    return vacant_flag    
        return vacant_flag
        
    def game_on(self):
        self.click_counter = 0
        self.old_x_coord = 0
        self.old_y_coord = 0
        self.old_X_piece_clicked = ""
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

                
    def init_info_GUI(self):
        #instantiate the components 
        self.label_text1 = "Timer: "
        self.label_text2 = "Turn Counter: "
        self.label_text3 = "Num Pieces Captured: "

        self.GUI_Button1 = tk.Button(self.canvas, text='Rules', command=self.printRules)
        self.GUI_Button1.grid(padx = 450, pady = 0, row = 1, column = 1)
        self.TIMER_Label = tk.Label(self.canvas, text=self.label_text1)
        self.TIMER_Label.grid(padx = 0, row = 2, column = 1)
        self.GUI_Label2 = tk.Label(self.canvas, text=self.label_text2)
        self.GUI_Label2.grid(padx = 0, row = 3, column = 1)
        self.GUI_Label3 = tk.Label(self.canvas, text=self.label_text3)
        self.GUI_Label3.grid(padx = 0, row = 4, column = 1)

        self.GUI_Button = tk.Button(self.canvas, text='Exit', command=self.endCommand)
        self.GUI_Button.grid(padx = 0, row = 10, column = 1)#(side=tk.RIGHT)
        
        
    def update_info_GUI(self):
        self.label_text2 = "Turn Counter: " + str(Client.turn_count)
        self.label_text3 = "Num Pieces Captured: " + str(Client.numCaptured)
        
        self.GUI_Label2.config(text = self.label_text2)
        self.GUI_Label3.config(text = self.label_text3)
        
    def printHello(self):
        self.label_text1Count+=1
        print("Hello World!")
        if(self.label_text1Count%2 == 1):
            self.label_text1.set("Test")
        else:
            self.label_text1.set("Not Test")
            
        print("Set new text")
        
    def printRules(self):
        messagebox.showinfo("Rules", "Move your checker pieces diagonally\n and capture their pieces!")
        os.startfile('images\Rules.png')
        
    def one_sec_counter(self, label):
        counter = count(0)
        def update_func():
            label.config(text="Timer: " + str(next(counter)) + " sec")
            label.after(1100, update_func) #after 1 sec or 1000 ms
            #this uses recursion
        update_func()        
    
    def processIncoming(self):
        """Handle all messages currently in the queue, if any."""
        #print("Is processIncoming() active on Client?") # yes its active
        #print("Client.recv_queue.qsize() is: ", Client.recv_queue.qsize())
        while Client.recv_queue.qsize():
            try:
                msg = self.recv_queue.get(0)
                # Check contents of message and do whatever is needed. As a
                # simple test, print it (in real life, you would
                # suitably update the GUI's display in a richer fashion).
                decoded_msg = pickle.loads(msg)
                self.server_moved_piece = decoded_msg[0]
                self.server_new_piece_coord = decoded_msg[1]
                self.server_removed_pieces = decoded_msg[2]
                # print("Printing my message", self.server_moved_piece)
                # print("Printing my message", self.server_new_piece_coord)
                # print("Printing my message", self.server_removed_pieces)
                self.movepiece(self.server_moved_piece, 7 - self.server_new_piece_coord[0], 7 - self.server_new_piece_coord[1])
                # self.canvas.delete("piece10")
                # self.removepiece("piece10")
                if(len(self.server_removed_pieces)>0):
                    for piece_name in self.server_removed_pieces:
                        self.removepiece(piece_name)
                        Client.numRemaining = Client.numRemaining - 1
                if(self.server_new_piece_coord[0] == 0):
                    myTags = self.canvas.gettags(self.server_moved_piece)
                    #self.removepiece(self.server_moved_piece)  
                    self.canvas.delete(self.server_moved_piece)
                    print("Time to make a king piece!!!")                    
                    redking = tk.PhotoImage(file="redking.gif")
                    col = 7 - self.server_new_piece_coord[1]
                    row = 7 - self.server_new_piece_coord[0]
                    xCoord = (col * self.size) + int(self.size/2)
                    yCoord = (row * self.size) + int(self.size/2)
                    self.canvas.create_image(xCoord,yCoord,image=redking, tags=(self.server_moved_piece, "redkingtag"),anchor="c")                    
                    self.placepiece(redking, 0, 0)
                # print("Client.coordArrayX is: ", Client.coordArrayX)
                # print("Client.coordArrayO is: ", Client.coordArrayO)
                self.GUI_Label2.config(text="Turn Counter: " + str(Client.turn_count))
                if(Client.numRemaining==0):
                    messagebox.showinfo("You Lost.", "Good Luck Next Time!")
                    self.running = 0
                    time.sleep(4)
                    sys.exit(0)
                print("Client.coordArrayO", Client.coordArrayO)
                print("Client.coordArrayX", Client.coordArrayX)                    
                print("Exitted processIncoming()")
            except:
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
        
        Client.numCaptured = 0
        Client.numRemaining = 12
        Client.turn_count = 1
        Client.pieces_to_remove = []
        self.init_board()
        self.setup_Gui()

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
        # also note this initialization is done in GUI side        
        Client.coordArrayX = [["piece12",5,0],["piece11",5,2],["piece10",5,4],["piece9",5,6], 
                        ["piece8",6,1], ["piece7",6,3], ["piece6",6,5], ["piece5",6,7],
                        ["piece4",7,0],["piece3",7,2],["piece2",7,4],["piece1",7,6]]
        Client.coordArrayO = [["piece24",0,1],["piece23",0,3],["piece22",0,5],["piece21",0,7], 
                        ["piece20",1,0], ["piece19",1,2], ["piece18",1,4], ["piece17",1,6],
                        ["piece16",2,1],["piece15",2,3],["piece14",2,5],["piece13",2,7]]

        #####################################################

    def setup_Gui(self):
        self.master = tk.Tk() #master = root
        self.master.title("Checkers: Client")
        self.master.minsize(width=640, height=320)
        self.master.maxsize(width=640, height=320)
        self.master.iconbitmap('fireball.ico')
        #Create Queue for I/O communication
        Client.recv_queue = queue.Queue() #Queue() class
        Client.send_queue = queue.Queue() #Queue() class
        #Setup GUI here (includes the Checkerboard)
        self.gui = Client_Gui(self.master, Client.recv_queue, Client.send_queue, self.endGame)
        
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
            #self.socket.setblocking(0) #making it non-blocking causes the data to not be caught :<
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


    
    def send_server_output_forever(self):
        while True:
            try:
                #self.get_console_input()
                #self.connection_send()
                #self.connection_receive()
                self.connection_handler(self.socket)
            except (KeyboardInterrupt, EOFError):
                print()
                print("Closing server connection ...")
                self.socket.close()
                sys.exit(1)
                
    def connection_handler(self, connection):
        while True:
            if(Client.send_queue.qsize()): #aka Client_Queue... for sending
                #Here we want to send the checker data
                print("Sending Client Data to Server!")
                #msg should be the game data that you want to send to the server gui!!!!!
                #print("Contents in the queue: ", Client.send_queue.qsize())
                data_to_send = Client.send_queue.get() #ie: list = ["piece5",[2,4],["piece5","piece9"],5]
                print("Contents in the queue: ", Client.send_queue.qsize())    
                #below cannot work for decode(utf-8)
                #since it only supports strings, not dynamic data type like above
                pickled_byte_msg = pickle.dumps(data_to_send) #pickled into byte object
                # Send the received bytes back to the client.
                connection.sendall(pickled_byte_msg)
                print("Sent: ", data_to_send)
                print("Contents in the queue: ", Client.send_queue.qsize())
                Client.turn_count = Client.turn_count + 1
            elif((Client.turn_count)%2==1): # even turns are for client
                #this socket made to be non-blocking, it polls then skips
                print("******************************")
                print("Receiving Data Right Now!!!!!!!!! xDDDDDDDDDD")
                print("******************************")
                pickled_data = connection.recv(1024)
                Client.recv_queue.put(pickled_data)
                print("Size of Client.recv_queue is: ", Client.recv_queue.qsize())
                Client.turn_count = Client.turn_count + 1

                
    def client_thread(self):
        #We will handle our asynchronous I/O of socket communication here.
        self.get_socket()
        self.connect_to_server()
        while self.running:
            #insert socket comm here
            self.send_server_output_forever()
        
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





