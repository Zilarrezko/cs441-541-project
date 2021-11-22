from random import randint
from game_state import Game_State, shuffle, draw, card_value

class BlackjackAction:
	hit   = 0;
	stand = 1;
	count = 2;

class BlackjackStrategy:
	random = 0;
	a = 1;
	reinforced_learning = 2;
	count = 3;

def blackjack_init(state: Game_State):
	shuffle(state);
	for i in range(state.player_count*2):
		draw(state, i%state.player_count);

def blackjack_end(state: Game_State):
	for i in range(state.player_count):
		length = len(state.players[i]);
		for j in range(length):
			v = state.players[i].pop;
			state.deck.append(v);

def blackjack_hand_value(hand: [int], start: int = 0) -> int:
	result = 0;
	one = 0;
	eleven = 0;
	for i in range(start, len(hand)):
		val = min(card_value(hand[i]), 10);
		if val == 1: # ace
			one += 1;
			eleven += 11;
		else:
			one += val;
			eleven += val;
	if eleven > 21:
		result = one;
	else:
		result = eleven;
	return result;

def play_blackjack(state: Game_State, strategy: int, printing: bool):
	blackjack_init(state);
	state.dealer = 0;
	for i in range(state.player_count):
		if i == state.dealer: continue;
		cur_player = i;
		action = get_blackjack_action(state, cur_player, strategy);
		while blackjack_hand_value(state.players[cur_player]) < 21 and action != BlackjackAction.stand:
			draw(state, cur_player);
			action = get_blackjack_action(state, cur_player, strategy);
		if printing: print("Player", cur_player, ":", blackjack_hand_value(state.players[cur_player]));
	while blackjack_hand_value(state.players[state.dealer]) < 17:
		draw(state, state.dealer);
	if printing:
		print("Dealer", 0, ":", blackjack_hand_value(state.players[state.dealer]));
		print("");
	blackjack_assess_players(state, printing);
	blackjack_end(state);

def blackjack_assess_players(state: Game_State, printing: bool = True):
	dealer_value = blackjack_hand_value(state.players[state.dealer]);
	for i in range(state.player_count):
		if i == state.dealer: continue;
		player_value = blackjack_hand_value(state.players[i]);
		if player_value > 21:
			if printing: print("player", i, ":", player_value, "broke!");
		elif dealer_value > 21:
			if printing: print("player", i, ":", player_value, "won!");
			state.win_count += 1;
		elif player_value > dealer_value:
			if printing: print("player", i, ":", player_value, "won!");
			state.win_count += 1;
		elif player_value == dealer_value:
			if printing: print("player", i, ":", player_value, "push");
		else:
			if printing: print("player", i, ":", player_value, "lost");

def get_blackjack_action(state: Game_State, cur_player: int, strategy: int) -> BlackjackAction:
	if strategy == BlackjackStrategy.random:	
		return randint(0, BlackjackAction.count - 1);
	elif strategy == BlackjackStrategy.a:
		val = blackjack_hand_value(state.players[cur_player]);
		if val < 17:
			return BlackjackAction.hit;
		else:
			return BlackjackAction.stand;
	#elif strategy == BlackjackStrategy.reinforced_learning:
		# Todo(jesse): We need to fill this out, as well as a second one
	else:
		return 0;
