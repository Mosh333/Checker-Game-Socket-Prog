        pieceCounter = 0
        #initial population of all the pieces for server side
        # for i in range(1,25):
            # if(i<13):
                # self.pieces['player%02d'%i] = blackpiece
            # else:
                # self.pieces['player%02d'%i] = redpiece
        # print("i at end is", i)     
        
        
        
        
        
               #board.addpiece("player1", player1, 0,0)
        myPlayer = []
        player1 = tk.PhotoImage(data=blackpiece)
        player2 = tk.PhotoImage(data=blackpiece)
        player3 = tk.PhotoImage(data=blackpiece)
        player4 = tk.PhotoImage(data=blackpiece)
        player5 = tk.PhotoImage(data=blackpiece)
        player6 = tk.PhotoImage(data=blackpiece)
        player7 = tk.PhotoImage(data=blackpiece)
        player8 = tk.PhotoImage(data=blackpiece)
        player9 = tk.PhotoImage(data=blackpiece)
        player10 = tk.PhotoImage(data=blackpiece)
        player11 = tk.PhotoImage(data=blackpiece)
        player12 = tk.PhotoImage(data=blackpiece)
        player13 = tk.PhotoImage(data=redpiece)
        player14 = tk.PhotoImage(data=redpiece)
        player15 = tk.PhotoImage(data=redpiece)
        player16 = tk.PhotoImage(data=redpiece)
        player17 = tk.PhotoImage(data=redpiece)
        player18 = tk.PhotoImage(data=redpiece)
        player19 = tk.PhotoImage(data=redpiece)
        player20 = tk.PhotoImage(data=redpiece)
        player21 = tk.PhotoImage(data=redpiece)
        player22 = tk.PhotoImage(data=redpiece)
        player23 = tk.PhotoImage(data=redpiece)
        player24 = tk.PhotoImage(data=redpiece)
        # player1 = player2 = player3 = player4 = player5 = player6 = tk.PhotoImage(data=blackpiece)
        # player7 = player8 = player9 = player10 = player11 = player12 = tk.PhotoImage(data=blackpiece)
        # player13 = player14 = player15 = player16 = player17 = player18 = tk.PhotoImage(data=redpiece)
        # player19 = player20 = player21 = player22 = player23 = player24 = tk.PhotoImage(data=redpiece)
        myPlayer.extend((player1,player2,player3,player4,player5,player6,player7,player8,player9,player10,player11,player12,
                        player13,player14,player15,player16,player17,player18,player19,player20,player21,player22,
                        player23,player24))
                        
        self.canvas.create_image(0,0, image=blackpiece, tags=(blackpiece, "blackpiece"), anchor="c")
        self.placepiece("player1",row,col)
        
        print("Problem here")
        # for row in range(8):
            # for col in range(8):
                # if (row,col) in coordArrayX:
                    # self.canvas.create_image(0,0, image=blackpiece, tags=(blackpiece, "blackpiece"), anchor="c")
                    # self.placepiece(myPlayer[pieceCounter],row,col)
                    # pieceCounter = pieceCounter + 1
                # elif (row,col) in coordArrayO:
                    # self.canvas.create_image(0,0, image=redpiece, tags=(redpiece, "redpiece"), anchor="c")
                    # self.placepiece(myPlayer[pieceCounter],row,col)
                    # pieceCounter = pieceCounter + 1
        # for row in range(8):
            # for col in range(8):
                # if (row,col) in coordArrayX:
                    # pieceCounter = pieceCounter + 1
                    # self.canvas.create_image(0,0, image=blackpiece, tags=(blackpiece, "blackpiece"), anchor="c")
                    # print('player%02d'%pieceCounter)
                    # self.placepiece('player%02d'%pieceCounter, row, col)
                # elif (row,col) in coordArrayO:
                    # pieceCounter = pieceCounter + 1
                    # self.canvas.create_image(0,0, image=redpiece, tags=(redpiece, "redpiece"), anchor="c")
                    # print('player%02d'%pieceCounter)
                    # self.placepiece('player%02d'%pieceCounter, row, col)