from typing import List
import copy


LEARNING_RATE: float = 0.1


class NetworkState:
    def __init__(self, input_layer: List[float], hidden_layer: List[float], output_layer: List[float]) -> None:
        self.input_layer: List[float] = copy.deepcopy(input_layer)
        self.hidden_layers: List[List[float]] = copy.deepcopy(hidden_layer)
        self.output_layer: List[float] = copy.deepcopy(output_layer)


class NeuralNetwork:
    def __init__(self, input_size: int, hidden_amount: int, hidden_size: int, output_size: int) -> None:
        self.input_size: int = input_size
        self.hidden_amount: int = hidden_amount
        self.hidden_size: int = hidden_size
        self.output_size: int = output_size

        # initialize weights to value to 0
        self.input_weights: List[List[float]] = \
            [[0 for i in range(hidden_size)] for j in range(input_size)]

        self.hidden_weights: List[List[List[float]]] = \
            [[[0 for i in range(hidden_size)] for j in range(hidden_size)] for k in range(hidden_amount - 1)]

        self.output_weights: List[List[float]] = \
            [[0 for i in range(output_size)] for j in range(hidden_size)]


    def execute_forward_propagation(self, input: List[float]) -> NetworkState:
        hidden_layers = [self.calculate_next_layer(input, self.input_weights, self.hidden_size)]

        for i in range(self.hidden_amount - 1):
            hidden_layers.append(self.calculate_next_layer(hidden_layers[i], self.hidden_weights[i], self.hidden_size))

        output_layer = self.calculate_next_layer(hidden_layers[-1], self.output_weights, self.output_size)

        return NetworkState(input, hidden_layers, output_layer)


    def calculate_next_layer(self, layer: List[float], weights: List[List[float]], next_layer_size: int) -> List[float]:
        next_layer = []
        for i in range(next_layer_size):
            total = 0
            for j in range(len(layer)):
                total += layer[j] * weights[j][i]
            next_layer.append(total / len(layer))
        return next_layer


    def execute_back_progagation(self, network_state: NetworkState, target_output: List[float]) -> None:
        output_error = self.calculate_loss(network_state.output_layer, target_output)
        hidden_errors = [self.calculate_error(network_state.hidden_layers[-1], 
                                              self.output_weights, output_error)]

        for i in range(1, self.hidden_amount):
            hidden_index = self.hidden_amount - 1 - i
            hidden_errors.append(self.calculate_error(network_state.hidden_layers[hidden_index],
                                                      self.hidden_weights[hidden_index], hidden_errors[-1]))

        self.update_weights(network_state.hidden_layers[-1], self.output_weights, output_error)

        for i in range(1, self.hidden_amount):
            hidden_index = self.hidden_amount - 1 - i
            self.update_weights(network_state.hidden_layers[hidden_index], 
                                self.hidden_weights[hidden_index], hidden_errors[i])

        self.update_weights(network_state.input_layer, self.input_weights, hidden_errors[0])


    def calculate_loss(self, output: List[float], target_output: List[float]) -> List[float]:
        error = []
        for i in range(len(output)):
            error.append(output[i] - target_output[i])
        return error


    def calculate_error(self, layer: List[float], weights: List[List[float]], previous_error: List[float]) -> List[float]:
        new_error = []
        for i in range(len(layer)):
            summation = 0
            for j in range(len(previous_error)):
                if previous_error[j] != 0: 
                    summation += previous_error[j] + (layer[i] * weights[i][j])
            new_error.append(summation)
        return new_error


    def update_weights(self, layer: List[float], weights: List[List[float]], error: List[float]) -> None:
        global LEARNING_RATE
        for i in range(len(layer)):
            for j in range(len(error)):
                weights[i][j] += LEARNING_RATE * layer[i] * error[j]



