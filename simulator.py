# simulator.py
from visual_grid_game import VisualGridHuntGame
from agent import SearchAgent

def run_search_agent(algo='AStarLogic'):
    env = VisualGridHuntGame(width=8, height=8, num_food=5, num_opponents=0)
    agent = SearchAgent(algo=algo)
    print(f"\n=== SEARCH AGENT ({algo}) ===")
    while not env.is_done():
        percept = env.get_percept()
        action = agent.sense_and_act(percept)
        env.execute_action(action)
        print(f"Action: {action} | Score: {env.score} | Steps: {env.steps} | Plan: {len(agent.plan)}")
    print(f"Final Score: {env.score} after {env.steps} steps.\n")

if __name__ == "__main__":
    run_search_agent('AStarLogic')