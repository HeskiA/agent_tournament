# Antonio Heski, Mateo Niksic
import random
from config import *


class Agent:
    knowledge_base = {
        'map': [['#' if row == 0 or row == HEIGHT - 1 or
                 col == 0 or col == WIDTH - 1 else '/'
                 for col in range(WIDTH)] for row in range(HEIGHT)],
    }

    def __init__(self, color, index):
        self.color = color  # "blue" or "red"
        self.index = index  # 0, 1, or 2

    def update_knowledge_base(self, visible_world, position, holding_flag):
        if visible_world:
            pos_col = position[0]
            pos_row = position[1]

            col_start = max(1, pos_col - 4)
            col_end = min(len(Agent.knowledge_base["map"][0]) - 1, pos_col + 4) + 1
            row_start = max(1, pos_row - 4)
            row_end = min(len(Agent.knowledge_base["map"]) - 1, pos_row + 4) + 1

            for row in range(row_start, row_end):
                for col in range(col_start, col_end):
                    vw_row = row - row_start
                    vw_col = col - col_start

                    if pos_row - 4 <= 0:
                        vw_row = vw_row + abs(pos_row - 4) + 1

                    if pos_col - 4 <= 0:
                        vw_col = vw_col + abs(pos_col - 4) + 1

                    tile = visible_world[vw_row][vw_col]

                    if tile != "/":
                        if tile in ["r", "R", "b", "B"]:
                            Agent.knowledge_base["map"][row][col] = "."
                        else:
                            Agent.knowledge_base["map"][row][col] = tile

    def display_knowledge_base_map(self):
        for row in range(len(Agent.knowledge_base["map"])):
            print(" " + " ".join(Agent.knowledge_base["map"][row]) + " ")

    def update(self, visible_world, position, can_shoot, holding_flag):

        # apply to all agents
        # print("\n===========================\n")
        # print(f"Color: {self.color},Index: {self.index}, Position: {position}")
        # for row in visible_world:
        #     print(" " + " ".join(row))
        # print("\n===========================\n")
        # self.update_knowledge_base(visible_world, position, holding_flag)
        # self.display_knowledge_base_map()

        # display one agent's vision:
        if self.index == 0:
            print("\n===========================\n")
            print(f"Color: {self.color},Index: {self.index}, Position: {position}")
            for row in visible_world:
                print(" " + " ".join(row))
            print("\n===========================\n")
            self.update_knowledge_base(visible_world, position, holding_flag)
            self.display_knowledge_base_map()

        if can_shoot and random.random() > 0.5:
            action = "shoot"
        else:
            action = "move"

        if self.color == "blue":
            preferred_direction = "right"
            if holding_flag:
                preferred_direction = "left"
        elif self.color == "red":
            preferred_direction = "left"
            if holding_flag:
                preferred_direction = "right"

        r = random.random() * 1.5
        if r < 0.25:
            direction = "left"
        elif r < 0.5:
            direction = "right"
        elif r < 0.75:
            direction = "up"
        elif r < 1.0:
            direction = "down"
        else:
            direction = preferred_direction

        return action, direction

    def terminate(self, reason):
        if reason == "died":
            print(self.color, self.index, "died")
