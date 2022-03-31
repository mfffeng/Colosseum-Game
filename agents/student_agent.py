# Student agent: Add your own agent here
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
        endgame = None
        board_size = chess_board.shape[0]
        new_board = chess_board.deep_copy()
        while not endgame[0]:
            dir = np.random.randint(0, 4)
            r = np.random.randint(0, board_size)
            c = np.random.randint(0, board_size)
            # Put Barrier
            while new_board[r, c, dir]:
                dir = np.random.randint(0, 4)
                r = np.random.randint(0, board_size)
                c = np.random.randint(0, board_size)
            # Place barrier
            new_board[r, c, dir] = True
            # Place barrier on opposite side
            move = self.moves[dir]
            new_board[r + move[0], c + move[1], (dir + 2) % 4] = True
            endgame = self.check_endgame(board_size, new_board, my_pos, adv_pos);    
        # our score - their score
        return endgame[1] - endgame[2]        


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
        # dummy return
        return my_pos, self.dir_map["u"]
