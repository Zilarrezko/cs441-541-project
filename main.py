# Jesse Coyle
# CS 441/541 Portland State University
# 21 Nov 2021
from game_state import Game_State, init_new_game
from poker import play_poker, PokerStrategy
from blackjack import play_blackjack, BlackjackStrategy

def main():
	state = Game_State();
	trials = 1;
	for i in range(trials):
		init_new_game(state, 1, 2);
		# play_blackjack(state, BlackjackStrategy.random, False);
		play_poker(state, PokerStrategy.random, True);
		if i%512 == 0: print("\r", i, end = "");
	print("\r", end = "");
	print("Player wins:", state.win_count, "/", trials, "...", str(100.0*state.win_count/trials) + "%");

# import cProfile
# cProfile.run('main()');

main();
