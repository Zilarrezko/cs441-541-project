import numpy as np
import random
from state import State
from deck import Deck

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


def perform_action(action, state, hand, dealer_hand, deck: Deck):

    # STAY
    if action == 0:
        dealer_value = dealer_sim(dealer_hand, deck)
        hand_value = eval_hand(hand)

        # Dealer busted
        if dealer_value > 21:
            return state, 1

        # We Busted (shouldnt ever happen, is captured elsewhere)
        if hand_value > 21:
            return state, -2

        # We draw
        if hand_value == dealer_value:
            return state, 0

        # We have perfect hand
        if hand_value == 21:
            return state, 2

        # We beat the the dealer without either of us busting
        if hand_value > dealer_value and hand_value <= 21:
            return state, 1

        # Lost to dealer without either of us busting
        if hand_value < dealer_value:
            return state, -1

    # HIT
    elif action == 1:
        hand.append(deck.draw())
        new_hand_value = eval_hand(hand)
        new_s = State(new_hand_value, state.dealer)

        # Busted
        if new_hand_value > 21:
            return state, -2

        return new_s, 0

def q_table_blackjack_test(episodes, Q, max_steps, epsilon):
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

            state = State(eval_hand(hand), d1.value)

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
