# Student agent: Add your own agent here
from agents.agent import Agent
from store import register_agent
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

    @staticmethod
    def valid_steps(board, my_pos, adv_position, max_step, visited):
        visited.add(my_pos)
        if max_step == 0:
            return []
        moves = ((-1, 0), (0, 1), (1, 0), (0, -1))
        result = []
        for num, m in enumerate(moves):
            x, y = my_pos[0] + m[0], my_pos[1] + m[1]
            if not (0 <= x and x < board.shape[0] and 0 <= y and y < board.shape[1]):
                continue
            # Can't go through boundaries
            if num == 0 and board[my_pos[0], my_pos[1], 0]:
                continue
            if num == 1 and board[my_pos[0], my_pos[1], 1]:
                continue
            if num == 2 and board[my_pos[0], my_pos[1], 2]:
                continue
            if num == 3 and board[my_pos[0], my_pos[1], 3]:
                continue
            can_explore = False
            for direction in (0, 1, 2, 3):
                if not board[x, y, direction] and (x, y) != adv_position and (x, y) not in visited:
                        can_explore = True
                        result.append((x, y, direction))
            if can_explore:
                result += StudentAgent.valid_steps(board, (x, y), adv_position, max_step - 1, visited)
        # Experimental: sort the result to let moves that shorten the distance to the opponent be examined first
        result = sorted(result, key=lambda x: (x[0] - adv_position[0]) ** 2 + (x[1] - adv_position[1] ** 2))[:5]
        return result

    @staticmethod
    def early_evaluation(board, my_pos, adv_pos):
        my_count = 0
        for i in range(max(my_pos[0] - 2, 0), min(my_pos[0] + 2, board.shape[0])):
            for j in range(max(my_pos[1] - 2, 0), min(my_pos[1] + 2, board.shape[1])):
                for k in range(4):
                    if board[i, j, k]:
                        my_count -= 1
        for i in range(max(adv_pos[0] - 2, 0), min(adv_pos[0] + 2, board.shape[0])):
            for j in range(max(adv_pos[1] - 2, 0), min(adv_pos[1] + 2, board.shape[1])):
                for k in range(4):
                    if board[i, j, k]:
                        my_count += 1
        return my_count

    @staticmethod
    def a_b_pruning(board, my_pos, adv_pos, max_step, a, b, is_max, depth):
        if depth == 0:
            result = StudentAgent.early_evaluation(board, my_pos, adv_pos)
            if is_max:
                return (-1, -1, -1, result)
            return (-1, -1, -1, -result)
        # Remove the end game check, since its evaluation metrics (based on the number of tiles each player control)
        # is different from that of the early evaluation's, which is based on the nunmber of walls around each player..
        ''''
        stats = StudentAgent.check_status(board, my_pos, adv_pos)
        if stats[0]:
            if is_max:
                return (-1, -1, -1, stats[1])
            return (-1, -1, -1, -stats[1])      # Invert the score if ending in min player's term'''
        potential_steps = StudentAgent.valid_steps(board, my_pos, adv_pos, max_step, set())
        for d in (0, 1, 2, 3):      # Stay where you are
            if board[my_pos[0], my_pos[1], d] == 0:
                potential_steps.append((my_pos[0], my_pos[1], d))
        if is_max:
            best = (-1, -1, -1, -10000)
            for i in potential_steps:
                board[i[0], i[1], i[2]] = True
                val = StudentAgent.a_b_pruning(board, adv_pos, (i[0], i[1]), max_step, a, b, False, depth - 1)
                board[i[0], i[1], i[2]] = False
                val = (i[0], i[1], i[2], val[3])            
                best = best if best[3] > val[3] else val
                if val[3] < best[3] and best[3] == -10000:
                    print(f'max{val}')
                a = a if a > best[3] else best[3]
                if a >= b:
                    break
            return best
        else:
            best = (-1, -1, -1, 10000)
            for i in potential_steps:
                board[i[0], i[1], i[2]] = True
                val = StudentAgent.a_b_pruning(board, adv_pos, (i[0], i[1]), max_step, a, b, True, depth - 1)
                board[i[0], i[1], i[2]] = False            
                val = (i[0], i[1], i[2], val[3])
                best = best if best[3] < val[3] else val
                b = b if b < best[3] else best[3]
                if a >= b:
                    break
            return best            

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
        output = StudentAgent.a_b_pruning(chess_board, my_pos, adv_pos, max_step, -10000, 10000, True, 3)
        return output[:2], output[2]
