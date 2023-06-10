import re
from random import randint as rnd
import math


class Card:
    def __init__(self, name='Компьютер'):
        self.name = name
        self.card = self.create_card()

    def __str__(self):
        card = f'-------Игрок {self.name} ------\n'
        for i in self.card:
            card += '  '.join(i) + '\n'
        card += '--------------------------'
        return card

    @staticmethod
    def create_nums(end_num):
        numbers_list = []
        while len(numbers_list) < end_num:
            num = rnd(1, 90)
            if num not in numbers_list:
                numbers_list.append(num)
        return numbers_list

    def create_card(self):
        card = []
        card_list = self.create_nums(15)
        ind_star = 0
        for lin in range(1, 4):
            ind_end = math.ceil(len(card_list) / 3) * lin
            lining = [str(el) for el in sorted(card_list[ind_star:ind_end])]
            for i in range(4):
                index = rnd(0, ind_end)
                lining.insert(index, '')
            ind_star = ind_end
            card.append(lining)
        return card


class PlayBalls:

    def __init__(self):
        self.bingo_balls = Card.create_nums(90)
        self.cards = self.get_cards()

    @staticmethod
    def get_cards():
        cards = []
        num_player = int(input('Введите количество игроков(с учетом компьютера):\n'))
        for i in range(1, num_player + 1):
            name = input(f'Введите имя игрока № {i}\n(что бы выбрать компьютер оставьте имя пустым)\n')
            if name == '':
                cards.append(Card())
            else:
                cards.append(Card(name))
            print(f'Добавлен Игрок:{cards[-1].name}\n')
        return cards

    def win(self, card, num):
        for line in card.card:
            if str(num) in line:
                index = line.index(str(num))
                line[index] = '-'
                print(card)
                new_list = [item for sublist in card.card for item in sublist]
                if not re.search(r'[0-9]', ''.join(new_list)):
                    print(f'Игрок {card.name} выиграл! =D')
                    raise 'End'
                return True
        if card.name != 'Компьютер':
            self.end(num, card, False)

    def end(self, num, card, i=True):
        for line in card.card:
            if (str(num) in line) == i:
                print(f'Игрок {card.name} выбыл')
                self.cards.remove(card)
                if len(self.cards) == 0:
                    raise 'End'
                return True

    def play(self):
        for ind, num in enumerate(self.bingo_balls):
            for card in self.cards:
                print(f'          Ход {ind + 1}')
                print(f'Новый бочонок: {num} (осталось {len(self.bingo_balls) - ind - 1})')
                print(card)
                if card.name == 'Компьютер':
                    self.win(card, num)
                else:
                    self.player(card, num)

    def player(self, card, num):
        while True:
            answer = input('Зачеркнуть цифру? (y/n)\n')
            if answer == 'y':
                self.win(card, num)
                self.end(num, card)
                break
            elif answer == 'n':
                self.end(num, card)
                break
            else:
                print('Введите (y/n)')


def main():
    try:
        bingo_balls = PlayBalls()
        bingo_balls.play()
    except TypeError:
        print('Игра окончена!!')


if __name__ == '__main__':
    main()
