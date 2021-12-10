import numpy as np

from card import Card


class Deck:
    def __init__(self):
        self._cards = [Card(card, suit) for suit in range(4) for card in range(1, 14)]

    def shuffle(self):
        np.random.shuffle(self._cards)

    def draw(self):
        return self._cards.pop()

    def deal(self):
        return self.draw(), self.draw(), self.draw(), self.draw()
