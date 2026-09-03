# visual_grid_game.py
import random
import tkinter as tk


class VisualGridHuntGame:
    """Fully observable grid environment with toxic traps, opponents, and food."""

    def __init__(self, width=10, height=10, num_food=10, num_opponents=2, custom_walls=None):
        self.width = width
        self.height = height
        self.agent_pos = [0, 0]

        # Walls
        if custom_walls is not None:
            self.walls = set(custom_walls)
        else:
            self.walls = {(2, 2), (2, 3), (5, 5), (6, 5), (3, 7)}

        # Food
        self.food_positions = set()
        while len(self.food_positions) < num_food:
            fx = random.randint(0, self.width - 1)
            fy = random.randint(0, self.height - 1)
            pos = (fx, fy)
            if pos != (0, 0) and pos not in self.walls:
                self.food_positions.add(pos)

        # Opponents
        self.opponents = []
        while len(self.opponents) < num_opponents:
            ox = random.randint(0, self.width - 1)
            oy = random.randint(0, self.height - 1)
            op = [ox, oy]
            if tuple(op) != (0, 0) and tuple(op) not in self.walls and tuple(op) not in self.food_positions:
                self.opponents.append(op)

        # Toxic traps (Practical 01)
        self.toxic_traps = set()
        num_traps = max(2, num_food // 4)
        while len(self.toxic_traps) < num_traps:
            tx = random.randint(0, self.width - 1)
            ty = random.randint(0, self.height - 1)
            pos = (tx, ty)
            if pos != (0, 0) and pos not in self.walls and pos not in self.food_positions:
                self.toxic_traps.add(pos)

        self.score = 0
        self.steps = 0
        self.collision = False

    def get_percept(self) -> dict:
        """Return a dictionary with all necessary information for the agent."""
        return {
            'agent_pos': list(self.agent_pos),
            'food_positions': list(self.food_positions),
            'walls': list(self.walls),
            'width': self.width,
            'height': self.height,
            'opponent_positions': [list(op) for op in self.opponents],
            'remaining_food': len(self.food_positions),
            'score': self.score,
            'collision': self.collision,
            'toxic_traps': list(self.toxic_traps)   # Needed for logic
        }

    def execute_action(self, action: str):
        """Execute a movement action. Only absolute directions are expected."""
        self.steps += 1
        new_pos = list(self.agent_pos)

        if action == 'Up':
            new_pos[1] = min(self.height - 1, new_pos[1] + 1)
        elif action == 'Down':
            new_pos[1] = max(0, new_pos[1] - 1)
        elif action == 'Left':
            new_pos[0] = max(0, new_pos[0] - 1)
        elif action == 'Right':
            new_pos[0] = min(self.width - 1, new_pos[0] + 1)
        elif action == 'Stay' or action == 'MoveForward':
            # 'Stay' is a safe no-op; 'MoveForward' kept for compatibility but ignored
            return
        else:
            return   # unknown action

        # Wall collision
        if tuple(new_pos) in self.walls:
            self.score -= 5
            # Agent does not move
        else:
            self.agent_pos = new_pos

            tuple_pos = tuple(self.agent_pos)

            # Eat food
            if tuple_pos in self.food_positions:
                self.food_positions.remove(tuple_pos)
                self.score += 20

            # Toxic trap penalty
            if tuple_pos in self.toxic_traps:
                self.score -= 15

        # Opponent movement (random)
        for op in self.opponents:
            move = random.choice(['Up', 'Down', 'Left', 'Right', 'Stay'])
            if move == 'Up' and op[1] < self.height - 1:
                op[1] += 1
            elif move == 'Down' and op[1] > 0:
                op[1] -= 1
            elif move == 'Left' and op[0] > 0:
                op[0] -= 1
            elif move == 'Right' and op[0] < self.width - 1:
                op[0] += 1

            # Check collision with opponent
            if op == self.agent_pos:
                self.score -= 50
                self.collision = True

    def is_done(self) -> bool:
        return len(self.food_positions) == 0 or self.steps >= 60 or self.collision


class GridGameGUI:
    """Tkinter GUI that uses a SearchAgent (with logic) to play the game."""

    def __init__(self, root, agent, width=10, height=10, num_food=12, num_opponents=2, walls=None):
        self.root = root
        self.root.title("IT3012 - A* Search Agent with Logic")

        self.env = VisualGridHuntGame(width=width, height=height,
                                      num_food=num_food, num_opponents=num_opponents,
                                      custom_walls=walls)
        self.agent = agent

        # Determine cell size to fit canvas in a 600x600 window
        max_canvas_dim = 600
        self.cell_size = max(20, min(max_canvas_dim // self.env.width,
                                     max_canvas_dim // self.env.height))

        canvas_w = self.env.width * self.cell_size
        canvas_h = self.env.height * self.cell_size

        self.canvas = tk.Canvas(root, width=canvas_w, height=canvas_h, bg="white")
        self.canvas.pack()

        self.label = tk.Label(root, text="Score: 0 | Steps: 0", font=("Arial", 14))
        self.label.pack(pady=10)

        self.btn = tk.Button(root, text="Start Simulation", command=self.run_loop,
                             font=("Arial", 12), bg="#000066", fg="white")
        self.btn.pack(pady=5)

        self.draw_grid()

    def draw_grid(self):
        """Redraw the entire grid, including all objects."""
        self.canvas.delete("all")

        # Draw cells and walls
        for x in range(self.env.width):
            for y in range(self.env.height):
                x1 = x * self.cell_size
                y1 = (self.env.height - 1 - y) * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                color = "#f1f5f9" if (x, y) not in self.env.walls else "#64748b"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#cbd5e1")

                if self.cell_size >= 40 and (x, y) in self.env.walls:
                    self.canvas.create_text(x1 + self.cell_size/2, y1 + self.cell_size/2,
                                            text="W", fill="white", font=("Arial", 8, "bold"))

        # Draw food (yellow circles)
        for fx, fy in self.env.food_positions:
            off = self.cell_size * 0.25
            x1 = fx * self.cell_size + off
            y1 = (self.env.height - 1 - fy) * self.cell_size + off
            self.canvas.create_oval(x1, y1, x1 + self.cell_size*0.5, y1 + self.cell_size*0.5,
                                    fill="#f59e0b", outline="#d97706")

        # Draw opponents (red squares)
        for ox, oy in self.env.opponents:
            off = self.cell_size * 0.2
            x1 = ox * self.cell_size + off
            y1 = (self.env.height - 1 - oy) * self.cell_size + off
            self.canvas.create_rectangle(x1, y1, x1 + self.cell_size*0.6, y1 + self.cell_size*0.6,
                                         fill="#990000", outline="#7a0000")

        # Draw toxic traps (purple diamonds)
        for tx, ty in self.env.toxic_traps:
            off = self.cell_size * 0.2
            x1 = tx * self.cell_size + off
            y1 = (self.env.height - 1 - ty) * self.cell_size + off
            self.canvas.create_polygon(
                x1 + self.cell_size*0.3, y1,
                x1 + self.cell_size*0.6, y1 + self.cell_size*0.3,
                x1 + self.cell_size*0.6, y1 + self.cell_size*0.6,
                x1 + self.cell_size*0.3, y1 + self.cell_size*0.8,
                x1, y1 + self.cell_size*0.6,
                x1, y1 + self.cell_size*0.3,
                fill="#6b21a8", outline="#4c1d95")

        # Draw the agent (blue circle)
        ax, ay = self.env.agent_pos
        off = self.cell_size * 0.15
        x1 = ax * self.cell_size + off
        y1 = (self.env.height - 1 - ay) * self.cell_size + off
        self.canvas.create_oval(x1, y1, x1 + self.cell_size*0.7, y1 + self.cell_size*0.7,
                                fill="#000066", outline="#1e3a8a")

    def run_loop(self):
        """Start the simulation loop."""
        self.btn.config(state="disabled")

        def step():
            if not self.env.is_done():
                percept = self.env.get_percept()
                action = self.agent.sense_and_act(percept)
                self.env.execute_action(action)

                self.draw_grid()
                plan_left = len(self.agent.plan) if hasattr(self.agent, 'plan') else 0
                self.label.config(
                    text=f"Score: {self.env.score} | Steps: {self.env.steps} | "
                         f"Action: {action} | Plan: {plan_left}"
                )
                self.root.after(250, step)
            else:
                end_text = f"Collision! Final Score: {self.env.score}" if self.env.collision else \
                           f"Finished! Final Score: {self.env.score}"
                self.label.config(text=end_text)
                self.btn.config(state="normal")

        step()


if __name__ == "__main__":
    from agent import SearchAgent

    root = tk.Tk()
    # Use A* with logic (this will avoid toxic traps and opponents)
    agent = SearchAgent(algo='AStarLogic')
    app = GridGameGUI(root, agent, width=12, height=12, num_food=15, num_opponents=0)
    root.mainloop()