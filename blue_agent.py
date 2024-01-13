# Antonio Heski, Mateo Niksic
import random
from config import *


class Agent:
    knowledge_base = {
        "map": [["#" if row == 0 or row == HEIGHT - 1 or
                 col == 0 or col == WIDTH - 1 else "/"
                 for col in range(WIDTH)]
                for row in range(HEIGHT)],
        "enemy_flag_positions": [],
        "home_flag_positions": []
    }

    def __init__(self, color, index):
        self.color = color  # "blue" or "red"
        self.index = index  # 0, 1, or 2
        self.ENEMY_AGENT_COLOR = ASCII_TILES["red_agent"] if self.color == "blue" else ASCII_TILES["blue_agent"]
        self.ENEMY_FLAG_TILE = ASCII_TILES["red_flag"] if self.color == "blue" else ASCII_TILES["blue_flag"]
        self.HOME_FLAG_TILE = ASCII_TILES["blue_flag"] if self.color == "blue" else ASCII_TILES["red_flag"]

    def update_flag_positions(self):
        for row in range(len(Agent.knowledge_base["map"])):
            for col in range(len(Agent.knowledge_base["map"][0])):
                tile = Agent.knowledge_base["map"][row][col]
                if tile == self.HOME_FLAG_TILE:
                    if not Agent.knowledge_base["home_flag_positions"]:
                        Agent.knowledge_base["home_flag_positions"].append((col, row))
                    elif Agent.knowledge_base["home_flag_positions"][-1] != (col, row):
                        continue
                if tile == self.ENEMY_FLAG_TILE:
                    if not Agent.knowledge_base["enemy_flag_positions"]:
                        Agent.knowledge_base["enemy_flag_positions"].append((col, row))
                    elif Agent.knowledge_base["enemy_flag_positions"][-1] != (col, row):
                        continue

    def update_map(self, visible_world, position):
        if visible_world:
            pos_row = position[1]
            pos_col = position[0]

            row_start = max(1, pos_row - 4)
            row_end = min(len(Agent.knowledge_base["map"]) - 1, pos_row + 4) + 1

            col_start = max(1, pos_col - 4)
            col_end = min(len(Agent.knowledge_base["map"][0]) - 1, pos_col + 4) + 1

            for row in range(row_start, row_end):
                for col in range(col_start, col_end):
                    vw_row = row - row_start
                    vw_col = col - col_start

                    if pos_row - 4 <= 0:
                        vw_row = vw_row + abs(pos_row - 4) + 1

                    if pos_col - 4 <= 0:
                        vw_col = vw_col + abs(pos_col - 4) + 1

                    tile = visible_world[vw_row][vw_col]

                    if tile in [ASCII_TILES["empty"],
                                ASCII_TILES["wall"],
                                ASCII_TILES["blue_flag"],
                                ASCII_TILES["red_flag"]]:
                        Agent.knowledge_base["map"][row][col] = tile

    def display_map(self):
        print("\n===========================\n")
        for row in range(len(Agent.knowledge_base["map"])):
            print(" " + " ".join(Agent.knowledge_base["map"][row]) + " ")

    def update_knowledge_base(self, visible_world, position, holding_flag):
        self.update_map(visible_world, position)
        self.update_flag_positions()

    def detect_nearby_enemies(self, visible_world):
        enemies = []

        vertical_direction = [tile[4] for row, tile in enumerate(visible_world) if row != 4]
        up_direction = vertical_direction[:4][::-1]
        down_direction = vertical_direction[4:]
        left_direction = visible_world[4][:4][::-1]
        right_direction = visible_world[4][5:]

        for position, tile in enumerate(up_direction):
            if tile in [self.ENEMY_AGENT_COLOR, self.ENEMY_AGENT_COLOR.upper()]:
                priority = 1 if tile == self.ENEMY_AGENT_COLOR.upper() else 0
                distance = position + 1
                enemies.append({"priority": priority, "distance": distance, "direction": "up"})

        for position, tile in enumerate(down_direction):
            if tile in [self.ENEMY_AGENT_COLOR, self.ENEMY_AGENT_COLOR.upper()]:
                priority = 1 if tile == self.ENEMY_AGENT_COLOR.upper() else 0
                distance = position + 1
                enemies.append({"priority": priority, "distance": distance, "direction": "down"})

        for position, tile in enumerate(left_direction):
            if tile in [self.ENEMY_AGENT_COLOR, self.ENEMY_AGENT_COLOR.upper()]:
                priority = 1 if tile == self.ENEMY_AGENT_COLOR.upper() else 0
                distance = position + 1
                enemies.append({"priority": priority, "distance": distance, "direction": "left"})

        for position, tile in enumerate(right_direction):
            if tile in [self.ENEMY_AGENT_COLOR, self.ENEMY_AGENT_COLOR.upper()]:
                priority = 1 if tile == self.ENEMY_AGENT_COLOR.upper() else 0
                distance = position + 1
                enemies.append({"priority": priority, "distance": distance, "direction": "right"})

        sorted_enemies = sorted(enemies, key=lambda x: (-x["priority"], x["distance"]))

        return sorted_enemies

    def update(self, visible_world, position, can_shoot, holding_flag):

        # display one agent's vision:
        if self.index == 0:
            print("\n===========================\n")
            print(f"Color: {self.color},Index: {self.index}, Position: {position}")
            for row in visible_world:
                print(" " + " ".join(row))
            self.update_knowledge_base(visible_world, position, holding_flag)
            self.display_map()
            print(Agent.knowledge_base)

        nearby_enemies = self.detect_nearby_enemies(visible_world)

        if can_shoot and len(nearby_enemies):
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

        if action == "shoot":
            direction = nearby_enemies[0]["direction"]

        return action, direction

    def terminate(self, reason):
        if reason == "died":
            print(self.color, self.index, "died")
