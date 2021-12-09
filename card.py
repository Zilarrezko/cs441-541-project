class Card:
    def __init__(self, id: int, suit: int):
        self._id = id
        self._suit = suit

    @property
    def value(self):
        return self._id

    @property
    def suit(self):
        return self._suit

    @property
    def suit_name(self) -> str:
        suit = self.suit
        name = ""
        if suit == 0:
            name = "♦"
        if suit == 1:
            name = "♣"
        if suit == 2:
            name = "♥"
        if suit == 3:
            name = "♠"
        return name

    @property
    def name(self):
        if self.value < 11 and self.value > 1:
            return str(self.value)
        elif self.value == 1:
            return "A"
        elif self.value == 11:
            return "J"
        elif self.value == 12:
            return "Q"
        elif self.value == 13:
            return "K"

    def __str__(self) -> str:
        return self.name + " of " + self.suit_name
