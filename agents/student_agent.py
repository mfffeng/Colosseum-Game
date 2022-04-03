# Student agent: Add your own agent here
from cmath import inf
from multiprocessing.sharedctypes import Value
from agents.agent import Agent
from store import register_agent
import numpy as np
import sys



@register_agent("student_agent")
class StudentAgent(Agent):
    """
    A dummy class for your implementation. Feel free to use this class to
    add any helper functionalities needed for your agent.
    """

    def __init__(self):
        super(StudentAgent, self).__init__()
        self.name = "StudentAgent"
        self.dir_map = {
            "u": 0,
            "r": 1,
            "d": 2,
            "l": 3,
        }
        self.moves = ((-1, 0), (0, 1), (1, 0), (0, -1))
        
 
    def check_endgame(self, board_size, chessboard, p0_pos, p1_pos):
        """
        Check if the game ends and compute the current score of the agents.

        Returns
        -------
        is_endgame : bool
            Whether the game ends.
        player_1_score : int
            The score of player 1.
        player_2_score : int
            The score of player 2.
        """
        # Union-Find
        father = dict()
        for r in range(board_size):
            for c in range(board_size):
                father[(r, c)] = (r, c)

        def find(pos):
            if father[pos] != pos:
                father[pos] = find(father[pos])
            return father[pos]

        def union(pos1, pos2):
            father[pos1] = pos2

        for r in range(board_size):
            for c in range(board_size):
                for dir, move in enumerate(self.moves[1:3]):  # Only check down and right
                    if chessboard[r, c, dir + 1]:
                        continue
                    pos_a = find((r, c))
                    pos_b = find((r + move[0], c + move[1]))
                    if pos_a != pos_b:
                        union(pos_a, pos_b)

        for r in range(board_size):
            for c in range(board_size):
                find((r, c))
        p0_r = find(tuple(p0_pos))
        p1_r = find(tuple(p1_pos))
        p0_score = list(father.values()).count(p0_r)
        p1_score = list(father.values()).count(p1_r)
        if p0_r == p1_r:
            return False, p0_score, p1_score
        return True, p0_score, p1_score

    def random_move_heuristic(self, chess_board, my_pos, adv_pos):
        endgame = (False, 1, 1)
        board_size = chess_board.shape[0]
        new_board = np.copy(chess_board)
        while not endgame[0]:
            indices = np.where(new_board == False)
            rand_ind = np.random.randint(0, len(indices[0]))
            r = indices[0][rand_ind]
            c = indices[1][rand_ind]
            dir = indices[2][rand_ind]
            # Place barrier
            new_board[r, c, dir] = True
            # Place barrier on opposite side
            move = self.moves[dir]
            new_board[r + move[0], c + move[1], (dir + 2) % 4] = True
            endgame = self.check_endgame(board_size, new_board, my_pos, adv_pos);    
        # our score - their score
        return endgame[2] - endgame[1]        

    # returns a, b,, score 
    def a_b_pruning(self, chess_board, my_pos, adv_pos, max_step, alpha=-inf, beta=inf, is_max=True, level=0):
        board_size = chess_board.shape[0]

        # Check if leaf node                
        endgame = self.check_endgame(board_size, chess_board, my_pos, adv_pos)
        if endgame[0]:
            # If it's leaf, return the score
            return endgame[1] - endgame[2]

        # Heuristic at depth 4    
        if level >= 2:
            return self.random_move_heuristic(chess_board, my_pos, adv_pos) 
        og_pos = my_pos if is_max else adv_pos
        other_pos = adv_pos if is_max else my_pos
        # Start w/ adv so we don't add it
        potential_places = [] # Make sure we don't add it
        frontier = [(og_pos[0],og_pos[1],0)] # Last number indicates the depth
        while frontier:
            nx, ny, step = frontier.pop()
            # Don't expand nodes @ max step 
            if step == max_step:
                potential_places.append( (nx, ny) )
                continue
            # self.moves[0] = (-1,0)
            if not chess_board[nx, ny, 0]:
                new_pos = (nx - 1, ny)
                if new_pos not in potential_places:
                    frontier.append((new_pos[0], new_pos[1], step+1))
            # self.moves[1] = (0, 1)    
            if not chess_board[nx, ny, 1]:
                new_pos = (nx, ny + 1)
                if new_pos not in potential_places:
                    frontier.append((new_pos[0], new_pos[1], step+1))

            # self.moves[2] = (1, 0)       
            if not chess_board[nx, ny, 2]:
                new_pos = (nx + 1, ny)
                if new_pos not in potential_places:
                    frontier.append((new_pos[0], new_pos[1], step+1))
            # self.moves[3] = (0, -1)    
            if not chess_board[nx, ny, 3]:
                new_pos =(nx, ny - 1)
                if new_pos not in potential_places:
                    frontier.append((new_pos[0], new_pos[1], step+1))
            potential_places.append( (nx, ny) )    
        try:
            potential_places.remove(other_pos)   
        except ValueError:
            pass           
        # Otherwise, loop over successors    
        if is_max:
            for i in potential_places:
                for dir in [0,1,2,3]:
                    if chess_board[ i[0], i[1], dir]:
                        continue
                    # Make change 
                    chess_board[i[0], i[1], dir] = True
                    move = self.moves[dir]
                    chess_board[i[0] + move[0], i[1] + move[1], (dir + 2) % 4] = True
                    # Recursive
                    min_val = self.a_b_pruning(chess_board, i, adv_pos, max_step, alpha, beta, False, level+1)
                    alpha = max(alpha, min_val)
                    # Undo Change
                    chess_board[i[0], i[1], dir] = False
                    chess_board[i[0] + move[0], i[1] + move[1], (dir+ 2) % 4] = False
                    if alpha >= beta:
                        return beta
            return alpha
        else:
            for i in potential_places:
                for dir in [0,1,2,3]:
                    if chess_board[ i[0], i[1], dir]:
                        continue
                    # Make Change
                    chess_board[i[0], i[1], dir] = True
                    move = self.moves[dir]
                    chess_board[i[0] + move[0], i[1] + move[1], (dir + 2) % 4] = True
                    # Recursive
                    max_val = self.a_b_pruning(chess_board, my_pos, i, max_step, alpha, beta, True, level+1)
                    beta = min(beta, max_val)
                    # Undo Change
                    chess_board[i[0], i[1], dir] = False
                    chess_board[i[0] + move[0], i[1] + move[1], (dir+ 2) % 4] = False
                    if alpha >= beta:
                        return alpha
            return beta


    def step(self, chess_board, my_pos, adv_pos, max_step):
        """
        Implement the step function of your agent here.
        You can use the following variables to access the chess board:
        - chess_board: a numpy array of shape (x_max, y_max, 4)
        - my_pos: a tuple of (x, y)
        - adv_pos: a tuple of (x, y)
        - max_step: an integer

        You should return a tuple of ((x, y), dir),
        where (x, y) is the next position of your agent and dir is the direction of the wall
        you want to put on.

        Please check the sample implementation in agents/random_agent.py or agents/human_agent.py for more details.
        """
        # Do first ab_pruning level ourselves
        potential_places = [] # Make sure we don't add it
        frontier = [(my_pos[0],my_pos[1],0)] # Last number indicates the depth
        while frontier:
            nx, ny, step = frontier.pop()
            # Don't expand nodes @ max step 
            if step == max_step:
                potential_places.append( (nx, ny) )
                continue
            # self.moves[0] = (-1,0)
            if not chess_board[nx, ny, 0]:
                new_pos = (nx - 1, ny)
                if new_pos not in potential_places:
                    frontier.append((new_pos[0], new_pos[1], step+1))
            # self.moves[1] = (0, 1)    
            if not chess_board[nx, ny, 1]:
                new_pos = (nx, ny + 1)
                if new_pos not in potential_places:
                    frontier.append((new_pos[0], new_pos[1], step+1))

            # self.moves[2] = (1, 0)       
            if not chess_board[nx, ny, 2]:
                new_pos = (nx + 1, ny)
                if new_pos not in potential_places:
                    frontier.append((new_pos[0], new_pos[1], step+1))
            # self.moves[3] = (0, -1)    
            if not chess_board[nx, ny, 3]:
                new_pos =(nx, ny - 1)
                if new_pos not in potential_places:
                    frontier.append((new_pos[0], new_pos[1], step+1))
            potential_places.append( (nx, ny) )
        potential_places.remove(adv_pos)   
        try:
            potential_places.remove(adv_pos)   
        except ValueError:
            pass            
        # Start ab pruning       
        alpha = -inf
        beta = inf
        for i in potential_places:
            for dir in [0,1,2,3]:
                if chess_board[ i[0], i[1], dir]:
                    continue
                # Make change 
                chess_board[i[0], i[1], dir] = True
                move = self.moves[dir]
                chess_board[i[0] + move[0], i[1] + move[1], (dir + 2) % 4] = True
                # Recursive
                min_val = self.a_b_pruning(chess_board, i, adv_pos, max_step, alpha, beta, False, 1)
                if min_val > alpha:
                    best_move = i
                    best_dir = dir
                    alpha = min_val   
                # Undo Change
                chess_board[i[0], i[1], dir] = False
                chess_board[i[0] + move[0], i[1] + move[1], (dir+ 2) % 4] = False
        return best_move, best_dir
