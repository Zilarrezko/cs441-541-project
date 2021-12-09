from card import Card


class Player:
    def __init__(self, id: int):
        self._hand = []
        self._id = id

    @property
    def id(self):
        return self._id

    @property
    def hand(self):
        return self._hand

    def add_card(self, card: Card):
        self._hand.append(card)

    def __str__(self) -> str:
        return f"Player ({self.id})"