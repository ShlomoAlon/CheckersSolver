from __future__ import annotations
from collections import defaultdict

import argparse
import sys
from typing import *


def n():
    return None

class TTableEntry:
    depth: int
    score: int
    upper_bound: bool
    lower_bound: bool
    exact: bool
    state: State
    def __init__(self, depth: int, score: int, state: State):
        self.depth = depth
        self.score = score
        self.state = state
        self.upper_bound = False
        self.lower_bound = False
        self.exact = False


cache: DefaultDict[str, Optional[TTableEntry]] = defaultdict(n)


class Direction:
    x: int
    y: int

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __add__(self, other: Direction) -> Direction:
        return Direction(self.x + other.x, self.y + other.y)

    def __mul__(self, other: int) -> Direction:
        return Direction(self.x * other, self.y * other)


UPPER_LEFT = Direction(-1, -1)
UPPER_RIGHT = Direction(1, -1)
LOWER_LEFT = Direction(-1, 1)
LOWER_RIGHT = Direction(1, 1)


def directions(piece: str, player: str) -> List[Direction]:
    # red moves up, black moves down
    if player == 'r':
        if piece == 'r':
            return [UPPER_LEFT, UPPER_RIGHT]
        elif piece == 'R':
            return [UPPER_LEFT, UPPER_RIGHT, LOWER_LEFT, LOWER_RIGHT]
        else:
            return []
    else:
        if piece == 'b':
            return [LOWER_LEFT, LOWER_RIGHT]
        elif piece == 'B':
            return [UPPER_LEFT, UPPER_RIGHT, LOWER_LEFT, LOWER_RIGHT]
        else:
            return []


class Heuristic:
    def score(self, state: State, player: str, depth: int, original_depth: int):
        raise NotImplementedError


class SimplePieceCount(Heuristic):
    def score(self, state: State, player: str, depth: int, original_depth: int):
        player_count = 0
        opp_player_count = 0
        for x in range(8):
            for y in range(8):
                piece = state[Direction(x, y)]
                if piece.lower() == player:
                    player_count += 1
                elif piece.lower() == get_next_turn(player):
                    opp_player_count += 1

        if player_count == 0:
            return -100000 + (original_depth - depth)
        return player_count - opp_player_count


