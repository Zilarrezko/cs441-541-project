import os
from blackjack import q_table_blackjack_test
from q_learning import q_learning_train
from monte_carlo import monte_carlo_train
from deep_q_learning import deep_q_learning_train, deep_q_learning_test
from neural_network import NeuralNetwork
from state import State

def output_action_table(Q):
    print("    A 2 3 4 5 6 7 8 9 10");
    for i in range(4, 22):
        print((" " if i < 10 else "") + str(i), end="  ");
        for j in range(1, 11):
            state = State(i, j);
            thinger = Q.get(state);
            if thinger == None:
                action = "?";
            else:
                action = "S" if thinger[0] > thinger[1] else "H";
            print(action, end=" ");
        print("");

if __name__ == "__main__":
    if not os.path.exists("data"):
        os.makedirs("data")

    # Q-Learning
    print(">> Q-Learning:");
    Q = {}
    N = 10000
    A = 0.125
    E = 0.35
    G = 0.6
    DELTA_E = (-100 * E) / (E / (0.65 * N))
    q_learning_train(N, Q, 20, A, G, E, DELTA_E)
    output_action_table(Q)
    q_table_blackjack_test(N, Q, 20, 0)
    print("");

    # Monte Carlo
    print(">> Monte Carlo:");
    Q = {}
    N = 10000
    A = 0.125
    E = 0.35
    G = 0.6
    DELTA_E = (-100 * E) / (E / (0.65 * N))
    monte_carlo_train(N, Q, 20, A, G, E, DELTA_E)
    output_action_table(Q)
    q_table_blackjack_test(N, Q, 20, 0)
    print("");

    # Deep Q-Learning
    print(">> Deep Q-Learning:");
    Q = NeuralNetwork(14, 2, 100, 2)
    N = 10000
    A = 0.125
    E = 0.35
    G = 0.6
    DELTA_E = (-100 * E) / (E / (0.65 * N))
    deep_q_learning_train(N, Q, 20, A, G, E, DELTA_E)
    deep_q_learning_test(N, Q, 20, 0)
