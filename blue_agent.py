"""
Izradili: Antonio Heski, Mateo Niksic.

Opis strategije:
1.) Implementirana baza znanja za pohranu otkrivenih podrucja mape,
pozicije zastava oba tima, statusa agenta, i slicno.
2.) Jedan agent je "Flag keeper" te se cijelo vrijeme nalazi ispred
zastave koju brani, a preostala dva agenta istrazuju mapu kako bi
doznali gdje je neprijateljska zastava.
3.) Kada agent pokupi zastavu od neprijatelja, drugi agent ako je ziv
se regrupira te ga prati da sigurno odnese zastavu na cilj.
4.) Ako je neprijatelj uzeo domaću zastavu, a agent se kreće prema
cilju ili domaćoj zastavi kada shvati da nema zastave agent se vraca
na poziciju neprijateljske zastave.
4.) A* algoritam za pronalazak najkraceg puta do zastave i nazad.
5.) Kada agent detektira neprijatelja u svom vidljivom podrucju koristi
algoritam za sortiranje neprijatelja na kojeg ce pucati prema prioritetu.
Prioritet je ubiti neprijateljskog agenta koji drzi zastavu ili najblizeg
neprijatelja.
"""
from config import *
import heapq
import math


class Agent:
    knowledge_base = {
        "map": [["#" if row == 0 or row == HEIGHT - 1 or
                 col == 0 or col == WIDTH - 1 else "/"
                 for col in range(WIDTH)]
                for row in range(HEIGHT)],
        "enemy_flag_positions": [],
        "home_flag_positions": [],
        "friendly_agents_alive": 3,
        "visited": [],
        "enemy_flag_captured": False,
        "friendly_capturer_position": (1, 1),
        "shot_fired": {0: False, 1: False, 2: False},
        "home_flag_captured": False
    }

    def __init__(self, color, index):
        self.color = color
        self.index = index
        self.ENEMY_AGENT_COLOR = ASCII_TILES["red_agent"] if self.color == "blue" else ASCII_TILES["blue_agent"]
        self.ENEMY_FLAG_TILE = ASCII_TILES["red_flag"] if self.color == "blue" else ASCII_TILES["blue_flag"]
        self.HOME_FLAG_TILE = ASCII_TILES["blue_flag"] if self.color == "blue" else ASCII_TILES["red_flag"]

    def knowledge_base_flag_positions_update(self):
        for row in range(len(Agent.knowledge_base["map"])):
            for col in range(len(Agent.knowledge_base["map"][0])):
                tile = Agent.knowledge_base["map"][row][col]
                if tile == self.HOME_FLAG_TILE:
                    if not Agent.knowledge_base["home_flag_positions"]:
                        Agent.knowledge_base["home_flag_positions"].append((row, col))
                    elif Agent.knowledge_base["home_flag_positions"][-1] != (row, col):
                        continue
                if tile == self.ENEMY_FLAG_TILE:
                    if not Agent.knowledge_base["enemy_flag_positions"]:
                        Agent.knowledge_base["enemy_flag_positions"].append((row, col))
                    elif Agent.knowledge_base["enemy_flag_positions"][-1] != (row, col):
                        continue

    def knowledge_base_map_update(self, visible_world, position):
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

                    if tile != "/":
                        if tile in [ASCII_TILES["red_agent"],
                                    ASCII_TILES["red_agent_f"],
                                    ASCII_TILES["blue_agent"],
                                    ASCII_TILES["blue_agent_f"]]:
                            Agent.knowledge_base["map"][row][col] = ASCII_TILES["empty"]
                        else:
                            Agent.knowledge_base["map"][row][col] = tile

    def knowledge_base_map_display(self):
        print("\n===========================\n")
        for row in range(len(Agent.knowledge_base["map"])):
            print(" " + " ".join(Agent.knowledge_base["map"][row]) + " ")

    def knowledge_base_update(self, visible_world, position):
        self.knowledge_base_map_update(visible_world, position)
        self.knowledge_base_flag_positions_update()

    def get_nearby_enemies(self, visible_world):
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

    def astar_reconstruct_path(self, processed, start, goal):
        current = goal
        path = [current]
        while current != start:
            current = processed[current]
            path.append(current)
        path.reverse()
        return path

    def astar_is_valid_neighbor(self, pos, map):
        row, col = pos
        return map[row][col] in [ASCII_TILES["empty"], ASCII_TILES["blue_flag"], ASCII_TILES["red_flag"]]

    def astar_heuristic(self, a, b):
        return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

    def astar(self, agent_position, target_position, map):
        start = agent_position
        goal = target_position

        to_process = []
        heapq.heappush(to_process, (0, start))

        processed = {}
        g_cost = {start: 0}

        while to_process:
            current_priority, current_pos = heapq.heappop(to_process)

            if current_pos == goal:
                return self.astar_reconstruct_path(processed, start, goal)

            neighbors = [(current_pos[0] + 1, current_pos[1]),
                         (current_pos[0] - 1, current_pos[1]),
                         (current_pos[0], current_pos[1] + 1),
                         (current_pos[0], current_pos[1] - 1)]

            for neighbor in neighbors:
                if self.astar_is_valid_neighbor(neighbor, map):
                    tentative_g_cost = g_cost[current_pos] + 1

                    if neighbor not in g_cost or tentative_g_cost < g_cost[neighbor]:
                        g_cost[neighbor] = tentative_g_cost
                        total_cost = tentative_g_cost + self.astar_heuristic(neighbor, goal)
                        heapq.heappush(to_process, (total_cost, neighbor))
                        processed[neighbor] = current_pos

        return []

    def convert_position_to_direction(self, curr_pos, next_pos):
        curr_row, curr_col = curr_pos
        next_row, next_col = next_pos

        vertical_direction = curr_row - next_row
        horizontal_direction = curr_col - next_col

        if vertical_direction > 0:
            return "up"
        elif vertical_direction < 0:
            return "down"

        if horizontal_direction > 0:
            return "left"
        elif horizontal_direction < 0:
            return "right"

    def euclidean_distance(self, point1, point2):
        x1, y1 = point1
        x2, y2 = point2

        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        return distance

    def update(self, visible_world, position, can_shoot, holding_flag):
        action = "move"
        direction = None
        agent_position = position[::-1]
        Agent.knowledge_base["visited"].append(agent_position)

        self.knowledge_base_update(visible_world, position)
        map = Agent.knowledge_base["map"]
        home_flag_position = Agent.knowledge_base["home_flag_positions"][-1] if len(
            Agent.knowledge_base["home_flag_positions"]) else None
        enemy_flag_position = Agent.knowledge_base["enemy_flag_positions"][-1] if len(
            Agent.knowledge_base["enemy_flag_positions"]) else None

        nearby_enemies = self.get_nearby_enemies(visible_world)
        nearby_enemy_direction = nearby_enemies[0]["direction"] if len(nearby_enemies) else None

        if can_shoot and nearby_enemy_direction:
            action = "shoot"
            if Agent.knowledge_base["shot_fired"][self.index]:
                Agent.knowledge_base["shot_fired"][self.index] = False
            Agent.knowledge_base["shot_fired"][self.index] = True
            direction = nearby_enemy_direction
        else:
            if self.index == 0 and Agent.knowledge_base["friendly_agents_alive"] > 1:
                if self.euclidean_distance(agent_position, home_flag_position) > 1:
                    path = self.astar(agent_position, home_flag_position, map)
                    if len(path) > 1:
                        next_position = path.pop(1)
                        direction = self.convert_position_to_direction(agent_position, next_position)
                else:
                    action = "move"
                    direction = None
            else:
                if holding_flag and home_flag_position:
                    Agent.knowledge_base["enemy_flag_positions"] = []
                    Agent.knowledge_base["enemy_flag_captured"] = True
                    Agent.knowledge_base["friendly_capturer_position"] = agent_position

                    path = self.astar(agent_position, home_flag_position, map)
                    if len(path) > 1:
                        next_position = path.pop(1)
                        direction = self.convert_position_to_direction(agent_position, next_position)
                    if agent_position == home_flag_position:
                        Agent.knowledge_base["home_flag_positions"] = []
                        Agent.knowledge_base["enemy_flag_positions"] = []
                elif not holding_flag and Agent.knowledge_base["enemy_flag_captured"]:
                    target = Agent.knowledge_base["friendly_capturer_position"]
                    target_position = (target[0] + 1, target[1])
                    path = self.astar(agent_position, target_position, map)
                    if len(path) > 1:
                        next_position = path.pop(1)
                        direction = self.convert_position_to_direction(agent_position, next_position)
                elif enemy_flag_position is not None:
                    path = self.astar(agent_position, enemy_flag_position, map)
                    if len(path) > 1:
                        next_position = path.pop(1)
                        direction = self.convert_position_to_direction(agent_position, next_position)
                else:
                    if not Agent.knowledge_base["enemy_flag_positions"]:
                        unvisited_positions = [(row, col) for row in range(1, HEIGHT - 1)
                                               for col in range(1, WIDTH - 1) if (row, col) not in Agent.knowledge_base["visited"]]
                        if unvisited_positions:
                            rever = True
                            if self.color == "red":
                                rever = False
                            unvisited_positions = sorted(unvisited_positions, key=lambda x: x[1], reverse=rever)
                            target_position = None
                            for el in unvisited_positions:
                                if Agent.knowledge_base["map"][el[0]][el[1]] == ASCII_TILES["empty"]:
                                    if self.astar(agent_position, el, map) != []:
                                        target_position = el
                                        break
                            path = self.astar(agent_position, target_position, map)
                            if len(path) > 1:
                                next_position = path.pop(1)
                                direction = self.convert_position_to_direction(agent_position, next_position)
                        else:
                            Agent.knowledge_base["visited"] = []

        return action, direction

    def terminate(self, reason):
        if reason == "died":
            Agent.knowledge_base["friendly_agents_alive"] -= 1
            print(self.color, self.index, "died")
            print(f"{self.color} agents left: ", Agent.knowledge_base["friendly_agents_alive"])
