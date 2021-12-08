import numpy as np
import random
from state import State
from deck import Deck
from matplotlib.pyplot import plot, savefig


def choose_action(state, Q, E):
    action_values = Q.get(state, None)
    if action_values == None:
        action_values = [0, 0]
        Q[state] = action_values

    if random.random() <= E:
        return np.random.choice([0, 1])

    return np.argmax(action_values)


def dealer_sim(hand, deck):
    total_value = hand[0].value + hand[1].value
    while total_value < 16:
        total_value += deck.draw().value

    if total_value > 21:
        total_value = -1

    return total_value


def perform_action(action, state, hand, dealer_hand, deck: Deck):

    # STAY
    if action == 0:
        dealer_value = dealer_sim(dealer_hand, deck)
        hand_value = state.hand

        # Dealer busted
        if dealer_value == -1:
            return state, 1

        # Draw
        if hand_value == dealer_value:
            return state, 0

        # Perfect hand
        if hand_value == 21:
            return state, 2

        # We beat the the dealer without either of us busting
        if hand_value > dealer_value and hand_value <= 21:
            return state, 1
        # Lost to dealer without either of us busting
        if hand_value < dealer_value:
            return state, -1
        # Busted
        if hand_value > 21:
            return state, -2
    # HIT
    elif action == 1:
        hand.append(deck.draw())
        new_hand_value = sum(c.value for c in hand)
        new_s = State(new_hand_value, state.dealer)

        # Busted
        if new_hand_value > 21:
            return state, -2

        return new_s, 0


def run_blackjack(episodes, Q, max_steps, alpha, gamma, epsilon, delta_e):
    # STAY, HIT
    rewards = []
    for ep in range(episodes):
        deck = Deck()
        deck.shuffle()
        mean_reward = 0
        c1, c2, d1, d2 = deck.deal()
        hand = [c1, c2]
        dealer_hand = [d1, d2]
        for step in range(max_steps):

            state = State(sum(c.value for c in hand), d1.value)

            action = choose_action(state, Q, epsilon)
            new_state, reward = perform_action(action, state, hand, dealer_hand, deck)

            Qo = Q.get(state, [0, 0])[action]
            Qn = np.max(Q.get(new_state, [0, 0]))

            Q[state][action] = Qo + alpha * (reward + gamma * Qn - Qo)
            mean_reward += reward

            # This means we reached a terminal state. and Episode should end.
            if state == new_state:
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


def test_blackjack(episodes, Q, max_steps, epsilon):
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

            state = State(sum(c.value for c in hand), d1.value)

            action = choose_action(state, Q, epsilon)
            new_state, reward = perform_action(action, state, hand, dealer_hand, deck)

            # This means we reached a terminal state. and Episode should end.
            if state == new_state:
                if reward > 0:
                    wins += 1
                if reward == 0:
                    draws += 1
                break

    print(f"Wins: {wins}\nDraws: {draws}")
    print(f"Win rate: {wins/episodes}")


if __name__ == "__main__":
    Q = {}
    E = 0
    N = 10000
    A = 0.125
    E = 0.35
    G = 0.6
    DELTA_E = (-100 * E) / (E / (0.65 * N))
    run_blackjack(N, Q, 20, A, G, E, DELTA_E)
    test_blackjack(N, Q, 20, 0)
