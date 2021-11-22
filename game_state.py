from random import randint

class Game_State:
	deck = [];
	players = [];
	player_count = 0;
	dealer = 0;
	win_count = 0;
	# Note(jesse): Blackjack specific
	# Note(jesse): Poker Specific
	community_cards = [];
	folded_players = [];
	player_money = [];
	player_stake = [];
	pool = 0;


def init_new_game(state: Game_State, deck_count: int, player_count: int):
	card_count = deck_count*52;
	state.deck = [0]*card_count;
	for i in range(deck_count):
		v = 1;
		for j in range(card_count):
			state.deck[j] = v;
			v += 1;
	state.player_count = player_count;
	state.players.clear();
	for i in range(player_count):
		player = [];
		state.players.append(player);

def shuffle(state: Game_State):
	# Research/Note(jesse): You can not generate a permutation of any length 52
	# without at least 226 bits of state. We can't generate all possible permutations
	# of a deck of cards here... 52 factorial
	# And if we end up using multiple decks, the problem is compounded, keeping the same
	# subset length within the new bigger set of permutations
	# Python is using a 32bit state Mersenne Twister, a far cry from 226bits.
	# There's probably a library for a 256bit one, I have not looked too hard.
	# maybe it's enough. Also... Maybe we don't care
	for i in range(len(state.deck) - 1):
		pos = randint(i, len(state.deck) - 1);
		t = state.deck[pos];
		state.deck[pos] = state.deck[i];
		state.deck[i] = t;

def draw(state, player: int):
	v = state.deck.pop();
	state.players[player].append(v);

def card_suit(card: int) -> int:
	return (card - 1)//13;

def card_value(card: int) -> int:
	return (card - 1)%13 + 1;

def card_print(cards: [int]) -> str:
	result: str = "";
	for i in cards:
		val = card_value(i);
		if   val == 1:  result += "A";
		elif val == 11: result += "J";
		elif val == 12: result += "Q";
		elif val == 13: result += "K";
		else:           result += str(val);
		suit = card_suit(i);
		if suit == 0: result += "♦";
		if suit == 1: result += "♣";
		if suit == 2: result += "♥";
		if suit == 3: result += "♠";
		result += " ";
	return result;
