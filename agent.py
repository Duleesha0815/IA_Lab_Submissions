# agent.py
import random
import math
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


# ========== PRACTICAL 03 + 04: Search Agent (Goal-Based Planning with A*) ==========
class SearchAgent:
    def __init__(self, algo='BFS'):
        self.active_algo = algo   # 'BFS', 'DFS', 'UCS', or 'AStar'
        self.plan = []            # Sequence of absolute actions: ['Up', 'Down', 'Left', 'Right']

    # ========== PRACTICAL 04: Heuristic Functions ==========
    def manhattan_distance(self, pos, goal):
        """Calculates Manhattan distance: |x1-x2| + |y1-y2|"""
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    def euclidean_distance(self, pos, goal):
        """Calculates Euclidean distance: sqrt((x1-x2)^2 + (y1-y2)^2)"""
        return math.sqrt((pos[0] - goal[0]) ** 2 + (pos[1] - goal[1]) ** 2)

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

    # ========== PRACTICAL 04: A* Search ==========
    def astar_search(self, start, goal, walls, grid_size, heuristic_type='manhattan'):
        """A* search using Manhattan or Euclidean heuristic."""
        if start == goal:
            return []

        # Choose heuristic function
        if heuristic_type == 'euclidean':
            h_func = self.euclidean_distance
        else:  # default to Manhattan
            h_func = self.manhattan_distance

        # Priority queue: (f_cost, g_cost, current_pos, path_actions)
        # For the start node: g=0, h=heuristic(start, goal)
        start_h = h_func(start, goal)
        heap = []
        heapq.heappush(heap, (start_h, 0, start, []))  # (f, g, pos, path)

        came_from = {start: None}
        cost_so_far = {start: 0}

        while heap:
            f_cost, g_cost, current, path = heapq.heappop(heap)

            # If we reached the goal, return the path
            if current == goal:
                return path

            # Skip if we already found a better path to this node
            if g_cost > cost_so_far.get(current, float('inf')):
                continue

            # Expand neighbors
            for neighbor in self._get_neighbors(current, grid_size, walls):
                new_g = g_cost + 1
                # If this is a better path to neighbor
                if neighbor not in cost_so_far or new_g < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_g
                    came_from[neighbor] = current
                    # Calculate heuristic for neighbor
                    h = h_func(neighbor, goal)
                    f = new_g + h
                    # Build the new path (actions to reach neighbor)
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

        return None  # No path found

    # ---------- Sense and Act (Main Loop for Search Agent) ----------
    def sense_and_act(self, percept: dict) -> str:
        # If no plan, compute a new one
        if not self.plan:
            agent_pos = tuple(percept['agent_pos'])
            grid_size = percept['grid_size']
            walls = set(percept['walls'])
            foods = percept['all_food']

            if not foods:
                return 'MoveForward'

            # Find closest food using Manhattan distance
            closest_food = min(foods, key=lambda f: abs(f[0] - agent_pos[0]) + abs(f[1] - agent_pos[1]))

            # Run the selected search algorithm
            if self.active_algo == 'BFS':
                plan = self.bfs_search(agent_pos, closest_food, walls, grid_size)
            elif self.active_algo == 'DFS':
                plan = self.dfs_search(agent_pos, closest_food, walls, grid_size)
            elif self.active_algo == 'UCS':
                plan = self.ucs_search(agent_pos, closest_food, walls, grid_size)
            # ========== PRACTICAL 04: A* integration ==========
            elif self.active_algo == 'AStar':
                plan = self.astar_search(agent_pos, closest_food, walls, grid_size, heuristic_type='manhattan')
            else:
                plan = self.bfs_search(agent_pos, closest_food, walls, grid_size)

            if plan is None:
                return 'MoveForward'
            self.plan = plan

        # Pop the next absolute action and execute it
        return self.plan.pop(0)


# ========== Original Agent (kept for reference) ==========
class GreedyGridAgent:
    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        return random.choice(self.actions_pool)


# ========== TESTING CHECKPOINT (Practical 04, Step 1.1) ==========
if __name__ == "__main__":
    # Test heuristic functions
    agent = SearchAgent()
    start = (0, 0)
    goal = (3, 4)

    manhattan = agent.manhattan_distance(start, goal)
    euclidean = agent.euclidean_distance(start, goal)

    print(f"Start: {start}, Goal: {goal}")
    print(f"Manhattan Distance: {manhattan} (Expected: 7)")
    print(f"Euclidean Distance: {euclidean} (Expected: 5.0)")