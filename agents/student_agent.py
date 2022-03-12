# Student agent: Add your own agent here
from agents.agent import Agent
from store import register_agent
import sys


def check_endgame(self):
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
    for r in range(self.board_size):
        for c in range(self.board_size):
            father[(r, c)] = (r, c)

    def find(pos):
        if father[pos] != pos:
            father[pos] = find(father[pos])
        return father[pos]

    def union(pos1, pos2):
        father[pos1] = pos2

    for r in range(self.board_size):
        for c in range(self.board_size):
            for dir, move in enumerate(
                self.moves[1:3]
            ):  # Only check down and right
                if self.chess_board[r, c, dir + 1]:
                    continue
                pos_a = find((r, c))
                pos_b = find((r + move[0], c + move[1]))
                if pos_a != pos_b:
                    union(pos_a, pos_b)

    for r in range(self.board_size):
        for c in range(self.board_size):
            find((r, c))
    p0_r = find(tuple(self.p0_pos))
    p1_r = find(tuple(self.p1_pos))
    p0_score = list(father.values()).count(p0_r)
    p1_score = list(father.values()).count(p1_r)
    if p0_r == p1_r:
        return False, p0_score, p1_score
    player_win = None
    win_blocks = -1
    if p0_score > p1_score:
        player_win = 0
        win_blocks = p0_score
    elif p0_score < p1_score:
        player_win = 1
        win_blocks = p1_score
    else:
        player_win = -1  # Tie
    if player_win >= 0:
        logging.info(
            f"Game ends! Player {self.player_names[player_win]} wins having control over {win_blocks} blocks!"
        )
    else:
        logging.info("Game ends! It is a Tie!")
    return True, p0_score, p1_score

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
