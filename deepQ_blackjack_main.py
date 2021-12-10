import numpy as np
import math
import random
from deck import Deck
from matplotlib.pyplot import plot, savefig
from neural_network import NetworkState, NeuralNetwork


def choose_action(network_state: NetworkState, E):
    if random.random() <= E:
        return np.random.choice([0, 1])

    return np.argmax(network_state.output_layer)


def eval_hand(hand: list):
    total_value = 0
    num_aces = 0

    for card in hand:
        if card.value == 1:
            num_aces += 1
            continue
        total_value += min(card.value, 10)
    while num_aces > 0:

        if total_value + 11 > 21:
            total_value += 1
        else:
            total_value += 11
        num_aces -= 1
    return total_value


def dealer_sim(hand, deck):
    total_value = min(hand[0].value, 10) + min(hand[1].value, 10)
    used_ace = False
    if hand[0].value == 1:
        used_ace = True
        if total_value + 10 <= 21:
            total_value += 10

    if hand[1].value == 1 and not used_ace:
        used_ace = True
        if total_value + 10 <= 21:
            total_value += 10

    while total_value < 17:
        card = deck.draw()

        if not used_ace and card.value == 1:
            used_ace = True
            if total_value + 11 <= 21:
                total_value += 11
            else:
                total_value += 1
            continue
        total_value += min(card.value, 10)

    return total_value


def perform_action(action, hand, dealer_hand, deck: Deck):
    # STAY
    if action == 0:
        dealer_value = dealer_sim(dealer_hand, deck)
        hand_value = eval_hand(hand)

        # Dealer busted
        if dealer_value > 21:
            return True, 1

        # We Busted (shouldnt ever happen, is captured elsewhere)
        if hand_value > 21:
            return True, -2

        # We draw
        if hand_value == dealer_value:
            return True, 0

        # We have perfect hand
        if hand_value == 21:
            return True, 2

        # We beat the the dealer without either of us busting
        if hand_value > dealer_value and hand_value <= 21:
            return True, 1

        # Lost to dealer without either of us busting
        if hand_value < dealer_value:
            return True, -1

    # HIT
    elif action == 1:
        hand.append(deck.draw())
        new_hand_value = eval_hand(hand)

        # Busted
        if new_hand_value > 21:
            return True, -2

        return False, 0


def generate_input(dealer_visible_card, player_cards):
    input = [dealer_visible_card] + ([0] * 13)
    for card in player_cards:
        input[card] += 1
    return input

# After a game has been completed, we are left with a "history" of network_states.
# A batch update must be performed to update the neural network where the reward
# earned at the final action is passed down through the previous actions and 
# the network's weights are adjusted according to these rewards.
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
        previous_max_Qvalue = max(target)
        network.execute_back_progagation(network_state, target)


def run_q_learning(num_episodes, network: NeuralNetwork, max_steps, alpha, gamma, epsilon, delta_e):
    # STAY, HIT
    rewards = []
    for ep in range(num_episodes):
        deck = Deck()
        deck.shuffle()
        mean_reward = 0
        c1, c2, d1, d2 = deck.deal()
        hand = [c1, c2]
        dealer_hand = [d1, d2]
        history = []
        for step in range(max_steps):

            input = generate_input(d1.value, [c.value for c in hand])
            network_state = network.execute_forward_propagation(input)

            action = choose_action(network_state, epsilon)
            is_game_over, reward = perform_action(action, hand, dealer_hand, deck)

            history.insert(0, (network_state, reward))

            mean_reward += reward

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

            if is_game_over == True:
                if reward > 0:
                    wins += 1
                if reward == 0:
                    draws += 1
                break

    print(f"Wins: {wins}\nDraws: {draws}")
    print(f"Win rate: {wins/episodes}")


if __name__ == "__main__":
    Q = NeuralNetwork(14, 2, 100, 2)
    E = 0
    N = 10000
    A = 0.125
    E = 0.35
    G = 0.6
    DELTA_E = (-100 * E) / (E / (0.65 * N))
    run_q_learning(N, Q, 20, A, G, E, DELTA_E)
    test_blackjack(N, Q, 20, 0)
