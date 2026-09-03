# simulator.py
from visual_grid_game import VisualGridHuntGame
from agent import SimpleReflexAgent, ModelBasedAgent


def run_simple_reflex():
    """Run the environment with the Simple Reflex Agent."""
    env = VisualGridHuntGame(width=8, height=8, num_food=5, num_opponents=0)
    agent = SimpleReflexAgent()
    
    print("\n=== RUNNING SIMPLE REFLEX AGENT (Will get stuck) ===")
    while not env.is_done():
        percept = env.get_percept()
        action = agent.sense_and_act(percept)
        env.execute_action(action)
        print(f"Percept: {percept} | Action: {action} | Score: {env.score}")
    
    print(f"Final Score: {env.score} after {env.steps} steps.\n")


def run_model_based():
    """Run the environment with the Model-Based Agent."""
    env = VisualGridHuntGame(width=8, height=8, num_food=5, num_opponents=0)
    agent = ModelBasedAgent()
    
    print("\n=== RUNNING MODEL-BASED AGENT (Should escape loops) ===")
    while not env.is_done():
        percept = env.get_percept()
        action = agent.sense_and_act(percept)
        env.execute_action(action)
        print(f"Percept: {percept} | Action: {action} | Score: {env.score}")
    
    print(f"Final Score: {env.score} after {env.steps} steps.\n")


if __name__ == "__main__":
    run_simple_reflex()
    run_model_based()