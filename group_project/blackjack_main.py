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
    total_value = hand[0].value + hand[1].value
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
        total_value += deck.draw().value

    if total_value > 21:
        total_value = -1

    return total_value


def perform_action(action, state, hand, dealer_hand, deck: Deck):

    # STAY
    if action == 0:
        dealer_value = dealer_sim(dealer_hand, deck)
        hand_value = eval_hand(hand)

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
        new_hand_value = eval_hand(hand)
        new_s = State(new_hand_value, state.dealer)

        # Busted
        if new_hand_value > 21:
            return state, -2

        return new_s, 0


def run_q_learning(num_episodes, Q, max_steps, alpha, gamma, epsilon, delta_e):
    # STAY, HIT
    rewards = []
    for ep in range(num_episodes):
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


def run_mc(num_episodes, Q, max_steps, alpha, gamma, epsilon, delta_e):
    # STAY, HIT

    num_visits = {}
    total_return = {}
    for ep in range(num_episodes):
        deck = Deck()
        deck.shuffle()
        c1, c2, d1, d2 = deck.deal()
        hand = [c1, c2]
        dealer_hand = [d1, d2]
        states = []
        for step in range(max_steps):

            state = State(sum(c.value for c in hand), d1.value)

            action = choose_action(state, Q, epsilon)
            new_state, reward = perform_action(action, state, hand, dealer_hand, deck)
            states.append((state, action, reward))

            # This means we reached a terminal state. and Episode should end.
            if state == new_state:
                break

        # We have finished an episode
        # analyze it based on first visit MC algorithm
        seen = []
        for i in range(len(states)):
            state, action, _ = states[i]

            pair = (state, action)
            if pair in seen:
                continue

            seen.append(pair)
            # Get the total return starting from this state until terminal state
            # Where Total Return = Rt + Rt+1 * G + Rt+2 * G^1 + ...
            G = sum(x[2] * gamma ** t for t, x in enumerate(states[i:]))
            tr = total_return.get(pair, 0)
            nv = num_visits.get(pair, 0)
            tr += G
            nv += 1
            # Update the values with +1 occurrence and +G
            total_return[pair] = tr
            num_visits[pair] = nv

            # Update the Q table.
            Q[state][action] = tr / nv


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
    run_q_learning(N, Q, 20, A, G, E, DELTA_E)
    # run_mc(N, Q, 20, A, G, E, DELTA_E)
    test_blackjack(N, Q, 20, 0)
