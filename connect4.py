import tkinter as tk
from tkinter import ttk
from matplotlib.pyplot import grid
import numpy as np
import random as rnd
from threading import Thread
from queue import Queue


disk_color = ['white', 'red', 'orange']
disks = list()

player_type = ['human']
for i in range(42):
    player_type.append('AI: alpha-beta level '+str(i+1))

def alpha_beta_decision(board, turn, ai_level, queue, max_player):
    opponent = 1 if max_player == 2 else 2
    depth_limit = max(1, ai_level)

    def is_winning_move(board, move, player):
        tmp = board.copy()
        tmp.add_disk(move, player, update_display=False)
        return tmp.check_victory() == player
    
    def winning_moves(board, player):
        return [
            move for move in board.get_possible_moves()
            if is_winning_move(board, move, player)
        ]
    
    def is_fork(board, move, player):
        tmp = board.copy()
        tmp.add_disk(move, player, update_display=False)
        return len(winning_moves(tmp, player)) >= 2

    def fork_moves(board, player):
        return [
            move for move in board.get_possible_moves()
            if is_fork(board, move, player)
        ]

    def opponent_fork_moves(board, opponent):
        forks = []
        for move in board.get_possible_moves():
            tmp = board.copy()
            tmp.add_disk(move, opponent, update_display=False)
            if len(winning_moves(tmp, opponent)) >= 2:
                forks.append(move)
        return forks
    
    def forced_move(board, moves):
        """
        Choisit un coup même perdant, en privilégiant
        la terminaison rapide de la partie.
        """
        for move in moves:
            tmp = board.copy()
            tmp.add_disk(move, max_player, update_display=False)
            if winning_moves(tmp, opponent):
                return move
        return moves[0]

    def terminal_move(board, moves):
        best = None
        best_score = float('inf')

        for move in moves:
            tmp = board.copy()
            tmp.add_disk(move, max_player, update_display=False)

            if winning_moves(tmp, opponent):
                return move

            score = tmp.eval(max_player)
            if score < best_score:
                best_score = score
                best = move

        return best
    
    def max_value(board, alpha, beta, depth):
        w = board.check_victory()
        if w == max_player:
            return 1_000_000 + depth
        elif w == opponent:
            return -1_000_000 - depth
        elif depth == 0:
            return board.eval(max_player)

        v = -float('inf')
        for move in board.get_possible_moves():
            new_board = board.copy()
            new_board.add_disk(move, max_player, update_display=False)
            v = max(v, min_value(new_board, alpha, beta, depth - 1))
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    def min_value(board, alpha, beta, depth):
        w = board.check_victory()
        if w == max_player:
            return 1_000_000
        elif w == opponent:
            return -1_000_000
        elif depth == 0:
            return board.eval(max_player)

        v = float('inf')
        for move in board.get_possible_moves():
            new_board = board.copy()
            new_board.add_disk(move, opponent, update_display=False)
            v = min(v, max_value(new_board, alpha, beta, depth - 1))
            if v <= alpha:
                return v
            beta = min(beta, v)
        return v

    best_score = -float('inf')
    best_move = None

    possible_moves = board.get_possible_moves()

    # Immediate win
    for move in possible_moves:
        if is_winning_move(board, move, max_player):
            queue.put(move)
            return

    # Block opponent immediate win
    opp_wins = winning_moves(board, opponent)
    if opp_wins:
        queue.put(opp_wins[0])
        return
    
    # Block opponent forks
    opp_forks = opponent_fork_moves(board, opponent)
    if opp_forks:
        # Try to block the fork by playing in one of the fork columns
        for move in possible_moves:
            tmp = board.copy()
            tmp.add_disk(move, max_player, update_display=False)
            if not opponent_fork_moves(tmp, opponent):
                queue.put(move)
                return

        # If no clean block exists, force best defense
        queue.put(opp_forks[0])
        return
    
    # Create a fork if possible
    forks = fork_moves(board, max_player)
    if forks:
        queue.put(forks[0])
        return

    # Avoid giving opponent an immediate win
    safe_moves = []
    for move in possible_moves:
        tmp = board.copy()
        tmp.add_disk(move, max_player, update_display=False)

        if not winning_moves(tmp, opponent):
            safe_moves.append(move)


    if not safe_moves:
        queue.put(terminal_move(board, possible_moves))
        return

    moves_to_evaluate = safe_moves if safe_moves else possible_moves

    

    # Strategic evaluation (alpha–beta)
    best_score = -float('inf')
    best_move = None

    for move in moves_to_evaluate:
        tmp = board.copy()
        tmp.add_disk(move, max_player, update_display=False)
        score = min_value(tmp, -float('inf'), float('inf'), depth_limit - 1)

        if score > best_score:
            best_score = score
            best_move = move

    if best_move is None:
        queue.put(forced_move(board, possible_moves))
        return

    queue.put(best_move)


