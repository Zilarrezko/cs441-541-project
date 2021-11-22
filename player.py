from card import Card


class Player:
    def __init__(self, id: int, money: int = 100):
        self._hand = []
        self._id = id
        self._money = money
        self._staked_money = 0
        self._folded = False

    @property
    def id(self):
        return self._id

    @property
    def has_folded(self):
        return self._folded

    @property
    def hand(self):
        return self._hand

    @property
    def money(self):
        return self._money

    @property
    def bet(self):
        return self._staked_money

    def set_money(self, money: int):
        self._money = money

    def add_card(self, card: Card):
        self._hand.append(card)

    def add_money(self, money: int):
        self._money += money

    def remove_money(self, money: int):
        self._money -= money

    def set_folded(self, fold: bool):
        self._folded = fold

    def set_bet(self, amount: int):
        self._staked_money = amount

    def __str__(self) -> str:
        return f"Player ({self.id})"