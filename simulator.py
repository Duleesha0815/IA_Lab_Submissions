# simulator.py
from visual_grid_game import VisualGridHuntGame
from agent import SimpleReflexAgent, ModelBasedAgent, SearchAgent


def run_simple_reflex():
    env = VisualGridHuntGame(width=8, height=8, num_food=5, num_opponents=0)
    agent = SimpleReflexAgent()
    print("\n=== SIMPLE REFLEX AGENT (Practical 02) ===")
    while not env.is_done():
        percept = env.get_percept()
        action = agent.sense_and_act(percept)
        env.execute_action(action)
        print(f"Action: {action} | Score: {env.score}")
    print(f"Final Score: {env.score} after {env.steps} steps.\n")


def run_model_based():
    env = VisualGridHuntGame(width=8, height=8, num_food=5, num_opponents=0)
    agent = ModelBasedAgent()
    print("\n=== MODEL-BASED AGENT (Practical 02) ===")
    while not env.is_done():
        percept = env.get_percept()
        action = agent.sense_and_act(percept)
        env.execute_action(action)
        print(f"Action: {action} | Score: {env.score}")
    print(f"Final Score: {env.score} after {env.steps} steps.\n")


def run_search_agent(algo='BFS'):
    env = VisualGridHuntGame(width=8, height=8, num_food=5, num_opponents=0)
    agent = SearchAgent(algo=algo)
    print(f"\n=== SEARCH AGENT ({algo}) - Practical 03/04/05 ===")
    while not env.is_done():
        percept = env.get_percept()
        action = agent.sense_and_act(percept)
        env.execute_action(action)
        print(f"Action: {action} | Score: {env.score} | Plan remaining: {len(agent.plan)}")
    print(f"Final Score: {env.score} after {env.steps} steps.\n")


if __name__ == "__main__":
    # Practical 05: Test Logic-Enhanced A*
    run_search_agent('AStarLogic')

    # Uncomment others as needed:
    # run_search_agent('BFS')
    # run_search_agent('DFS')
    # run_search_agent('UCS')
    # run_search_agent('AStar')