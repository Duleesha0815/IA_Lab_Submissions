# agent.py
import random
import math
from collections import deque
import heapq
from logic_engine import KnowledgeBase


# ===== Practical 02: Simple Reflex =====
class SimpleReflexAgent:
    def sense_and_act(self, percept: dict) -> str:
        if percept.get('food_here', False):
            return 'MoveForward'
        if percept.get('wall_ahead', False):
            return 'TurnLeft'
        return 'MoveForward'


# ===== Practical 02: Model‑Based =====
class ModelBasedAgent:
    def __init__(self):
        self.visited_states = set()
        self.last_action = None
        self.position = (0, 0)

    def sense_and_act(self, percept: dict) -> str:
        self.visited_states.add(self.position)
        if percept.get('food_here', False):
            action = 'MoveForward'
        elif percept.get('wall_ahead', False):
            if self.position in self.visited_states and self.last_action == 'TurnLeft':
                action = 'TurnRight'
            else:
                action = 'TurnLeft'
        else:
            state_key = (percept.get('wall_ahead', False), percept.get('food_here', False))
            if state_key in self.visited_states:
                action = 'TurnRight'
            else:
                action = 'MoveForward'
        self.last_action = action
        return action


# ===== Practical 03 + 04 + 05: Search Agent with Logic =====
class SearchAgent:
    def __init__(self, algo='AStarLogic'):
        self.active_algo = algo
        self.plan = []
        self.food_cache = set()
        self.opponents_cache = []
        self.toxic_traps_cache = set()

        # Knowledge Base & Rules (Practical 05)
        self.kb = KnowledgeBase()
        self.kb.tell_rule(['TargetVisible', 'HasDust'], 'SafeToEngage')
        self.kb.tell_rule(['SafeToEngage', 'BloodseekerMissing'], 'Retreat')
        # NEW RULE: Directly avoid toxic traps
        self.kb.tell_rule(['ToxicTrapAhead'], 'Retreat')

    # ---------- Heuristics ----------
    def manhattan_distance(self, pos, goal):
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    def euclidean_distance(self, pos, goal):
        return math.sqrt((pos[0] - goal[0])**2 + (pos[1] - goal[1])**2)

    # ---------- Neighbors & Path reconstruction ----------
    def _get_neighbors(self, pos, grid_size, walls):
        x, y = pos
        width, height = grid_size
        neighbors = []
        if y + 1 < height and (x, y + 1) not in walls:
            neighbors.append((x, y + 1))
        if y - 1 >= 0 and (x, y - 1) not in walls:
            neighbors.append((x, y - 1))
        if x - 1 >= 0 and (x - 1, y) not in walls:
            neighbors.append((x - 1, y))
        if x + 1 < width and (x + 1, y) not in walls:
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

    # ---------- BFS / DFS / UCS ----------
    def bfs_search(self, start, goal, walls, grid_size):
        if start == goal:
            return []
        frontier = deque([start])
        came_from = {start: None}
        while frontier:
            current = frontier.popleft()
            if current == goal:
                return self._reconstruct_path(came_from, start, goal)
            for nb in self._get_neighbors(current, grid_size, walls):
                if nb not in came_from:
                    came_from[nb] = current
                    frontier.append(nb)
        return None

    def dfs_search(self, start, goal, walls, grid_size):
        if start == goal:
            return []
        frontier = [start]
        came_from = {start: None}
        while frontier:
            current = frontier.pop()
            if current == goal:
                return self._reconstruct_path(came_from, start, goal)
            for nb in self._get_neighbors(current, grid_size, walls):
                if nb not in came_from:
                    came_from[nb] = current
                    frontier.append(nb)
        return None

    def ucs_search(self, start, goal, walls, grid_size):
        if start == goal:
            return []
        heap = [(0, start)]
        came_from = {start: None}
        cost_so_far = {start: 0}
        while heap:
            cost, current = heapq.heappop(heap)
            if current == goal:
                return self._reconstruct_path(came_from, start, goal)
            for nb in self._get_neighbors(current, grid_size, walls):
                new_cost = cost + 1
                if nb not in cost_so_far or new_cost < cost_so_far[nb]:
                    cost_so_far[nb] = new_cost
                    came_from[nb] = current
                    heapq.heappush(heap, (new_cost, nb))
        return None

    # ---------- A* with logic ----------
    def astar_search(self, start, goal, walls, grid_size,
                     heuristic_type='manhattan', use_logic=False,
                     opponents=None, toxic_traps=None):
        if start == goal:
            return []

        h_func = self.euclidean_distance if heuristic_type == 'euclidean' else self.manhattan_distance
        start_h = h_func(start, goal)
        heap = [(start_h, 0, start, [])]
        came_from = {start: None}
        cost_so_far = {start: 0}

        if opponents is None:
            opponents = self.opponents_cache
        if toxic_traps is None:
            toxic_traps = self.toxic_traps_cache

        while heap:
            f, g, pos, path = heapq.heappop(heap)
            if pos == goal:
                return path

            if g > cost_so_far.get(pos, float('inf')):
                continue

            for nb in self._get_neighbors(pos, grid_size, walls):
                # ---- Logic feasibility check (Practical 05) ----
                if use_logic:
                    self.kb.clear_facts()

                    # 1) TargetVisible: food at this neighbor?
                    if nb in self.food_cache:
                        self.kb.tell_fact('TargetVisible')

                    # 2) HasDust: toxic trap at this neighbor?
                    if nb in toxic_traps:
                        self.kb.tell_fact('HasDust')
                        # Direct rule to avoid traps
                        self.kb.tell_fact('ToxicTrapAhead')

                    # 3) BloodseekerMissing: opponent at this exact neighbor?
                    if nb in opponents:
                        self.kb.tell_fact('BloodseekerMissing')

                    self.kb.forward_chain()

                    # If 'Retreat' is deduced, this tile is INFEASIBLE → skip
                    if 'Retreat' in self.kb.facts:
                        continue

                # ---- Standard A* expansion ----
                new_g = g + 1
                if nb not in cost_so_far or new_g < cost_so_far[nb]:
                    cost_so_far[nb] = new_g
                    came_from[nb] = pos
                    h = h_func(nb, goal)
                    f_new = new_g + h
                    dx = nb[0] - pos[0]
                    dy = nb[1] - pos[1]
                    if dx == 1:
                        action = 'Right'
                    elif dx == -1:
                        action = 'Left'
                    elif dy == 1:
                        action = 'Up'
                    elif dy == -1:
                        action = 'Down'
                    heapq.heappush(heap, (f_new, new_g, nb, path + [action]))

        return None

    # ---------- Main sense‑and‑act ----------
    def sense_and_act(self, percept: dict) -> str:
        # Update caches from percept
        self.food_cache = set(percept.get('food_positions', []))
        self.opponents_cache = [tuple(op) for op in percept.get('opponent_positions', [])]
        self.toxic_traps_cache = set(percept.get('toxic_traps', []))

        # If we have a plan, execute the next action
        if self.plan:
            return self.plan.pop(0)

        # Otherwise, compute a new plan
        agent_pos = tuple(percept['agent_pos'])
        grid_size = (percept['width'], percept['height'])
        walls = set(percept['walls'])
        foods = self.food_cache

        if not foods:
            return 'Stay'

        # Closest food (Manhattan)
        closest = min(foods, key=lambda f: abs(f[0]-agent_pos[0]) + abs(f[1]-agent_pos[1]))

        # Choose algorithm
        plan = None
        if self.active_algo == 'BFS':
            plan = self.bfs_search(agent_pos, closest, walls, grid_size)
        elif self.active_algo == 'DFS':
            plan = self.dfs_search(agent_pos, closest, walls, grid_size)
        elif self.active_algo == 'UCS':
            plan = self.ucs_search(agent_pos, closest, walls, grid_size)
        elif self.active_algo == 'AStar':
            plan = self.astar_search(agent_pos, closest, walls, grid_size,
                                     heuristic_type='manhattan', use_logic=False)
        elif self.active_algo == 'AStarLogic':
            plan = self.astar_search(agent_pos, closest, walls, grid_size,
                                     heuristic_type='manhattan', use_logic=True,
                                     opponents=self.opponents_cache,
                                     toxic_traps=self.toxic_traps_cache)
        else:
            plan = self.astar_search(agent_pos, closest, walls, grid_size,
                                     heuristic_type='manhattan', use_logic=True,
                                     opponents=self.opponents_cache,
                                     toxic_traps=self.toxic_traps_cache)

        if plan is None:
            return 'Stay'
        self.plan = plan
        return self.plan.pop(0)


# ===== Original Greedy Agent =====
class GreedyGridAgent:
    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        return random.choice(self.actions_pool)


# ===== Test heuristics =====
if __name__ == "__main__":
    agent = SearchAgent()
    start = (0, 0); goal = (3, 4)
    print(f"Manhattan: {agent.manhattan_distance(start, goal)} (expected 7)")
    print(f"Euclidean: {agent.euclidean_distance(start, goal)} (expected 5.0)")