import os
import random
import re
from dataclasses import dataclass
from functools import partial
from random import sample

from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse
from kivy.graphics import Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.anchorlayout import AnchorLayout

Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'width', '640')
Config.set('graphics', 'height', '480')


@dataclass
class LotoData:
    players = ["Компьютер"]
    main = AnchorLayout()
    display = AnchorLayout()
    players_display = BoxLayout(
        orientation='horizontal', size_hint=(1, .75), height=100
    )
    play_display = FloatLayout()
    balls_display = BoxLayout(
        orientation='horizontal', center_x=0.5, center_y=0.5, size_hint=(1, 1)
    )
    balls_float_layout = FloatLayout(
        size_hint=(None, None)
    )
    bingo_balls = sample(range(1, 91), 90)
    bingo_balls.insert(0, '')
    ball_labels = []
    ball_nums = []
    game_ended = False


class Play(LotoData):

    def on_press_num(self, instance):
        if instance.text.isdigit() and int(instance.text) in self.ball_nums:
            instance.text = ''
            buttons = instance.parent.children
            label = instance.parent.parent.children[-1].text
            if not re.search(
                    r'[0-9]', ''.join([button.text for button in buttons])
            ):
                if self.game_ended:
                    return
                Clock.schedule_once(partial(self.end_game, winner=label), 0.1)

    def play_computer(self):
        player_grid_layout = self.players_display.children[1]
        label = player_grid_layout.children[-1].text
        if label == 'Игрок Компьютер':
            for card in player_grid_layout.children[:3]:
                for button in card.children:
                    button.trigger_action(0)

    def end_game(self, dt, winner):
        self.game_ended = True
        root_widget = App.get_running_app().root
        screenshot = Window.screenshot("screenshot.png")
        self.balls_float_layout.clear_widgets()

        root_widget.clear_widgets()

        container = BoxLayout(
            orientation='vertical', pos=(350, 600),
            size_hint=(.6, .3), spacing=10
        )

        label = Label(
            text=f"{winner} выиграл!", font_size=60,
            color=(1, 0, 0, 1), bold=True
        )

        with label.canvas.before:
            Color(1, 1, 1, 0.85)  # Цвет фона контейнера
            self.rect = Rectangle(
                pos=label.pos, size=(label.width, label.height)
            )

        label.bind(pos=lambda instance, value: setattr(self.rect, 'pos', value))
        label.bind(size=lambda instance, value: setattr(self.rect, 'size', value))

        image = Image(source=screenshot, allow_stretch=True, keep_ratio=True)

        root_widget.add_widget(image)
        container.add_widget(label)

        root_widget.add_widget(container)
        if os.path.exists(screenshot):
            os.remove(screenshot)


class Card(Play):
    @staticmethod
    def create_card():
        card = []
        numbers = random.sample(range(1, 91), 15)
        linings = [
            numbers[i:i + 5] for i in range(0, 15, 5)
        ]
        for line in linings:
            for index in random.sample(range(8), 3):
                line.insert(index, '')
            card.extend(line)
        return card

    def drawing_cards(self):
        for name in self.players:
            player_box_layout = BoxLayout(orientation='vertical')
            label_player = Label(
                text=f'Игрок {name}', size_hint=(1, 0.1),
                font_size=70, color=(0, 0, 0, 1), bold=True)
            player_box_layout.add_widget(label_player)

            for _ in range(3):
                cards_grid_layout = GridLayout(
                    rows=3, row_force_default=True, row_default_height=100,
                    col_force_default=True, col_default_width=110, padding=[50],size_hint=(0.5, 1),
                )
                card = self.create_card()
                for x in card:
                    button = Button(
                        text=str(x), on_press=self.on_press_num,
                        background_color=(1, 0.2, 0.5, 0.7), bold=True,
                        size_hint=(0.01, 0.01),
                    )
                    cards_grid_layout.add_widget(button)
                player_box_layout.add_widget(cards_grid_layout)

            self.players_display.add_widget(player_box_layout)


from kivy.uix.boxlayout import BoxLayout


class Balls(Play):

    def drawing_balls(self):
        scroll_view = ScrollView(size_hint=(1, 1))
        Clock.schedule_interval(self.show_next_ball, 3.5)
        scroll_view.add_widget(self.balls_float_layout)

        pause_button_layout = BoxLayout(
            orientation='horizontal', size_hint=(1, 1),
            pos_hint={'x': 0.3, 'y': 0.1}, padding=[200, 10, 600, 10], spacing=10
        )

        pause_button = Button(
            text="Пауза", font_size=30, size_hint=(0.1, 0.05),
            pos_hint={'x': 0.8, 'y': 0.8},
            background_color=(0.2, 0.2, 0.8, 1), background_normal='',
            on_press=self.pause_game, bold=True
        )
        pause_button_layout.add_widget(pause_button)

        self.balls_display.clear_widgets()
        self.balls_display.add_widget(pause_button_layout)
        self.balls_display.add_widget(scroll_view)
        self.play_display.add_widget(self.balls_display)

    def show_next_ball(self, dt):
        if self.bingo_balls:
            num = self.bingo_balls.pop(0)
            is_empty_ball = (num == '')
            ball_widget = BallWidget(number=num, is_empty=is_empty_ball)
            self.ball_labels.append(ball_widget)
            self.ball_nums.append(num)
            self.balls_float_layout.add_widget(ball_widget)

            for i, ball_widget in enumerate(
                    self.balls_float_layout.children[:-1], start=1
            ):
                ball_widget.move(100 + i, 0)

            self.play_computer()


