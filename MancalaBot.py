import numpy as np
import copy

class MancalaBot:
    def __init__(self):
        self.board = np.zeros(14).astype(int)+4
        self.board[6] = 0
        self.board[13] = 0
        self.mystore = 0
        self.oppstore = 0
        self.myturn = 1
        self.gameover = False
        self.issim = False
        self.bot = True

    def StartGame(self):
        depth = 6
        num_players = int(input('Play with 1 or 2 players?\t'))
        if num_players == 1:
            pass
        elif num_players == 2:
            self.bot = False
        else:
            print('Error: input not recognized. Defaulting to single player')
        default = True
        def_input = input('Use default board setup? (Y or N):\t').lower()
        if def_input == 'y':
            pass
        elif def_input == 'n':
            default = False
        else:
            print('Error: input not recognized. Using default board setup.')
        if not default:
            self.SetupBoard()
        first = int(input('Which player goes first? Enter 1 or 2:\t'))
        if first == 1:
            pass
        elif first == 2:
            self.myturn = -1
        else:
            print('Error: input not recognized. Defaulting to player 1 first.')
        self.PrintBoard()
        print('Starting game.')
        print("Player {}'s turn.".format((self.myturn+3)%3))
        # main game loop
        quitted = False
        while(self.gameover==False):
            if (self.bot==True and self.myturn==1) or self.bot==False:
                try:
                    move = input('Play a move:\t')
                    if move.lower() == 'q':
                        quitted = True
                        break
                    self.PlayMove(self.ConvertMove(int(move)))
                except ValueError:
                    print('Error: input not understood.')
            else:
                self.PlayMove(self.ConvertMove(self.FindBestMove(depth)))
        if not quitted:
            self.CheckWinner()
            
        
    def PlayMove(self,move):
        # make sure the move is legal
        if (((self.myturn==1) and (move > 5)) or ((self.myturn==-1) and ((move < 7) or (move > 12)))) or self.board[move]==0:
            if not self.issim:
                print('Illegal move!')
            return -1
                
        # number in the hole the player picks are all
        # moved into the hand
        num_active = self.board[move]
        self.board[move] = 0

        # depending on whose turn it is, one store will
        # be passed over
        store_index = 13
        skip_index = 6
        if self.myturn == 1:
            store_index = 6
            skip_index = 13

        i = 1 # counter representing which hole we're at
        # loop through holes until turn is over
        while(True):
            # modulo 14 to get current hole index from 0-13
            hole = (move + i) % 14

            # don't drop stones in the other player's store
            if hole == skip_index:
                i += 1
                continue

            # add one stone to the current hole
            self.board[hole] = self.board[hole] + 1

            # remove one stone from the hand
            num_active -= 1

            # if last stone has been dropped, check if it
            # was dropped in an emtpy hole or not
            if num_active == 0:
                # if the hole is a store, the player gets another turn
                if hole == store_index:
                    message = 'Free turn!'
                    break
                # if hole was emtpy (ie it now has one stone)...
                if self.board[hole] == 1:
                    # ...the turn is finished
                    self.myturn *= -1
                    message = 'Turn finished.\n----------------------------------------'
                    break
                # otherwise, continue turn
                else:
                    num_active = self.board[hole]
                    self.board[hole] = 0
                
            # move to the next hole
            i += 1

        # check if the game has ended
        if all(self.board[0:6] == np.zeros(6)) or all(self.board[7:13] == np.zeros(6)):
            self.gameover = True
            if not self.issim:
                self.PrintBoard()
            return 1
            
        if not self.issim:
            self.PrintBoard()
            print(message)
            print("Player {}'s turn".format((self.myturn+3)%3))
        return 0

    def ConvertMove(self,move):
        if self.myturn == 1:
            return move - 1
        else:
            return 13 - move
        
    def CheckWinner(self):
        if self.board[6]>self.board[13]:
            print('Player 1 wins!')
            return 1
        elif self.board[6]<self.board[13]:
            print('Player 2 wins!')
            return 2
        else:
            print("It's a tie!")
            return 0

    def SetupBoard(self):
        self.board = np.zeros(14).astype(int)
        print('Input the starting number of stones in each hole,')
        print('from top to bottom, left to right.')
        for j in range(6):
            self.board[j] = int(input('Number of stones:\t'))
            self.PrintBoard()
            self.board[12-j] = int(input('Number of stones:\t'))
            self.PrintBoard()

    def PrintBoard(self):
        print('-------------')
        print('|    '+' '*(2-len(str(self.board[13])))+str(self.board[13])+'     |')
        print('-------------')
        for j in range(6):
            left = str(self.board[j])
            right = str(self.board[12-j])
            print('|'+' '*(3-len(left))+left+'  |'+' '*(3-len(right))+right+'  |')
        print('-------------')
        print('|    '+' '*(2-len(str(self.board[6])))+str(self.board[6])+'     |')
        print('-------------')

    def GetWinsAndPoints(self,depth=6):
        board = copy.deepcopy(self.board)
        myturn = copy.deepcopy(self.myturn)
        points = np.zeros(6)
        games = np.zeros(6)
        for j in range(6):
            self.board = copy.deepcopy(board)
            self.myturn = copy.deepcopy(myturn)
            self.gameover = False
            result = self.PlayMove(self.ConvertMove(j+1))
            if result == -1:
                continue
            if depth==0 or result==1:
                points[j] += self.CheckPointDifferential()
                games[j] += 1
                continue
            pts,gms = self.GetWinsAndPoints(depth-1)
            points[j] += np.sum(pts)
            games[j] += np.sum(gms)
        self.board = copy.deepcopy(board)
        self.myturn = copy.deepcopy(myturn)
        self.gameover = False
        return points, games
    
    def CheckPointDifferential(self):
        # points of player 2 minus player 1 since the bot always plays
        # as player 2 and tries to maximize the differential in its own favor
        return self.board[13] - self.board[6]

    def FindBestMove(self,depth):
        self.issim = True
        pts,gms = self.GetWinsAndPoints(depth)
        print('Playing out {:.0f} possible scenarios...'.format(sum(gms)))
        gms[gms==0] = -1e-6
        num_pts = pts/gms
        if self.myturn==1:
            board = self.board[0:6]
        else:
            board = np.flip(self.board[-7:-1])
        max_pts = max(num_pts[board!=0])
        move = np.argwhere(num_pts==max_pts)[0][0]
        print('Play move '+str(move+1)+'.')
        self.issim = False
        return move + 1
        
if __name__=='__main__':
    mc = MancalaBot()
    mc.StartGame()

