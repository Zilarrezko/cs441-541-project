from random import randint
from game_state import Game_State, shuffle, draw, card_print, card_value, card_suit

class PokerAction:
	fold = 0;
	call = 1;    # Note(jesse): includes check (nothing to add to pot)
	raising = 2; # Note(jesse): can't use "raise" because it's a keyword
	count = 3;

class PokerStrategy:
	random = 0;
	reinforced_learning = 1;
	count = 2;

def poker_init(state: Game_State):
	shuffle(state);
	state.player_money.clear();
	state.community_cards.clear();
	state.pot = 0;
	state.player_money = [100]*len(state.players);
	state.folded_players.clear();
	state.player_bet = [0]*len(state.players);
	for i in range(state.player_count*2):
		draw(state, i%state.player_count);

def poker_end(state: Game_State, winner: int):
	state.player_money[winner] += state.pot;
	for i in range(state.player_count):
		length = len(state.players[i]);
		for j in range(length):
			v = state.players[i].pop;
			state.deck.append(v);

def players_in_play(folded_players: [bool]) -> int:
	result = 0;
	for i in range(len(folded_players)):
		if folded_players[i] == False:
			result += 1;
	return result;

def play_poker(state: Game_State, strategy: int, printing: bool):
	poker_init(state);
	state.dealer = 0;
	# Todo(jesse): Big blind/small blind? Other Poker things?
	# for i in range(len(state.players)):
	# 	print("player", i, ":", card_print(state.players[i]));
	state.folded_players = [False]*len(state.players);
	highest_bet = 0;
	in_play = len(state.players);
	for turn in range(4):
		print(">> Turn", turn, "pot:", state.pot, "community:", card_print(state.community_cards));
		betting = True;
		last_raise = -1;
		while betting:
			betting = False;
			for i in range(len(state.players)):
				if in_play == 1: break;
				if i == last_raise: break;
				if state.folded_players[i] == True: continue;
				action, stake = get_poker_action(state, i, strategy);
				if action == PokerAction.fold:
					state.folded_players[i] = True;
					in_play -= 1;
				elif action == PokerAction.call:
					bet = state.player_bet[i];
					if bet < highest_bet:
						to_bet = highest_bet - bet;
						state.pot += to_bet;
						state.player_money[i] -= to_bet;
						state.player_bet[i] = highest_bet;
				elif action == PokerAction.raising:
					if stake > 0:
						betting = True;
						state.pot += stake;
						state.player_money[i] -= stake;
						state.player_bet[i] = highest_bet + stake;
						highest_bet = state.player_bet[i];
						print("new highest bet:", highest_bet);
						last_raise = i;
				if   action == PokerAction.fold:
					print("player", i, "folded");
				elif action == PokerAction.call:
					print("player", i, "called", "bet:", state.player_bet[i]);
				elif action == PokerAction.raising:
					print("player", i, "raised:", stake, "bet:", state.player_bet[i]);
		if in_play == 1: break;
		if turn == 0:
			for i in range(3):
				state.community_cards.append(state.deck.pop());
		elif turn < 3:
			state.community_cards.append(state.deck.pop());
	poker_assess_players(state, printing);

# Note(jesse):
# value:
#  1 - pair
#  2 - two pair
#  3 - three of a kind
#  4 - straight
#  5 - flush
#  6 - full house
#  7 - four of a kind
#  8 - straight flush
#  9 - royal flush
hand_value_strings = [
	"----",
	"pair",
	"two pair",
	"three of a kind",
	"straight",
	"flush",
	"full house",
	"four of a kind",
	"straight flush",
	"royal flush"
];
def poker_hand_value(state: Game_State, hand: [int]) -> (int, int):
	# Todo(Jesse): There's a lot of problems here... Lots of edge cases
	#              Even if, there's a lot of things we can't do here
	value = 0;
	highest = 0;
	suits = [0]*4;
	cards = [0]*13;
	for i in hand:
		val = card_value(i);
		highest = max(val, highest);
		if val == 1:
			highest = 14;
		suits[card_suit(i)] += 1;
		cards[val - 1] += 1;

	for i in state.community_cards:
		val = card_value(i);
		# highest = max(val, highest);
		# if val == 1:
		# 	highest = 13;
		suits[card_suit(i)] += 1;
		cards[val - 1] += 1;

	highest_suit = 0;
	for i in range(4):
		highest_suit = max(highest_suit, suits[i]);
	print("highest suit:", highest_suit);

	run = 0;
	run_end = 0;
	pair_count = three_count = four_count = 0;
	for i in range(13):
		count = cards[i];
		if   count == 2: pair_count  += 1;
		elif count == 3: three_count += 1;
		elif count == 4: four_count  += 1;
		if cards[i] > 0 and i > 0 and cards[i - 1] > 0:
			if run == 0:
				run = 2;
			else:
				run += 1;
			run_end = i;

	if pair_count == 1:
		value = 1;
	if pair_count == 2:
		value = 2;
	if three_count == 1:
		value = 3;
	if run >= 5:
		value = 4;
	if highest_suit >= 5:
		value = 5;
	if pair_count == 1 and three_count == 1:
		value = 6;
	if four_count == 1:
		value = 7;
	if highest_suit >= 5 and run >= 5:
		value = 8;
	if highest_suit >= 5 and run >= 5 and run_end == 14:
		value = 9;

	return value, highest;

# Todo(jesse): Finish this
def poker_assess_players(state: Game_State, printing: bool = True):
	best_player = 0;
	best_hand = 0;
	best_high = 0;
	for i in range(state.player_count):
		hand = state.players[i];
		player_value, high = poker_hand_value(state, hand);
		print("player", i, "with", card_print(hand), "value", player_value, "high", high, hand_value_strings[player_value]);
		if player_value > best_hand:
			best_player = i;
			best_hand = player_value;
			best_high = high;
		#elif player_value == best_hand && high > 

def get_poker_action(state: Game_State, cur_player: int, strategy: int) -> (PokerAction, int):
	if strategy == PokerStrategy.random:
		action = randint(0, PokerAction.count - 1);
		stake = 0;
		if action == PokerAction.raising:
			stake = min(randint(1, 5), state.player_money[cur_player]);
		return action, stake;
	#elif strategy == PokerStrategy.reinforced_learning:
		# Todo(jesse): We need to fill this out, as well as a second one