class BallWidget(Widget):
    def __init__(self, number, is_empty=False, **kwargs):
        super().__init__(**kwargs)
        self.circle = None
        self.color_instruction = None
        self.label = None
        self.number = number
        self.is_empty = is_empty
        self.size_hint = (None, None)
        self.color = self.generate_random_color()
        self.draw_circle()
        self.draw_number()
        self.start_blinking()

    def draw_circle(self):
        self.canvas.clear()
        with self.canvas:
            self.color_instruction = Color(*self.color)
            self.circle = Ellipse(pos=self.pos)

    def update_color(self, *args):
        self.color_instruction.rgba = self.generate_random_color()
        self.label.text = str(random.randint(1, 90))

    def start_blinking(self):
        if self.is_empty:
            anim = Animation(duration=2.)
            anim += Animation(duration=2.)
            anim.bind(on_progress=self.update_color)
            anim.repeat = True
            anim.start(self)
            anim.start(self.circle)

    def draw_number(self):
        self.label = Label(
            text=str(self.number), font_size=40, center=self.center, bold=True
        )
        self.add_widget(self.label)

    @staticmethod
    def generate_random_color():
        r = random.random()
        g = random.random()
        b = random.random()
        return r, g, b, 1.0

    def move(self, x, y):
        anim = Animation(pos=(self.pos[0] + x, self.pos[1] + y), duration=0.2)
        anim.start(self)
        anim.start(self.label)
        anim.start(self.circle)


class MyTextInput(TextInput):
    def insert_text(self, substring, from_undo=False):
        new_text = self.text + substring
        if len(new_text) > 23:
            substring = substring[:10 - len(self.text)]
        return super(MyTextInput, self).insert_text(substring, from_undo)


class LotoApp(App, Balls, Card):
    name = MyTextInput(font_size=50)
    image = Image(source='index.jpg', allow_stretch=True, keep_ratio=False)

    def build(self):
        root_layout = RelativeLayout()
        root_layout.add_widget(self.image)

        input_layout = BoxLayout(
            orientation='vertical', pos=(720, 450),
            size_hint=(.3, .3), spacing=30
        )
        label = Label(
            text="Добро пожаловать в игру", font_size=60,
            size_hint=(1, 1), color=(1, 0, 0, 1), bold=True
        )
        input_layout.add_widget(label)
        label = Label(
            text="ЛОТО", font_size=60,
            size_hint=(1, 1), color=(1, 0, 0, 1), bold=True
        )
        input_layout.add_widget(label)
        label = Label(
            text="Введите свое имя", font_size=40,
            size_hint=(1, 1), color=(0, 0, 0, 1), bold=True
        )
        input_layout.add_widget(label)

        self.name.size_hint = (1, 1)
        input_layout.add_widget(self.name)

        button = Button(
            text="Начать игру!", font_size=40, size_hint=(1, 1),
            background_color=(1, 0.02, 0.17, 1), background_normal='',
            on_press=self.loto_game, bold=True
        )
        input_layout.add_widget(button)

        root_layout.add_widget(input_layout)
        self.main.add_widget(root_layout)
        return self.main

    def loto_game(self, instance):
        self.paused = False
        root_widget = App.get_running_app().root
        root_widget.bind(on_touch_down=self.on_touch_down)
        root_widget.clear_widgets()

        self.players.append(self.name.text)
        self.play_display.add_widget(
            Image(source='on.jpg', allow_stretch=True, keep_ratio=False)
        )

        self.drawing_cards()
        self.drawing_balls()

        self.play_display.add_widget(self.players_display)
        self.display.add_widget(self.play_display)
        root_widget.add_widget(self.display)

    def pause_game(self, instance):
        self.paused = not self.paused
        if self.paused:
            Clock.unschedule(self.show_next_ball)
        else:
            Clock.schedule_interval(self.show_next_ball, 3.5)
        popup = Popup(
            title='Пауза',
            content=Label(text='Для продолжения коснитесь дважды'),
            size_hint=(None, None),
            auto_dismiss=True
        )
        popup.open()

    def on_touch_down(self, instance, touch):
        if self.paused:
            self.paused = False
            Clock.schedule_interval(self.show_next_ball, 3.5)


if __name__ == '__main__':
    LotoApp().run()
