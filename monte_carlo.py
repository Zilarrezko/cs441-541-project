from state import State
from deck import Deck
from blackjack import choose_action, perform_action, eval_hand
from matplotlib.pyplot import legend, plot, savefig, clf

def monte_carlo_train(num_episodes, Q, max_steps, alpha, gamma, epsilon, delta_e):
    num_visits = {}
    total_return = {}
    wrs = []
    lrs = []
    drs = []
    wins = 0
    draws = 0
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

    plot(wrs, label="Win Rate")
    plot(drs, label="Draw Rate")
    plot(lrs, label="Loss Rate")
    legend()
    savefig("data/monte_carlo_training.png")
    with open("data/monte_carlo_training.csv", "w") as file:
        file.write("WR, DR, LR\n")
        for i in range(len(wrs)):
            file.write(f"{wrs[i]},{drs[i]},{lrs[i]}\n")
    clf()