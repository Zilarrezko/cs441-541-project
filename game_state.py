from random import randint
from typing import List
import numpy as np

from player import Player
from card import Card


class GameState:
    def __init__(self, deck_count: int, player_count: int):
        card_count = deck_count * 52
        self._deck_count = deck_count
        self._deck = [Card(j % 13 + 1, j // 13) for i in range(deck_count) for j in range(52)]
        self._players = [Player(i) for i in range(player_count)]
        self._player_count = player_count
        self._dealer = 0
        self._win_count = 0

    @property
    def win_count(self):
        return self._win_count

    @property
    def deck(self):
        return self._deck

    @property
    def player_count(self):
        return self._player_count

    @property
    def players(self):
        return self._players

    @property
    def deck_count(self):
        return self._deck_count

    def reset(self):
        # Reset the deck and shuffle
        self._deck = [
            Card(j % 13 + 1, j // 13) for i in range(self.deck_count) for j in range(52)
        ]
        self.shuffle_deck()

    def shuffle_deck(self):
        # Note (Dylan): Numpy Random Shuffle, shuffles the array contents in place.
        np.random.shuffle(self.deck)

    def draw_card(self, player: int):
        """
        Draws a card for the specified player at the given index.
        """
        card = self._deck.pop()
        self._players[player].add_card(card)
