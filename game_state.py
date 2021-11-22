from random import randint
from typing import List
import numpy as np

from player import Player
from card import Card


class GameState:
    def __init__(self, deck_count: int, player_count: int):
        card_count = deck_count * 52
        self._deck_count = deck_count
        self._deck = [Card(j + 1, j // 13) for i in range(deck_count) for j in range(52)]
        self._players = [Player(i, 100) for i in range(player_count)]
        self._player_count = player_count
        self._dealer = 0
        self._win_count = 0
        # Note(jesse): Blackjack specific
        # Note(jesse): Poker Specific
        self._community_cards = []
        self._pool = 0

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

    @property
    def community_cards(self):
        return self._community_cards

    @property
    def folded_players(self):
        return [player for player in self.players if player.has_folded]

    @property
    def pot(self):
        return self._pot

    @property
    def players_in_play(self):
        return sum(1 for player in self.players if not player.has_folded)

    def reset(self):
        # Reset the deck and shuffle
        self._deck = [
            Card(j % 13 + 1, j // 13) for i in range(self.deck_count) for j in range(52)
        ]
        self.shuffle_deck()

        # Set all players to have $100, and unfold
        for player in self.players:
            player.set_money(100)
            player.set_folded(False)

        # Clear public cards & Folder players
        self._community_cards.clear()

        # Set the pot to 0.
        self._pot = 0

    def shuffle_deck(self):
        # Research/Note(jesse): You can not generate a permutation of any length 52
        # without at least 226 bits of state. We can't generate all possible permutations
        # of a deck of cards here... 52 factorial
        # And if we end up using multiple decks, the problem is compounded, keeping the same
        # subset length within the new bigger set of permutations
        # Python is using a 32bit state Mersenne Twister, a far cry from 226bits.
        # There's probably a library for a 256bit one, I have not looked too hard.
        # maybe it's enough. Also... Maybe we don't care

        # Note (Dylan): Numpy Random Shuffle, shuffles the array contents in place.
        np.random.shuffle(self.deck)

    def draw_card(self, player: int):
        """
        Draws a card for the specified player at the given index.
        """
        card = self._deck.pop()
        self._players[player].add_card(card)
