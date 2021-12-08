# Jesse Coyle
# CS 441/541 Portland State University
# 21 Nov 2021
from game_state import GameState
from blackjack import blackjack_train_agent, blackjack_test_agent

if __name__ == "__main__":
    # Initialize a new game state with 1 deck, and 2 players
    state = GameState(1, 2)
    trials = 10000
    agent = blackjack_train_agent(state, trials, 0.1, 0.2, 0.9, False);
    blackjack_test_agent(state, agent, trials, False);
