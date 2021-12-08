class State:


    def __init__(self, hand, dealer):
        self._hand = hand
        self._dealer = dealer


    @property
    def hand(self):
        return self._hand

    @property
    def dealer(self):
        return self._dealer

    def __hash__(self) -> int:
        return hash(self.dealer + self.hand)
    
    def __eq__(self, o: object) -> bool:
        return self.hand == o.hand and self.dealer == o.dealer