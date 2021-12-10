from neural_network import NetworkState, NeuralNetwork
import numpy as np
import random
from deck import Deck
from matplotlib.pyplot import plot, savefig


def choose_action(network_state: NetworkState, E):
    if random.random() <= E:
        return np.random.choice([0, 1])

    return np.argmax(network_state.output_layer)


def dealer_sim(hand, deck: Deck):
    total_value = hand[0].value + hand[1].value
    while total_value < 16:
        total_value += deck.draw().value

    if total_value > 21:
        total_value = -1

    return total_value


#def perform_action(action, state, hand, dealer_hand, deck: Deck):
def perform_action(action, player_hand, dealer_hand, deck: Deck):
    player_value = sum(c.value for c in player_hand)
    dealer_value = sum(c.value for c in dealer_hand)

    # STAY
    if action == 0:
        dealer_value = dealer_sim(dealer_hand, deck)

        # Dealer busted
        if dealer_value == -1:
            return True, 1

        # Draw
        if player_value == dealer_value:
            return True, 0

        # Perfect hand
        if player_value == 21:
            return True, 2

        # We beat the the dealer without either of us busting
        if player_value > dealer_value and player_value <= 21:
            return True, 1
        # Lost to dealer without either of us busting
        if player_value < dealer_value:
            return True, -1
        # Busted
        if player_value > 21:
            return True, -2
    # HIT
    elif action == 1:
        player_hand.append(deck.draw())
        new_player_value = sum(c.value for c in player_hand)

        # Busted
        if new_player_value > 21:
            return True, -2

        return False, 0


def generate_input(dealer_visible_card, player_cards):
    input = [dealer_visible_card] + ([0] * 14)
    for card in player_cards:
        input[card] += 1
    return input


def update_network(network: NeuralNetwork, history, alpha, gamma) -> None:
    previous_max_Qvalue = 0
    for i in range(len(history)):
        network_state, reward = history[i][0], history[i][1]
        target = network_state.output_layer.copy()
        max_index = np.argmax(target)
        if i == 0:
            target[max_index] += alpha * reward
        else:
            target[max_index] += \
                alpha * (reward + (gamma * previous_max_Qvalue) - max(network_state.output_layer))
        previous_max_Qvalue = max(network_state.output_layer)
        network.execute_back_progagation(network_state, target)


def run_blackjack(episodes, network: NeuralNetwork, max_steps, alpha, gamma, epsilon, delta_e):
    # STAY, HIT
    rewards = []
    for ep in range(episodes):
        deck = Deck()
        deck.shuffle()
        mean_reward = 0
        c1, c2, d1, d2 = deck.deal()
        hand = [c1, c2]
        dealer_hand = [d1, d2]
        history = []
        for step in range(max_steps):

            #state = State(sum(c.value for c in hand), d1.value)
            input = generate_input(d1.value, [c.value for c in hand])
            network_state = network.execute_forward_propagation(input)

            action = choose_action(network_state, epsilon)
            is_game_over, reward = perform_action(action, hand, dealer_hand, deck)

            history.insert(0, (network_state, reward))


            #Qo = Q.get(state, [0, 0])[action]
            #Qn = np.max(Q.get(new_state, [0, 0]))

            #Q[state][action] = Qo + alpha * (reward + gamma * Qn - Qo)


            mean_reward += reward

            # This means we reached a terminal state. and Episode should end.
            if is_game_over == True:
                update_network(network, history, alpha, gamma)
                break

        if ep % 100 == 0:
            epsilon += delta_e

            # Calculate average reward thus far and plot it.
            if len(rewards) == 0:
                rewards.append(mean_reward)
            else:
                last = rewards[-1]
                mr = (mean_reward - last) / (len(rewards) + 1)
                rewards.append(last + mr)

    plot(rewards)
    savefig("graph.png")


def test_blackjack(episodes, network, max_steps, epsilon):
    wins = 0
    draws = 0
    for ep in range(episodes):
        deck = Deck()
        deck.shuffle()
        mean_reward = 0
        c1, c2, d1, d2 = deck.deal()
        hand = [c1, c2]
        dealer_hand = [d1, d2]
        for step in range(max_steps):

            input = generate_input(d1.value, [c.value for c in hand])
            network_state = network.execute_forward_propagation(input)

            action = choose_action(network_state, epsilon)
            is_game_over, reward = perform_action(action, hand, dealer_hand, deck)

            # This means we reached a terminal state. and Episode should end.
            if is_game_over == True:
                if reward > 0:
                    wins += 1
                if reward == 0:
                    draws += 1
                break

    print(f"Wins: {wins}\nDraws: {draws}")
    print(f"Win rate: {wins/episodes}")


if __name__ == "__main__":
    Q = NeuralNetwork(15, 2, 100, 2)
    E = 0
    N = 10000
    A = 0.125
    E = 0.35
    G = 0.6
    DELTA_E = (-100 * E) / (E / (0.65 * N))
    run_blackjack(N, Q, 20, A, G, E, DELTA_E)
    test_blackjack(N, Q, 20, 0)