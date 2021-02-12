import random

class Deck:
    def __init__(self):
        self.cards = [Card(i, j) for j in range(2, 15) for i in range(4)]

    def shuffle(self):
        num_cards = len(self.cards)
        for i in range(num_cards):
            j = random.randrange(i, num_cards)
            self.cards[i], self.cards[j] = self.cards[j], self.cards[i]

    def remove(self, card):
        if card in self.cards:
            self.cards.remove(card)
            return True
        else:
            return False

    def pop(self):
        return self.cards.pop(0)

    def is_empty(self):
        return len(self.cards) == 0

    def deal(self, hand):
        hand.add(self.pop())


class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        if suit < 2:
            self.colour = 'zwart'
        else:
            self.colour = 'rood'

    def __lt__(self, other):
        return self.rank < other.rank

    def __le__(self, other):
        return self.rank <= other.rank

    def __ge__(self, other):
        return self.rank >= other.rank

    def __gt__(self, other):
        return self.rank > other.rank

    def __eq__(self, other):
        return self.rank == other.rank

    def __repr__(self):

        suits = ['♤', '♧', '♦️', '♥️']
        rank = ['2', '3', '4', '5', '6', '7',
                '8', '9', '10', 'J', 'Q', 'K', 'A']
        return f'{suits[self.suit]}{rank[self.rank - 2]}'

    def __str__(self):
        suits = ['♤', '♧', '♦️', '♥️']
        rank = ['2', '3', '4', '5', '6', '7',
                '8', '9', '10', 'J', 'Q', 'K', 'A']
        return f'{suits[self.suit]}{rank[self.rank - 2]}'


class Player(Deck):
    def __init__(self, name="", player_id=0):
        super().__init__()
        self.cards = []
        self.name = name.capitalize()
        self.id = player_id

    def add(self, card):
        self.cards.append(card)
        self.cards = sorted(self.cards)

    def __repr__(self):
        return self.id

    def __str__(self):
        return self.name


class CardGame:
    def __init__(self):
        self.deck = Deck()
        self.deck.shuffle()

    def new_deck(self):
        self.deck = Deck()
        self.deck.shuffle()