class State:
    # This class is used to represent a state.
    # board : a list of lists that represents the 8*8 board
    def __init__(self, board):
        self.suc = None
        self.board = board

    def __str__(self):
        return '\n'.join(''.join(row) for row in self.board)

    def __getitem__(self, item: Direction):
        if item.x < 0 or item.x > 7 or item.y < 0 or item.y > 7:
            return None
        else:
            return self.board[item.y][item.x]

    def __setitem__(self, item: Direction, value: str):
        self.board[item.y] = self.board[item.y][:]  # copy the list
        self.board[item.y][item.x] = value

    def __copy__(self):
        new_state = State(self.board[:])
        return new_state

    def all_jumps(self, player: str) -> List[State]:
        jumps = []
        for x in range(8):
            for y in range(8):
                location = Direction(x, y)
                piece = self[location]
                for direction in directions(piece, player):
                    single_move = location + direction
                    jump = single_move + direction
                    if self[single_move] in get_opp_char(player) and self[jump] == '.':
                        new_state = self.__copy__()
                        new_state[jump] = new_state[location]
                        new_state[location] = '.'
                        new_state[single_move] = '.'
                        if jump.y == 0 and player == 'r' or jump.y == 7 and player == 'b':
                            new_state[jump] = player.upper()
                            jumps.append(new_state)
                            continue

                        double_jumps = new_state.all_jumps(player)
                        if double_jumps:
                            jumps.extend(double_jumps)
                        else:
                            jumps.append(new_state)
        return jumps

    def simple_moves(self, player: str) -> List[State]:
        moves = []
        for x in range(8):
            for y in range(8):
                location = Direction(x, y)
                piece = self[location]
                for direction in directions(piece, player):
                    move = location + direction
                    if self[move] == '.':
                        new_state = self.__copy__()
                        new_state[move] = new_state[location]
                        new_state[location] = '.'
                        if move.y == 0 and player == 'r' or move.y == 7 and player == 'b':
                            new_state[move] = player.upper()
                        moves.append(new_state)
        return moves

    def generate_successors(self, player: str) -> List[State]:
        if self.suc:
            return self.suc
        jumps = self.all_jumps(player)
        if jumps:
            self.suc = jumps
        else:
            self.suc = self.simple_moves(player)
        return self.suc

    def negamax(self, player: str, depth: int, alpha: int, beta: int, score_mechanism: Heuristic,
                original_depth: int) -> Tuple[int, Optional[State]]:
        original_alpha = alpha
        state_str = str(self) + player
        lookup = cache[state_str]
        if lookup:
            diff = lookup.depth - depth
            if lookup.score > 900000:
                 actual_score = lookup.score - diff
            elif lookup.score < -900000:
                actual_score = lookup.score + diff
            else:
                actual_score = lookup.score
            if lookup.exact and (lookup.score > 900000 or lookup.score < -900000):
                return actual_score, lookup.state
            if lookup.depth >= depth:
                if lookup.lower_bound:
                    alpha = max(alpha, actual_score)
                elif lookup.upper_bound:
                    beta = min(beta, actual_score)
                elif lookup.exact:
                    return actual_score, lookup.state
                if alpha >= beta:
                    return actual_score, lookup.state





        if depth == 0:
            return score_mechanism.score(self, player, depth, original_depth), None
        successor_states = self.generate_successors(player)
        # successor_states = sorted(successor_states, key=lambda succ: len(succ.generate_successors(get_next_turn(player))))
        if not successor_states:
            return -100000 + (original_depth - depth), None
        best_state = None
        best_score = -100000
        for s in successor_states:
            score, _ = s.negamax(get_next_turn(player), depth - 1, -beta, -alpha, score_mechanism, original_depth)
            score = -score
            # if depth == original_depth:
            #     print("score: ", score)
            #     s.display()
            #     print("best score: ", best_score)
            #     if best_state:
            #         best_state.display()
            if score > best_score:
                best_score = score
                best_state = s
                alpha = max(alpha, score)
                if alpha >= beta:
                    break
        new_cache_entry = TTableEntry(depth, best_score, best_state)
        if best_score <= original_alpha:
            new_cache_entry.upper_bound = True
        elif best_score >= beta:
            new_cache_entry.lower_bound = True
        else:
            new_cache_entry.exact = True
        cache[state_str] = new_cache_entry
        return best_score, best_state

    def play(self, player: str, depth: int, heuristic1: Heuristic, heuristic2: Heuristic) -> List[State]:
        state = self
        player = player
        seen_states = []
        while state:
            seen_states.append(state)
            score, new_state = state.negamax(player, depth, -100000, 100000, heuristic1, depth)
            # print("Score: ", score)
            # state.display()
            player = get_next_turn(player)
            state = new_state

        return seen_states

    def display(self):
        for i in self.board:
            for j in i:
                print(j, end="")
            print("")
        print("")


def get_opp_char(player):
    if player in ['b', 'B']:
        return ['r', 'R']
    else:
        return ['b', 'B']


def get_next_turn(curr_turn):
    if curr_turn == 'r':
        return 'b'
    else:
        return 'r'


def read_from_file(filename):
    f = open(filename)
    lines = f.readlines()
    board = [[str(x) for x in l.rstrip()] for l in lines]
    f.close()

    return board


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--inputfile",
        type=str,
        required=True,
        help="The input file that contains the puzzles."
    )
    parser.add_argument(
        "--outputfile",
        type=str,
        required=True,
        help="The output file that contains the solution."
    )
    args = parser.parse_args()

    initial_board = read_from_file(args.inputfile)
    state = State(initial_board)
    # value, state = state.negamax('r', 5, -100000, 100000, SimplePieceCount())
    # state.display()
    # value, state = state.negamax('b', 5, -100000, 100000, SimplePieceCount())
    # state.display()
    # value, state = state.negamax('r', 5, -100000, 100000, SimplePieceCount())
    # state.display()
    #
    # print(state.negamax('b', 5, -100000, 100000, SimplePieceCount()))
    # value, state = state.negamax('r', 5, -100000, 100000, SimplePieceCount())
    # state.display()

    game = state.play('r', 13, SimplePieceCount(), SimplePieceCount())
    with open(args.outputfile, 'w') as f:
        f.write("\n\n".join([str(s) for s in game]))
    # for state in game:
    # state.display()