class Board:
    grid = np.array([[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]])

    def is_playable(self, col, row):
        return row == 0 or self.grid[col][row - 1] != 0
    
    def score_window(self, window, coords, player):
        opponent = 1 if player == 2 else 2

        count_p = np.count_nonzero(window == player)
        count_o = np.count_nonzero(window == opponent)
        empties = [(c, r) for (c, r), v in zip(coords, window) if v == 0]

        if count_o > 0 and count_p > 0:
            return 0

        # WIN
        if count_p == 4:
            return 1_000_000

        # IMMEDIATE WIN THREAT
        if count_p == 3 and len(empties) == 1:
            c, r = empties[0]
            if self.is_playable(c, r):
                return 50_000
            return 200  # future threat

        # TWO-IN-A-ROW
        if count_p == 2 and len(empties) == 2:
            playable = sum(self.is_playable(c, r) for c, r in empties)
            if playable == 2:
                return 500
            elif playable == 1:
                return 50

        # BLOCK OPPONENT
        if count_o == 3 and len(empties) == 1:
            c, r = empties[0]
            if self.is_playable(c, r):
                return -80_000

        return 0   
                          
    
    def winning_moves(self, player):
        wins = []
        for move in self.get_possible_moves():
            tmp = self.copy()
            tmp.add_disk(move, player, update_display=False)
            if tmp.check_victory() == player:
                wins.append(move)
        return wins
    
    def eval(self, player):
        score = 0

        # Centre
        for row in range(6):
            if self.grid[3][row] == player:
                score += 6

        # Pour chaque fenêtre de 4 :
        # Horizontal
        for row in range(6):
            for col in range(4):
                window = self.grid[col:col+4, row]
                coords = [(col+i, row) for i in range(4)]
                score += self.score_window(window, coords, player)

        # Vertical
        for col in range(7):
            for row in range(3):
                window = self.grid[col, row:row+4]
                coords = [(col, row+i) for i in range(4)]
                score += self.score_window(window, coords, player)

        # Diagonal (bottom-left to top-right)
        for col in range(4):
            for row in range(3):
                window = np.array([self.grid[col + i][row + i] for i in range(4)])
                coords = [(col + i, row + i) for i in range(4)]
                score += self.score_window(window, coords, player)
        
        # Diagonal (top-left to bottom-right)
        for col in range(4):
            for row in range(3, 6):
                window = np.array([self.grid[col + i][row - i] for i in range(4)])
                coords = [(col + i, row - i) for i in range(4)]
                score += self.score_window(window, coords, player)

        #fork opportunities
        forks = 0
        for move in self.get_possible_moves():
            tmp = self.copy()
            tmp.add_disk(move, player, update_display=False)
            if len(tmp.winning_moves(player)) >= 2:
                forks += 1

        score += forks * 15_000


        return score
    

    def copy(self):
        new_board = Board()
        new_board.grid = np.array(self.grid, copy=True)
        return new_board

    def reinit(self):
        self.grid.fill(0)
        for i in range(7):
            for j in range(6):
                canvas1.itemconfig(disks[i][j], fill=disk_color[0])

    def get_possible_moves(self):
        possible_moves = list()
        if self.grid[3][5] == 0:
            possible_moves.append(3)
        for shift_from_center in range(1, 4):
            if self.grid[3 + shift_from_center][5] == 0:
                possible_moves.append(3 + shift_from_center)
            if self.grid[3 - shift_from_center][5] == 0:
                possible_moves.append(3 - shift_from_center)
        return possible_moves

    def add_disk(self, column, player, update_display=True):
        for j in range(6):
            if self.grid[column][j] == 0:
                break
        self.grid[column][j] = player
        if update_display:
            canvas1.itemconfig(disks[column][j], fill=disk_color[player])

    def column_filled(self, column):
        return self.grid[column][5] != 0

    def check_victory(self):
        # Horizontal
        for line in range(6):
            for col in range(4):
                v = self.grid[col][line]
                if v != 0 and v == self.grid[col+1][line] == self.grid[col+2][line] == self.grid[col+3][line]:
                    return v

        # Vertical
        for col in range(7):
            for row in range(3):
                v = self.grid[col][row]
                if v != 0 and v == self.grid[col][row+1] == self.grid[col][row+2] == self.grid[col][row+3]:
                    return v

        # Diagonals
        for col in range(4):
            for row in range(3):
                v = self.grid[col][row]
                if v != 0 and v == self.grid[col+1][row+1] == self.grid[col+2][row+2] == self.grid[col+3][row+3]:
                    return v

                v = self.grid[col][row+3]
                if v != 0 and v == self.grid[col+1][row+2] == self.grid[col+2][row+1] == self.grid[col+3][row]:
                    return v

        return 0