class Bussen(CardGame):

    def __init__(self):
        super().__init__()
        self.players = []
        self.current_player = None
        self.started = False

        # Where we are in the game
        self.game_status = 0

        # keep track of the pyramid
        self.piramide_cards = []
        self.piramide_progress = 0
        self.piramide_row = 1

        # keeping track of the bus
        self.bus_revealed = 0
        self.bus_cards = []
        self.bus_progress = 0
        self.slokken = 0
        self.bus_length = 7
        self.bus_speler = None

    def play(self, text="", user=None, initiate=False):

        if initiate:
            self.started = True
            self.current_player = self.players[0]
            return self.kleur(initiate=True)

        if not self.started:
            return

        # check if it is this player's turn
        if not self.check_turn(user):
            return None

        if self.game_status == 0:
            output = self.kleur(text)
        elif self.game_status == 1:
            output = self.hogerlager(text)
        elif self.game_status == 2:
            output = self.binnenbuiten(text)
        elif self.game_status == 3:
            output = self.hebjehemal(text)
        elif self.game_status == 4:
            output = self.piramide(text, user)
        elif self.game_status == 5:
            output = self.bus(text)
        elif self.game_status == 6:
            return f"Type '!end'\n"
        else:
            print(f'The game status broke :), it is {self.game_status}')
            output = 'something went wrong'

        return output

    def not_accept(self, text):
        # which  inputs will be accepted for each game state
        kleur = ("zwart", "rood", "groen", "paars", "blauw", "oranje", "wit")
        hoger_lager = ("hoger", "lager", "op")
        binnen_buiten = ("binnen", "buiten", "op")
        hebjehem = ("ja", "nee", "regenboog", "kwartet")
        pira = ("ja", "next")
        bus = ("hoger", "lager", "op", "paal", "hetzelfde", "gelijk", "h", "l")
        all_inputs = list((kleur, hoger_lager, binnen_buiten, hebjehem, pira, bus))
        for part in all_inputs[self.game_status]:
            if part in text:
                return False
        return True

    def kleur(self, text="", initiate=False):
        if initiate:
            output = f"De eerste ronde, welke kleur heeft de kaart? {self.current_player.name} begint.\n"
            return output

        if self.not_accept(text):
            return

        output = ""
        card = self.next_card()

        if "zwart" in text and "rood" in text:
            output += f"{card} Zo kan ik het ook, Neem 1 slok\n"
        elif card.colour in text:
            output += f"{card} Goed.\n"
        else:
            output += f"{card} fout!, Zuipen\n"

        self.deck.deal(self.current_player)

        if self.next_player():
            output += f"{self.current_player.name}, rood of zwart?\n"
        else:
            output += self.hogerlager(initiate=True)
        return output

    def hogerlager(self, text="", initiate=False):
        if initiate:
            self.initiate()
            output = f"Ronde twee. {self.current_player.name}, " \
                     f"hoger of lager dan je {self.current_player.cards[0]}?\n "
            return output

        if self.not_accept(text):
            return None

        player_card = self.current_player.cards[0]
        next_card = self.next_card()

        output = ""

        # check if the player guessed right
        if (player_card < next_card and text == 'hoger') or (player_card > next_card and text == 'lager') \
                or (player_card == next_card and text == 'op'):

            output += f"{next_card} Goed\n"
        else:

            output += f"{next_card} Fout, drinken.\n"

        self.deck.deal(self.current_player)

        if self.next_player():
            output += f"{self.current_player.name}, hoger of lager dan je {self.current_player.cards[0]}?\n"
        else:
            output += self.binnenbuiten(text, initiate=True)

        return output

    def binnenbuiten(self, text, initiate=False):
        if initiate:
            self.initiate()
            output = f"Ronde drie. {self.current_player.name}," \
                     f" binnen of buiten je {self.current_player.cards[0]} en {self.current_player.cards[1]}?\n"
            return output

        if self.not_accept(text):
            return

        card = self.next_card()
        lower_card = self.current_player.cards[0]
        higher_card = self.current_player.cards[1]
        output = ""

        if (lower_card < card < higher_card) and "binnen" in text:
            output += f"{self.next_card()} Goed.\n"
        elif (card < lower_card or card > higher_card) and "buiten" in text:
            output += f"{self.next_card()} Goed.\n"
        elif (card is lower_card or card is higher_card) and "op" in text:
            output += f"{self.next_card()} Goed.\n"
        else:
            output += f"{self.next_card()} Fout, drinken.\n"

        self.deck.deal(self.current_player)

        if self.next_player():
            output += f"{self.current_player.name}, binnen of buiten je" \
                      f" {self.current_player.cards[0]} en {self.current_player.cards[1]}?\n"
        else:
            output += self.hebjehemal(text, initiate=True)

        return output

    def hebjehemal(self, text, initiate=False):
        if initiate:
            self.initiate()
            output = f"Ronde 4. {self.current_player.name}, heb je hem al?" \
                     f" {self.current_player.cards[0]} {self.current_player.cards[1]} " \
                     f"{self.current_player.cards[2]}\n "
            return output

        if self.not_accept(text):
            return

        colors = set([card.suit for card in self.current_player.cards])
        output = ""
        if text == 'regenboog':
            if self.next_card().suit not in colors and len(colors) == 3:
                output += f"{self.next_card()} REGENBOOG!! Iedereen drinken!\n"
            else:
                output += f"{self.next_card()} Fout! {len(self.players)} " \
                          f"slok{'ken' if len(self.players) > 1 else ''}!\n"
        elif text == 'kwartet':
            if self.next_card().suit not in colors:
                output += f"{self.next_card()} Fout! {len(self.players)} " \
                          f"slok{'ken' if len(self.players) > 1 else ''}!\n"
            else:
                output += f"{self.next_card()} KWARTET!! Iedereen drinken!\n"
        elif text == 'ja':
            if self.next_card().suit in colors:
                output += f"{self.next_card()} Goed.\n"
            else:
                output += f"{self.next_card()} Fout, drinken.\n"
        elif text == 'nee':
            if self.next_card().suit not in colors:
                output += f"{self.next_card()} Goed.\n"
            else:
                output += f"{self.next_card()} Fout, drinken.\n"
        else:
            output += f"{self.next_card()} Fout, drinken.\n"

        self.deck.deal(self.current_player)

        if self.next_player():
            output += f"{self.current_player.name}, heb je hem al? " \
                      f"{self.current_player.cards[0]} {self.current_player.cards[1]} " \
                      f"{self.current_player.cards[2]}\n"
        else:
            output += self.piramide(text, initiate=True)

        return output

    def piramide(self, text, user=None, initiate=False):
        if initiate:
            self.initiate()
            self.piramide_cards = [self.deck.pop() for _ in range(15)]
            output = f"Nu jullie vier kaarten hebben kan de piramide beginnen!\n type 'ja' om een kaart op te gooien\n"
            output += f"type 'next' voor de volgende kaart\n"
            output += f"type '!cards' om je kaarten te zien (doet ie nog niet hoor, goed je kaarten onthouden\n"

            for player in self.players:
                output += f"{player.name}: {''.join([str(card) for card in player.cards])} \n"
            output += self.show_piramide()
            return output

        output = ""

        if self.not_accept(text):
            return

        for player in self.players:
            if player.id == user.id:
                user = player
                break

        if text == 'next':
            if time.time()+10 < self.make_sure_nobody_nexts_too_fast:
                continue
            else:
                self.make_sure_nobody_nexts_too_fast = time.time()
                return "Niet zo snel!! ik ben ook maar dronken"
            self.piramide_progress += 1
            if self.piramide_progress in [5, 9, 12, 14]:
                self.piramide_row += 1

            if self.piramide_progress >= 15:
                output += self.bus(text, initiate=True)
                return output

            return self.show_piramide()

        if not text.startswith('ja'):
            return False

        current_piramide = self.piramide_cards[self.piramide_progress]

        discard = []
        for card in user.cards:
            if card.rank == current_piramide.rank:
                discard.append(card)

        if len(discard) > 0:
            output += f"{user.name}, je mag {self.piramide_row * len(discard)} " \
                      f"slok{'ken' if self.piramide_row * len(discard) > 1 else ''} uitdelen.\n"
            for card in discard:
                user.cards.remove(card)
        else:
            output += f"{user.name}, je hebt deze kaart niet, drinken.\n"

        return output

    def bus(self, text, initiate=False):
        if initiate:
            self.initiate()
            self.create_bus()
            self.new_bus_speler()
            output = f"{self.current_player} moet de bus in! zeg h(oger) of l(ager) om er uit te komen\n"
            output += self.bus_string()
            return output

        if self.not_accept(text):
            return

        output = ""
        if self.deck.is_empty():
            self.reshuffle_bus()
            output += 'Oei de stapel is op, maar geen paniek! we gaan gewoon door\n'

        buscard = self.bus_cards[self.bus_progress]
        next_card = self.next_card()

        # check if hoger or lager is correct
        if next_card > buscard and text in ['h', 'hoger'] or next_card < buscard and text in ['l', 'lager']:
            # check if new card is unlocked
            if self.bus_progress == self.bus_revealed:
                self.bus_revealed += 1
                output += self.bus_string()

            # updates the bus
            output += f"{next_card} Goed.\n"
            self.add_bus(self.deck.pop())
            output += self.bus_string()
            self.bus_progress += 1

            # checks if player is finished
            if self.bus_progress >= self.bus_length:
                output += self.end()
                return output

        # if you guesses 'op' correctly you are out
        elif next_card == buscard and text in ['op', 'paal', 'gelijk', 'hetzelfde']:
            output += f"{next_card} GOED!!!\n"
            output += self.end()
            return output
        else:
            if self.bus_progress == self.bus_revealed:
                self.bus_revealed += 1
                output += self.bus_string()

            self.slokken += self.bus_progress + 1
            output += f"{self.next_card()} fout! {self.bus_progress + 1} slok{'ken' if self.bus_progress > 0 else ''}\n"
            self.add_bus(self.deck.pop())
            output += self.bus_string()
            self.bus_progress = 0

        output += f"Hoger of lager dan {self.ask_bus()}?\n"

        return output

    def ask_bus(self):
        return self.bus_cards[self.bus_progress] if self.bus_progress < self.bus_revealed else '--'

    def end(self):
        if self.game_status == 5:
            output = f"Gefeliciteerd {self.current_player.name}, je bent uit de bus gekomen na {self.slokken} slokken!\n"
            self.game_status = 6
        else:
            output = f"gestopt\n"
            self.game_status = 6
        return output + "einde"

    def show_piramide(self):
        output = f"--"
        for iterate in range(15):
            if iterate <= self.piramide_progress:
                output += f"{self.piramide_cards[iterate]}--"
            else:
                output += f"----"
        return output + "\n"

    def initiate(self):
        self.current_player = self.players[0]
        self.game_status += 1
        return

    def check_turn(self, user):
        # True if this player may continue
        if any(x.id == user.id for x in self.players):
            if user.id == self.current_player.id or self.game_status == 4:
                return True

        return False

    def next_player(self):
        try:
            ind = self.players.index(self.current_player)
            self.current_player = self.players[ind + 1]
            return True
        except IndexError:
            self.current_player = self.players[0]
            return False

    def add_bus(self, card):
        self.bus_cards[self.bus_progress] = card
        return

    def create_bus(self):
        self.new_deck()
        for _ in range(self.bus_length):
            self.bus_cards.append(self.deck.pop())
        return

    def new_bus_speler(self):
        new_speler = self.players[0]

        possible_players = [new_speler]

        for speler in self.players:
            # krijg een lijst met spelers met de meeste kaarten
            if len(speler.cards) > len(possible_players[0].cards):
                possible_players = [speler]
            elif len(speler.cards) == len(possible_players[0].cards):
                possible_players.append(speler)

        if len(possible_players) == 1:
            self.current_player = random.choice(possible_players)
            return

        if len(possible_players[0].cards) == 0:
            self.current_player = random.choice(possible_players)
            return

        while True:
            all_cards = [player.cards.pop() for player in possible_players]
            lowest_card = min(all_cards)
            indexes = []
            for index, card in enumerate(all_cards):
                if card > lowest_card: # checks which cards are higher, so dont get in the bus
                    indexes.append(index)
            for index in reversed(indexes):
                del possible_players[index]
            if len(possible_players) == 1:
                self.current_player = possible_players[0]
                return
            elif len(possible_players[0].cards) == 0:
                self.current_player = random.choice(possible_players)
                return


    def reshuffle_bus(self):
        # Shuffles the deck when the player went through all cards in the bus. Keeps the current bus.
        self.new_deck()
        for card in self.bus_cards:
            self.deck.remove(card)
        return

    def bus_string(self):
        # creates the string for the bus to print
        if not self.bus_cards:
            return
        bus_string = ""
        for card in self.bus_cards[:self.bus_revealed]:
            bus_string += str(card) + '-'
        for _ in range(self.bus_revealed, self.bus_length):
            bus_string += "---"
        bus_string += "\n"
        return bus_string

    def next_card(self):
        return self.deck.cards[0]

    def join(self, user_id, user_name):
        if user_id in [player.id for player in self.players]:
            output = "Adtje des, je doet al mee"
        elif self.started:
            output = "laupie we zijn al begonnen"
        elif len(self.players) >= 7:
            output = "Sorry, er kunnen maar 7 mensen meedoen"
        else:
            self.players.append((Player(user_name, user_id)))
            output = f'Welkom {user_name}'

        return output

    def leave(self, user_id):
        # leave the game before it started

        for player in self.players:
            if player.id != user_id:
                continue

            if self.started:
                output = "Je kunt niet halverwege het spel weggaan, laf!!!"
            else:
                self.players.remove(player)
                output = "ok doei"
            break

        else:
            output = "Je doet niet eens mee kerel"

        return output, len(self.players) == 0

    def show_cards(self, user):
        for player in self.players:
            if player.id == user.id:
                _user = player
                break
        else:
            return "wat denk je zelf?"

        cards = _user.name + ": " + " ".join([str(card) for card in _user.cards])

        return cards


if __name__ == "__main__":
    pass
