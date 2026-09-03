# agent.py
import random
import math
from collections import deque
import heapq
from logic_engine import KnowledgeBase   # <-- NEW: Import the KB


# ========== PRACTICAL 02: Simple Reflex Agent ==========
class SimpleReflexAgent:
    def sense_and_act(self, percept: dict) -> str:
        if percept['food_here']:
            return 'MoveForward'
        if percept['wall_ahead']:
            return 'TurnLeft'
        return 'MoveForward'


# ========== PRACTICAL 02: Model-Based Agent ==========
class ModelBasedAgent:
    def __init__(self):
        self.visited_states = set()
        self.last_action = None

    def sense_and_act(self, percept: dict) -> str:
        state_key = (percept['wall_ahead'], percept['food_here'])
        if state_key in self.visited_states and self.last_action == 'TurnLeft':
            self.last_action = 'TurnRight'
            return 'TurnRight'
        self.visited_states.add(state_key)
        if percept['food_here']:
            action = 'MoveForward'
        elif percept['wall_ahead']:
            action = 'TurnLeft'
        else:
            action = 'MoveForward'
        self.last_action = action
        return action


# ========== PRACTICAL 03 + 04 + 05: Search Agent with Logic ==========
class SearchAgent:
    def __init__(self, algo='BFS'):
        self.active_algo = algo   # 'BFS', 'DFS', 'UCS', 'AStar', 'AStarLogic'
        self.plan = []

        # ========== PRACTICAL 05: Instantiate Knowledge Base ==========
        self.kb = KnowledgeBase()

        # ========== PRACTICAL 05: Define Safety Rules ==========
        # Rule 1: TargetVisible ∧ HasDust ⇒ SafeToEngage
        self.kb.tell_rule(['TargetVisible', 'HasDust'], 'SafeToEngage')
        # Rule 2: SafeToEngage ∧ BloodseekerMissing ⇒ Retreat
        self.kb.tell_rule(['SafeToEngage', 'BloodseekerMissing'], 'Retreat')

    # ========== PRACTICAL 04: Heuristic Functions ==========
    def manhattan_distance(self, pos, goal):
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    def euclidean_distance(self, pos, goal):
        return math.sqrt((pos[0] - goal[0]) ** 2 + (pos[1] - goal[1]) ** 2)

    def _get_neighbors(self, pos, grid_size, walls):
        """Returns valid neighboring absolute coordinates."""
        x, y = pos
        neighbors = []
        if y + 1 < grid_size[1] and (x, y + 1) not in walls:
            neighbors.append((x, y + 1))
        if y - 1 >= 0 and (x, y - 1) not in walls:
            neighbors.append((x, y - 1))
        if x - 1 >= 0 and (x - 1, y) not in walls:
            neighbors.append((x - 1, y))
        if x + 1 < grid_size[0] and (x + 1, y) not in walls:
            neighbors.append((x + 1, y))
        return neighbors

    def _reconstruct_path(self, came_from, start, goal):
        if goal not in came_from:
            return None
        path = []
        current = goal
        while current != start:
            prev = came_from[current]
            dx = current[0] - prev[0]
            dy = current[1] - prev[1]
            if dx == 1:
                action = 'Right'
            elif dx == -1:
                action = 'Left'
            elif dy == 1:
                action = 'Up'
            elif dy == -1:
                action = 'Down'
            path.append(action)
            current = prev
        path.reverse()
        return path

    # ---------- BFS (FIFO Queue) ----------
    def bfs_search(self, start, goal, walls, grid_size):
        if start == goal:
            return []
        frontier = deque()
        frontier.append(start)
        came_from = {start: None}
        while frontier:
            current = frontier.popleft()
            if current == goal:
                return self._reconstruct_path(came_from, start, goal)
            for neighbor in self._get_neighbors(current, grid_size, walls):
                if neighbor not in came_from:
                    came_from[neighbor] = current
                    frontier.append(neighbor)
        return None

    # ---------- DFS (LIFO Stack) ----------
    def dfs_search(self, start, goal, walls, grid_size):
        if start == goal:
            return []
        frontier = [start]
        came_from = {start: None}
        while frontier:
            current = frontier.pop()
            if current == goal:
                return self._reconstruct_path(came_from, start, goal)
            for neighbor in self._get_neighbors(current, grid_size, walls):
                if neighbor not in came_from:
                    came_from[neighbor] = current
                    frontier.append(neighbor)
        return None

    # ---------- UCS (Priority Queue ordered by cost) ----------
    def ucs_search(self, start, goal, walls, grid_size):
        if start == goal:
            return []
        heap = []
        heapq.heappush(heap, (0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}
        while heap:
            current_cost, current = heapq.heappop(heap)
            if current == goal:
                return self._reconstruct_path(came_from, start, goal)
            for neighbor in self._get_neighbors(current, grid_size, walls):
                new_cost = current_cost + 1
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    came_from[neighbor] = current
                    heapq.heappush(heap, (new_cost, neighbor))
        return None

    # ========== PRACTICAL 04 + 05: A* Search with Logic ==========
    def astar_search(self, start, goal, walls, grid_size, heuristic_type='manhattan', use_logic=False):
        """
        A* search with optional Knowledge Base logic for feasibility checking.
        """
        if start == goal:
            return []

        h_func = self.euclidean_distance if heuristic_type == 'euclidean' else self.manhattan_distance

        start_h = h_func(start, goal)
        heap = []
        heapq.heappush(heap, (start_h, 0, start, []))
        came_from = {start: None}
        cost_so_far = {start: 0}

        while heap:
            f_cost, g_cost, current, path = heapq.heappop(heap)

            if current == goal:
                return path

            if g_cost > cost_so_far.get(current, float('inf')):
                continue

            for neighbor in self._get_neighbors(current, grid_size, walls):
                # ========== PRACTICAL 05: Logic-Based Feasibility Check ==========
                if use_logic:
                    # Clear previous facts
                    self.kb.clear_facts()

                    # Simulate percepts for this cell (in a real game, we'd use actual sensor data)
                    # For demonstration, we infer facts from the grid state:
                    # - "TargetVisible" if there is food in this cell
                    # - "HasDust" if it's a special tile (we'll simulate randomly for demo)
                    # - "BloodseekerMissing" as a random threat
                    if neighbor in walls:
                        # Wall – skip physically (already handled in _get_neighbors)
                        continue

                    # Check if there's food at this neighbor (TargetVisible)
                    if neighbor in self.food_positions_cache:
                        self.kb.tell_fact('TargetVisible')

                    # Simulate "HasDust" based on cell position (e.g., certain cells)
                    # For demonstration, we'll mark every third cell as dusty
                    if (neighbor[0] + neighbor[1]) % 3 == 0:
                        self.kb.tell_fact('HasDust')

                    # Simulate "BloodseekerMissing" for some cells (e.g., random threat)
                    if (neighbor[0] * neighbor[1]) % 2 == 0:
                        self.kb.tell_fact('BloodseekerMissing')

                    # Run Forward Chaining
                    self.kb.forward_chain()

                    # If 'Retreat' is deduced, this tile is INFEASTIBLE → skip it
                    if 'Retreat' in self.kb.facts:
                        continue  # Skip this neighbor (logic says it's unsafe)

                # If we reach here, the tile is PHYSICALLY REACHABLE and LOGICALLY FEASIBLE
                new_g = g_cost + 1
                if neighbor not in cost_so_far or new_g < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_g
                    came_from[neighbor] = current
                    h = h_func(neighbor, goal)
                    f = new_g + h
                    dx = neighbor[0] - current[0]
                    dy = neighbor[1] - current[1]
                    if dx == 1:
                        action = 'Right'
                    elif dx == -1:
                        action = 'Left'
                    elif dy == 1:
                        action = 'Up'
                    elif dy == -1:
                        action = 'Down'
                    new_path = path + [action]
                    heapq.heappush(heap, (f, new_g, neighbor, new_path))

        return None

    # ---------- Sense and Act (Main Loop) ----------
    def sense_and_act(self, percept: dict) -> str:
        if not self.plan:
            agent_pos = tuple(percept['agent_pos'])
            grid_size = percept['grid_size']
            walls = set(percept['walls'])
            foods = percept['all_food']

            # Cache food positions for logic checks
            self.food_positions_cache = set(foods)

            if not foods:
                return 'MoveForward'

            closest_food = min(foods, key=lambda f: abs(f[0] - agent_pos[0]) + abs(f[1] - agent_pos[1]))

            # Select algorithm
            if self.active_algo == 'BFS':
                plan = self.bfs_search(agent_pos, closest_food, walls, grid_size)
            elif self.active_algo == 'DFS':
                plan = self.dfs_search(agent_pos, closest_food, walls, grid_size)
            elif self.active_algo == 'UCS':
                plan = self.ucs_search(agent_pos, closest_food, walls, grid_size)
            elif self.active_algo == 'AStar':
                plan = self.astar_search(agent_pos, closest_food, walls, grid_size, heuristic_type='manhattan', use_logic=False)
            elif self.active_algo == 'AStarLogic':
                plan = self.astar_search(agent_pos, closest_food, walls, grid_size, heuristic_type='manhattan', use_logic=True)
            else:
                plan = self.bfs_search(agent_pos, closest_food, walls, grid_size)

            if plan is None:
                return 'MoveForward'
            self.plan = plan

        return self.plan.pop(0)


# ========== Original Agent ==========
class GreedyGridAgent:
    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        return random.choice(self.actions_pool)


# ========== TESTING CHECKPOINT (Practical 04, Step 1.1) ==========
if __name__ == "__main__":
    agent = SearchAgent()
    start = (0, 0)
    goal = (3, 4)
    manhattan = agent.manhattan_distance(start, goal)
    euclidean = agent.euclidean_distance(start, goal)
    print(f"Start: {start}, Goal: {goal}")
    print(f"Manhattan Distance: {manhattan} (Expected: 7)")
    print(f"Euclidean Distance: {euclidean} (Expected: 5.0)")