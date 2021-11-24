# Jesse Coyle
# CS 441/541 Portland State University
# 21 Nov 2021
from game_state import GameState
from poker import play_poker, PokerStrategy


# import cProfile
# cProfile.run('main()');

if __name__ == "__main__":
    # Initialize a new game state with 1 deck, and 2 players
    state = GameState(1, 4)
    trials = 10
    for i in range(trials):
        # play_blackjack(state, BlackjackStrategy.random, False);
        play_poker(state, PokerStrategy.random, True)
        if i % 512 == 0:
            print("\r", i, end="")
    print("\r", end="")
    # print(
    #    "Player wins:",
    #    state.win_count,
    #    "/",
    #    trials,
    #    "...",
    #    str(100.0 * state.win_count / trials) + "%",
    # )
