from random import randint, random
from card import Card
from game_state import GameState
from player import Player

class BlackjackAction:
	hit   = 0;
	stand = 1;
	count = 2;

def blackjack_init(state: GameState):
	state.dealer = 0;
	state.shuffle_deck();
	for i in range(state.player_count*2):
		state.draw_card(i%state.player_count);

def blackjack_end(state: GameState):
	for i in range(state.player_count):
		length = len(state.players[i].hand);
		for j in range(length):
			v = state.players[i].hand.pop();
			state.deck.append(v);

def blackjack_hand_value(player: Player, start: int = 0) -> int:
	result = 0;
	one = 0;
	eleven = 0;
	for i in range(start, len(player.hand)):
		val = min(player.hand[i].value, 10);
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

class Agent:
	q: [float];

######### Q-Learning ############################

# Note(jesse): Creating an index into the q-table
#   0-9   are reserved for the dealer's up card
#  00-270 are reserved for the player's hand values
#  range is 0-279 for state
#  so first radix is used for dealer card offset into the q table
#  while the second and third radix is taken for the player's hand value
#  -4 is from the lowest hand value a player can have to make the q-table smaller
#  Note: I'm also assuming we are checking if we've busted outside of this procedure
def blackjack_get_state(game_state, player):
	result = 0;
	dealer_card = min(game_state.players[game_state.dealer].hand[1].value, 10);
	result = dealer_card - 1;
	result += 10*(blackjack_hand_value(game_state.players[player]) - 4);
	return result;

def blackjack_get_max_action(agent, state):
	result = 0;
	# Note(jesse): I'm being general here, really we just need to return
	#              the max between index state and index state + 1 (for the two actions in blackjack)
	#         e.g. result = 0 if agent.q[state] < agent.q[state + 1] else 1;
	for i in range(1, BlackjackAction.count):
		if agent.q[state*2 + result] < agent.q[state*2 + i]:
			result = i;
	return result;

REWARD_LOSE = -1;
REWARD_BUST = -5;
REWARD_WIN  = 1;
REWARD_PUSH = 0;
REWARD_TAX  = 0;
def blackjack_take_action(game_state, action):
	reward = 0;
	if action == BlackjackAction.hit:
		game_state.draw_card(1);
		if blackjack_hand_value(game_state.players[1]) > 21:
			reward = REWARD_BUST;
		else:
			reward = 0;
	elif action == BlackjackAction.stand:
		dealer_value = blackjack_hand_value(game_state.players[0]);
		while dealer_value < 17:
			game_state.draw_card(0);
			dealer_value = blackjack_hand_value(game_state.players[0]);
		player_value = blackjack_hand_value(game_state.players[1]);
		if dealer_value < player_value or dealer_value > 21:
			reward = REWARD_WIN;
			game_state.inc_win();
		elif dealer_value > player_value:
			reward = REWARD_LOSE;
			game_state.inc_loss();
		elif dealer_value == player_value:
			reward = REWARD_PUSH;
			game_state.inc_draw();
	return reward + REWARD_TAX;

action_string = ["hit", "stand"];

def blackjack_train_agent(game_state, episodes, epsilon, eta, gamma, printing):
	print("Training:");
	game_state.reset();
	agent = Agent();
	# Note(jesse): 27 if from the -4, since a player's lowest hand value is 4 and highest
	#              is 31 (having 21 and hitting, will result in maximum 31)
	#              31 - 4 = 27...
	agent.q = [0]*((10 + 10*27)*BlackjackAction.count);
	e = epsilon;
	de = epsilon/(episodes/50);
	reward_total = 0;
	data = [];
	for episode in range(episodes):
		blackjack_init(game_state);
		while True:
			state = blackjack_get_state(game_state, 1);
			action = 0;
			if random() >= e:
				action = blackjack_get_max_action(agent, state);
			else:
				action = randint(0, BlackjackAction.count - 1);
			reward = blackjack_take_action(game_state, action);
			reward_total += reward;
			q_index = state*2 + action;
			state_prime = blackjack_get_state(game_state, 1);
			max_action_prime = blackjack_get_max_action(agent, state_prime);
			q_index_prime = state_prime*2 + max_action_prime;
			agent.q[q_index] = agent.q[q_index] + eta*(reward + gamma*agent.q[q_index_prime] - agent.q[q_index]);

            # Log data
            data.append({
                'num_trials': episodes,
                'epsilon': epsilon,
                'eta': eta,
                'gamma': gamma,
                'trial': episode,
                'reward': reward_total/(episode + 1),
                'winrate': game_state.win_count/(episode + 1)*100
            })
			if blackjack_hand_value(game_state.players[1]) > 21 or action == BlackjackAction.stand:
				break;
		if episode > 0 and episode%50 == 0:
			e -= de;
			# e += -e*0.06 # Note(jesse): Hard coded for now, will do linear recurrence later
		blackjack_end(game_state);

	print("wins:", game_state.win_count);
	print("winrate:", game_state.win_count/episodes*100);
    '''
	f = open("training.csv", "w");
	string = "";
	for i in range(0, len(data) - 1, 2):
		string += str(data[i]);
		string += ",";
		string += str(data[i + 1]);
		string += "\n";
	f.write(string);
    '''
	return agent, data;

def blackjack_test_agent(game_state, agent, episodes, printing):
	print("Testing:");
	game_state.reset();
	reward_total = 0;
	data = [];
	for episode in range(episodes):
		blackjack_init(game_state);
		while True:
			state = blackjack_get_state(game_state, 1);
			action = blackjack_get_max_action(agent, state);
			reward = blackjack_take_action(game_state, action);
			reward_total += reward;
			if blackjack_hand_value(game_state.players[1]) > 21 or action == BlackjackAction.stand:
				break;
		data.append(reward_total/(episode + 1)); # reward
		data.append(game_state.win_count/(episode + 1)*100); # winrate
		blackjack_end(game_state);
	print("wins:", game_state.win_count);
	print("winrate:", game_state.win_count/episodes*100);
	f = open("test.csv", "w");
	string = "";
	for i in range(0, len(data) - 1, 2):
		string += str(data[i]);
		string += ",";
		string += str(data[i + 1]);
		string += "\n";
	f.write(string);