class Connect4:

    def __init__(self):
        self.board = Board()
        self.human_turn = False
        self.turn = 1
        self.players = (0, 0)
        self.ai_move = Queue()

    def current_player(self):
        return 2 - (self.turn % 2)

    def launch(self):
        self.board.reinit()
        self.turn = 0
        information['fg'] = 'black'
        information['text'] = "Turn " + str(self.turn) + " - Player " + str(
            self.current_player()) + " is playing"
        self.human_turn = False
        self.players = (combobox_player1.current(), combobox_player2.current())
        self.handle_turn()

    def move(self, column):
        if not self.board.column_filled(column):
            self.board.add_disk(column, self.current_player())
            self.handle_turn()

    def click(self, event):
        if self.human_turn:
            column = event.x // row_width
            self.move(column)

    def ai_turn(self, ai_level):
        Thread(target=alpha_beta_decision, args=(self.board, self.turn, ai_level, self.ai_move, self.current_player(),)).start()
        self.ai_wait_for_move()

    def ai_wait_for_move(self):
        if not self.ai_move.empty():
            self.move(self.ai_move.get())
        else:
            window.after(100, self.ai_wait_for_move)

    def handle_turn(self):
        self.human_turn = False
        if self.board.check_victory():
            information['fg'] = 'red'
            information['text'] = "Player " + str(self.current_player()) + " wins !"
            return
        elif self.turn >= 42:
            information['fg'] = 'red'
            information['text'] = "This a draw !"
            return
        self.turn = self.turn + 1
        information['text'] = "Turn " + str(self.turn) + " - Player " + str(
            self.current_player()) + " is playing"
        if self.players[self.current_player() - 1] != 0:
            self.human_turn = False
            self.ai_turn(self.players[self.current_player() - 1])
        else:
            self.human_turn = True


game = Connect4()

# Graphical settings
width = 700
row_width = width // 7
row_height = row_width
height = row_width * 6
row_margin = row_height // 10

window = tk.Tk()
window.title("Connect 4")
canvas1 = tk.Canvas(window, bg="blue", width=width, height=height)

# Drawing the grid
for i in range(7):
    disks.append(list())
    for j in range(5, -1, -1):
        disks[i].append(canvas1.create_oval(row_margin + i * row_width, row_margin + j * row_height, (i + 1) * row_width - row_margin,
                            (j + 1) * row_height - row_margin, fill='white'))


canvas1.grid(row=0, column=0, columnspan=2)

information = tk.Label(window, text="")
information.grid(row=1, column=0, columnspan=2)

label_player1 = tk.Label(window, text="Player 1: ")
label_player1.grid(row=2, column=0)
combobox_player1 = ttk.Combobox(window, state='readonly')
combobox_player1.grid(row=2, column=1)

label_player2 = tk.Label(window, text="Player 2: ")
label_player2.grid(row=3, column=0)
combobox_player2 = ttk.Combobox(window, state='readonly')
combobox_player2.grid(row=3, column=1)

combobox_player1['values'] = player_type
combobox_player1.current(0)
combobox_player2['values'] = player_type
combobox_player2.current(6)

button2 = tk.Button(window, text='New game', command=game.launch)
button2.grid(row=4, column=0)

button = tk.Button(window, text='Quit', command=window.destroy)
button.grid(row=4, column=1)

# Mouse handling
canvas1.bind('<Button-1>', game.click)

window.mainloop()
