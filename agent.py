# agent.py
import random  # Fixed the missing import!


# ========== PRACTICAL 02: Simple Reflex Agent (No memory) ==========
class SimpleReflexAgent:
    """A pure reflex agent using only IF-THEN rules. No internal state."""
    
    def sense_and_act(self, percept: dict) -> str:
        # Condition-Action Rules
        if percept['food_here']:
            return 'MoveForward'   # Move forward to eat it
        if percept['wall_ahead']:
            return 'TurnLeft'      # Turn left to avoid wall
        return 'MoveForward'       # Default: move forward


# ========== PRACTICAL 02: Model-Based Agent (With internal memory) ==========
class ModelBasedAgent:
    """A model-based agent that maintains internal state to escape loops."""
    
    def __init__(self):
        self.visited_states = set()   # Memory of percepts encountered
        self.last_action = None       # Memory of the previous action

    def sense_and_act(self, percept: dict) -> str:
        # Build a key for the current percept (used to detect loops)
        state_key = (percept['wall_ahead'], percept['food_here'])
        
        # If we've seen this exact percept before AND we just turned left,
        # then we are likely in a loop – try turning right instead.
        if state_key in self.visited_states and self.last_action == 'TurnLeft':
            self.last_action = 'TurnRight'
            return 'TurnRight'
        
        # Remember this percept for the future
        self.visited_states.add(state_key)
        
        # Standard condition-action rules
        if percept['food_here']:
            action = 'MoveForward'
        elif percept['wall_ahead']:
            action = 'TurnLeft'
        else:
            action = 'MoveForward'
        
        self.last_action = action
        return action


# ========== Original agent (kept for reference) ==========
class GreedyGridAgent:
    """Original agent – not used in Practical 02, but kept for compatibility."""
    
    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        # This agent expects the OLD percept format.
        # Since we changed it in Practical 02, this will break if used.
        return random.choice(self.actions_pool)