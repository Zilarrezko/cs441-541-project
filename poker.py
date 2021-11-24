from random import randint
from typing import List
from card import Card
from game_state import GameState
from player import Player


class PokerAction:
    fold = 0
    call = 1     # Note(jesse): includes check (nothing to add to pot)
    raising = 2  # Note(jesse): can't use "raise" because it's a keyword
    count = 3


class PokerStrategy:
    random = 0
    reinforced_learning = 1
    count = 2


def poker_init(state: GameState):
    state.reset()
    for i in range(state.player_count * 2):
        state.draw_card(i % state.player_count)

def poker_end(state: GameState, winner: int):
    # Give money to the player.
    state.players[winner].add_money(state.pot)
    for player in state.players:
        # Add player's cards back into the deck
        state.append_cards(player.hand);
        # Clear the player's hand.
        player.hand.clear()
        player.set_folded(False)

def play_poker(state: GameState, strategy: int, printing: bool):
    poker_init(state)
    state.dealer = 0
    # Todo(jesse): Big blind/small blind? Other Poker things?
    # for i in range(len(state.players)):
    # 	print("player", i, ":", card_print(state.players[i]))

    highest_bet = 0
    in_play = len(state.players)
    for turn in range(4):
        print(
            ">> Turn",
            turn,
            "pot:",
            state.pot,
            "community:",
            [str(card) for card in state.community_cards],
        )
        betting = True
        last_raise = -1
        while betting:
            if in_play == 1:
                    break
            betting = False
            for player in state.players:
                if player == last_raise:
                    break
                if player.has_folded:
                    continue

                action, stake = get_poker_action(state, player, strategy)
                if action == PokerAction.fold:
                    player.set_folded(True)
                    in_play -= 1

                elif action == PokerAction.call:
                    bet = player.bet
                    if bet < highest_bet:
                        to_bet = highest_bet - bet
                        state.pot += to_bet
                        player.remove_money(to_bet)
                        player.set_bet(highest_bet)

                elif action == PokerAction.raising:
                    if stake > 0:
                        betting = True
                        state.pot += stake
                        player.remove_money(stake)
                        player.set_bet(highest_bet + stake)
                        highest_bet = player.bet
                        print("new highest bet:", highest_bet)
                        last_raise = player

                if action == PokerAction.fold:
                    print(f"{player}, folded")
                    if in_play == 1:
                        break
                elif action == PokerAction.call:
                    print(f"{player}, called bet: {player.bet}")
                elif action == PokerAction.raising:
                    print(f"{player}, raised: {stake}, bet: {player.bet}")

        if in_play == 1:
                break
        if turn == 0:
            for i in range(3):
                state.community_cards.append(state.deck.pop())
        elif turn < 3:
            state.community_cards.append(state.deck.pop())
    winner = poker_assess_players(state, printing)
    poker_end(state, winner);


# Note(jesse):
# value:
#  1 - pair
#  2 - two pair
#  3 - three of a kind
#  4 - straight
#  5 - flush
#  6 - full house
#  7 - four of a kind
#  8 - straight flush
#  9 - royal flush
hand_value_strings = [
    "----",
    "pair",
    "two pair",
    "three of a kind",
    "straight",
    "flush",
    "full house",
    "four of a kind",
    "straight flush",
    "royal flush",
]


def poker_hand_value(state: GameState, hand: List[Card]) -> int:
    value = 0
    suits = [0]*4
    cards = [0]*13
    for card in hand:
        val = card.value
        suits[card.suit] += 1
        cards[val - 1] += 1

    for card in state.community_cards:
        val = card.value
        suits[card.suit] += 1
        cards[val - 1] += 1

    highest_suit = 0
    for i in range(4):
        highest_suit = max(highest_suit, suits[i])

    run = 0
    run_end = 0
    pair_count = three_count = four_count = 0
    for i in range(13):
        count = cards[i]
        if count == 2:
            pair_count += 1
        elif count == 3:
            three_count += 1
        elif count == 4:
            four_count += 1
        if cards[i] > 0 and i > 0 and cards[i - 1] > 0:
            if run == 0:
                run = 2
            else:
                run += 1
            run_end = i

    if pair_count == 1:
        value = 1
    if pair_count == 2:
        value = 2
    if three_count == 1:
        value = 3
    if run >= 5:
        value = 4
    if highest_suit >= 5:
        value = 5
    if pair_count == 1 and three_count == 1:
        value = 6
    if four_count == 1:
        value = 7
    if highest_suit >= 5 and run >= 5:
        value = 8
    if highest_suit >= 5 and run >= 5 and run_end == 14:
        value = 9

    return value


# Todo(jesse): Finish this
def poker_assess_players(state: GameState, printing: bool = True) -> int:
    contenders = [];
    best_player = 0;
    best_hand = 0
    for i in range(len(state.players)):
        player = state.players[i];
        hand = player.hand
        player_value = poker_hand_value(state, hand)
        print(
            f"{player} with {[str(card) for card in player.hand]}, with value:{player_value}, {hand_value_strings[player_value]}"
        )
        if player_value > best_hand:
            contenders.clear();
            contenders.append(i);
            best_player = i
            best_hand = player_value
        elif player_value == best_hand:
            contenders.append(i);
    best_high = 0;
    for i in contenders:
        player = state.players[i];
        hand_score = 0;
        for card in player.hand:
            if card.value == 1:
                hand_score += 14;
            else:
                hand_score += card.value;
        if best_high < hand_score:
            best_high = hand_score;
            best_player = i;
    return best_player;


def get_poker_action(
    state: GameState, cur_player: Player, strategy: int
) -> tuple[PokerAction, int]:
    if strategy == PokerStrategy.random:
        action = randint(0, PokerAction.count - 1)
        stake = 0
        if action == PokerAction.raising:
            stake = min(randint(1, 5), cur_player.money)
        return action, stake
    # elif strategy == PokerStrategy.reinforced_learning:
    # Todo(jesse): We need to fill this out, as well as a second one
