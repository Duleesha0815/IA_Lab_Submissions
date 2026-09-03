# agent.py
import random
from collections import deque
import heapq


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


# ========== PRACTICAL 03: Search Agent (Goal-Based Planning) ==========
class SearchAgent:
    def __init__(self, algo='BFS'):
        self.active_algo = algo   # 'BFS', 'DFS', or 'UCS'
        self.plan = []            # Sequence of absolute actions: ['Up', 'Down', 'Left', 'Right']

    def _get_neighbors(self, pos, grid_size, walls):
        """Returns valid neighboring absolute coordinates."""
        x, y = pos
        neighbors = []
        # Up
        if y + 1 < grid_size[1] and (x, y + 1) not in walls:
            neighbors.append((x, y + 1))
        # Down
        if y - 1 >= 0 and (x, y - 1) not in walls:
            neighbors.append((x, y - 1))
        # Left
        if x - 1 >= 0 and (x - 1, y) not in walls:
            neighbors.append((x - 1, y))
        # Right
        if x + 1 < grid_size[0] and (x + 1, y) not in walls:
            neighbors.append((x + 1, y))
        return neighbors

    def _reconstruct_path(self, came_from, start, goal):
        """Reconstruct the action sequence from start to goal."""
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
        return None  # No path found

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
        # Priority queue stores (cost, node)
        heap = []
        heapq.heappush(heap, (0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}
        while heap:
            current_cost, current = heapq.heappop(heap)
            if current == goal:
                return self._reconstruct_path(came_from, start, goal)
            for neighbor in self._get_neighbors(current, grid_size, walls):
                new_cost = current_cost + 1  # Each move costs 1
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    came_from[neighbor] = current
                    heapq.heappush(heap, (new_cost, neighbor))
        return None

    # ---------- Sense and Act (Main Loop for Search Agent) ----------
    def sense_and_act(self, percept: dict) -> str:
        # If no plan, compute a new one
        if not self.plan:
            agent_pos = tuple(percept['agent_pos'])
            grid_size = percept['grid_size']
            walls = set(percept['walls'])
            foods = percept['all_food']

            if not foods:
                return 'MoveForward'  # No food left, just idle

            # Find closest food using Manhattan distance
            closest_food = min(foods, key=lambda f: abs(f[0] - agent_pos[0]) + abs(f[1] - agent_pos[1]))

            # Run the selected search algorithm
            if self.active_algo == 'BFS':
                plan = self.bfs_search(agent_pos, closest_food, walls, grid_size)
            elif self.active_algo == 'DFS':
                plan = self.dfs_search(agent_pos, closest_food, walls, grid_size)
            elif self.active_algo == 'UCS':
                plan = self.ucs_search(agent_pos, closest_food, walls, grid_size)
            else:
                plan = self.bfs_search(agent_pos, closest_food, walls, grid_size)

            if plan is None:
                return 'MoveForward'  # No path found
            self.plan = plan

        # Pop the next absolute action and execute it
        return self.plan.pop(0)


# ========== Original Agent (kept for reference) ==========
class GreedyGridAgent:
    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        return random.choice(self.actions_pool)