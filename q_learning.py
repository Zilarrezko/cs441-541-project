import numpy as np
from state import State
from deck import Deck
from blackjack import choose_action, perform_action, eval_hand
from matplotlib.pyplot import legend, plot, savefig, clf


def q_learning_train(num_episodes, Q, max_steps, alpha, gamma, epsilon, delta_e):
    # STAY, HIT
    wrs = []
    lrs = []
    drs = []
    wins = 0
    draws = 0
    for ep in range(num_episodes):
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

            Qo = Q.get(state, [0, 0])[action]
            Qn = np.max(Q.get(new_state, [0, 0]))

            Q[state][action] = Qo + alpha * (reward + gamma * Qn - Qo)
            mean_reward += reward

            # This means we reached a terminal state. and Episode should end.
            if state == new_state:
                if reward > 0:
                    wins += 1
                elif reward == 0:
                    draws += 1
                break

        div = ep + 1
        cur_wr = wins / div
        cur_dr = draws / div
        cur_lr = (div - wins - draws) / div
        wrs.append(cur_wr)
        drs.append(cur_dr)
        lrs.append(cur_lr)

        if ep % 100 == 0:
            epsilon += delta_e

    plot(wrs, label="Win Rate")
    plot(drs, label="Draw Rate")
    plot(lrs, label="Loss Rate")
    legend()
    savefig("data/q_learning_training.png")
    with open("data/q_learning_training.csv", "w") as file:
        file.write("WR, DR, LR\n")
        for i in range(len(wrs)):
            file.write(f"{wrs[i]},{drs[i]},{lrs[i]}\n")
    clf()
