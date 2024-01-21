"""Классическая игра Змейка (ver. 3.3).

В игре реализованы следующие возможности:
-отрисованы линии границ каждой ячейки игрового поля, с разлинееным полем игра
выглядит более привлекательно;
-смена цвета любого игрового объекта, поля и линий границ ячеек путём
переопределения констант;
-смена скорости движения змейки;
-включение/выключение неправильной еды.

Объявлены следующие классы, более подробное описание см. в классе:
-GameObject - базовый класс, родитель всех классов;
-Apple - класс яблока, родительский класс для класса неправильной еды;
-Snake - класс змейки;
-Wrong - класс неправильной еды.

Объявлены следующие функции:
-handle_keys - функция обработки действий пользователя (из прекода);
-draw_lines - отрисовывает горизонтальные и вертикальные линии на поле;
-print_game_over - выводит иформационные сообщения и итог игры в консоль;
-get_used_positions - получает список из кортежей занятых на поле позиций.

Прекод максимально не трогал. Объявил дополнительныеконстанты. По идее
код можно разнести по модулям, но не уверен, что это необходимо в
данном проекте.
"""

import pygame
from random import choice, randint
from typing import Optional
from snake_brain import SnakeBrain, NoCellException

# Инициализация PyGame
pygame.init()

# Константы для размеров
SCREEN_WIDTH: int = 640
SCREEN_HEIGHT: int = 480
GRID_SIZE: int = 20
GRID_WIDTH: int = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT: int = SCREEN_HEIGHT // GRID_SIZE

# Направления движения
UP: tuple = (0, -1)
DOWN: tuple = (0, 1)
LEFT: tuple = (-1, 0)
RIGHT: tuple = (1, 0)

# Словарь используется для смены движения змейки,
# в нём описаны все возможные изменения направления.
# (<нажатая кнопка>, <текущее направление>): <новое направление>
direction_dict: dict = {
    (pygame.K_UP, LEFT): UP,
    (pygame.K_UP, RIGHT): UP,
    (pygame.K_DOWN, LEFT): DOWN,
    (pygame.K_DOWN, RIGHT): DOWN,
    (pygame.K_LEFT, UP): LEFT,
    (pygame.K_LEFT, DOWN): LEFT,
    (pygame.K_RIGHT, UP): RIGHT,
    (pygame.K_RIGHT, DOWN): RIGHT,
}

# Это первая итерация моего кода по автозаполнению словаря с учётом движений
# в себя, оставил на память)
# key_d = [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]
# cur_d = [UP, DOWN, LEFT, RIGHT]
# for i in range(len(key_d)):
#     for j in range(len(cur_d)):
#         if cur_d[j] == (-cur_d[i][0], -cur_d[i][1]):
#             direction_dict[(key_d[i], cur_d[j])] =(-cur_d[i][0],-cur_d[i][1])
#         else:
#             direction_dict[(key_d[i], cur_d[j])] = cur_d[i]

# =====================================================================
# Ниже возможно переопределить константы
# Все цвета задаются кортежем в кодировке RGB: (R, G, B)

# Цвета фона - черный
BOARD_BACKGROUND_COLOR: tuple = (0, 0, 0)  # ТЗ, тёмная тема
# BOARD_BACKGROUND_COLOR = (200, 200, 200)  # Светлая тема

# Скорость движения змейки
SPEED: int = 20  # ТЗ
# SPEED = 12  # Альтернативный

# Цвет линий игрового поля
LINE_COLOR: tuple = (20, 20, 20)  # Тёмная тема
# LINE_COLOR = (120, 120, 120)  # Светлая тема

# Включить/выключить неправильную еду
WRONG_EAT: bool = True

# Цвет неправильной еды
WRONG_COLOR: tuple = (255, 255, 0)  # Тёмная тема
# WRONG_COLOR = (229, 230, 25)  # Светлая тема

# Цвет яблок
APPLE_COLOR: tuple = (255, 0, 0)  # ТЗ, тёмная тема
# APPLE_COLOR = (255, 20, 20)  # Светлая тема

# Цвет змейки
SNAKE_COLOR: tuple = (0, 255, 0)  # ТЗ, тёмная тема
# SNAKE_COLOR = (20, 50, 0)  # Светлая тема

# Цвет обводки/границы еды
FG_COLOR: tuple = (93, 216, 228)

# Для проверки столкновение змейки с собой при длине змейки более 3,
# т.к. при меньшей длине невозможно столкнуться с собой.
CHECKED_LENGTH: int = 3

# =====================================================================

# Настройка игрового окна
screen: pygame.surface.Surface = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
screen.fill(BOARD_BACKGROUND_COLOR)

# Заголовок окна игрового поля
pygame.display.set_caption('Змейка')

# Настройка времени
clock: pygame.time.Clock = pygame.time.Clock()


# Тут опишите все классы игры
class GameQuitError(Exception):
    """Класс для обработки исключения при закрытии окна игры."""

    def __str__(self) -> str:
        """Исключение по закрытию игры пользователем."""
        return 'Выход из игры по требованию пользователя.'


class NoDirectionError(Exception):
    """Класс для обработки исключения при смене направления движения змейки."""

    def __str__(self) -> str:
        """Исключение при невозможности сменить направление змейки."""
        return (
            'Невозможно сменить направление '
            'или нажата неподдерживаемая кнопка!'
        )


class GameObject:
    """Базовый класс игровых объектов GameObject."""

    # Цвет игрового объекта
    body_color: tuple = BOARD_BACKGROUND_COLOR

    def __init__(self):
        self.position = (
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2
        )

    def draw(self, surface, position=None,
             color=None, border_color=None) -> None:
        """Метод отрисовывает/закрашивает одну клетку на игровом поле.

        Пришлось унифицировать метод на все случаи жизни. При этом требуется
        минимум вводимых атрибутов, когда это возможно.

        Аргументы:
            surface (pygame.display): игровой экран.
            position (Optional[tuple]): координаты закрашиваемой ячейки
                игрового поля.
            color (Optional[tuple]): цвет закрашиваемой ячейки.
            border_color (Optional[tuple]): цвет границы ячейки.

        Возвращает:
            None.
        """
        # Определяю границы указанной ячейки, либо ячейки self.position
        if position:
            rect = pygame.Rect(
                (position[0], position[1]), (GRID_SIZE, GRID_SIZE)
            )
        else:
            rect = pygame.Rect(
                (self.position[0], self.position[1]), (GRID_SIZE, GRID_SIZE)
            )

        # Закрашиваю ячейку указанным цветом, либо цветом self.body_color
        if color:
            pygame.draw.rect(surface, color, rect)
        else:
            pygame.draw.rect(surface, self.body_color, rect)

        # Если требуется, закрашиваю границы ячейки
        if border_color:
            pygame.draw.rect(surface, border_color, rect, 1)


class Apple(GameObject):
    """Класс Apple, описывает яблоко и действия с ним.

    Данный класс является родителем для класса Wrong - класс неправильной еды.
    Содержит атрибуты и методы для яблока.
    """

    # Цвет яблока
    body_color = APPLE_COLOR

    def __init__(self, positions: list = []):
        super().__init__()
        self.randomize_position(positions)

    def randomize_position(self, positions: list = []) -> None:
        """Выбирает случайную не занятую ячейку на игровом поле."""
        # Выбираем свободную ячейку на поле
        while True:
            random_position: tuple = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            )
            if random_position not in positions:
                break
        self.position = random_position

        # # Для дебага
        # position = (0, 460)
        # if not isinstance(self, Wrong) and position not in positions:
        #     self.position = position


class Wrong(Apple):
    """Класс Wrong, описывает неправильную еду и действия с ней.

    Данный класс является дочерним классом Apple.
    """

    # Цвет неправильной еды
    body_color = WRONG_COLOR

    def __init__(self, positions: list = []):
        super().__init__(positions)


class Snake(GameObject):
    """Класс Snake, описывает змейку и её поведение.

    Содержит атрибуты и методы для змейки. Также добален новый метод
    downsizing() для уменьшения змейки в случае съедания неправильной еды.
    """

    # Цвет змейки
    body_color = SNAKE_COLOR

    def __init__(self) -> None:
        super().__init__()
        self.length: int = 1
        self.positions: list = [self.position]
        self.direction: tuple = RIGHT  # Так по ТЗ
        self.next_direction: Optional[tuple] = None
        self.last: Optional[tuple] = None
        # Змейка в порядке, она в игре
        self.in_game: bool = True

    def reset(self) -> None:
        """Сбрасывает змейку в начальное состояние."""
        self.length = 1
        self.positions = [self.position]
        self.direction = choice([RIGHT, LEFT, UP, DOWN])
        self.next_direction = None
        self.last = None
        self.in_game = True

    def update_direction(self) -> None:
        """Метод обновления направления после нажатия на кнопку."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self) -> None:
        """Обновляет позицию змейки на поле."""
        # Вычисляю новую позицию головы
        head: list = list(self.get_head_position())
        head[0] = (head[0] + self.direction[0] * GRID_SIZE) % SCREEN_WIDTH
        head[1] = (head[1] + self.direction[1] * GRID_SIZE) % SCREEN_HEIGHT

        # Добавляю новую голову
        self.positions.insert(0, tuple(head))

        # Обрабатываю хвост змейки
        if len(self.positions) - 1 >= self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self, surface, border_color):
        """Отрисовывает змейку."""
        # Если голова пройдет перпендикулярно к хвосту, и разминется
        # с ним буквально на фрейм, то затрется один блок, и будет черным.
        # Поэтому оставляю перерисовку всей змейки, с головой.
        for position in self.positions[:-1]:
            super().draw(surface, position,
                         self.body_color, border_color)

        # Отрисовка головы змейки
        super().draw(surface, self.positions[0], self.body_color, border_color)

        # Затирание последней ячейки
        if self.last:
            super().draw(surface, self.last,
                         BOARD_BACKGROUND_COLOR)

    def get_head_position(self) -> tuple:
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def downsizing(self, surface) -> None:
        """Убирает последний элемент змейки."""
        erase_position = self.positions.pop()
        self.length -= 1
        # Затираю последнюю ячейку
        super().draw(surface, erase_position,
                     color=BOARD_BACKGROUND_COLOR)


def handle_keys(game_object) -> None:
    """Обрабатывает действия пользователя по управлению змейкой."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            raise GameQuitError
        elif event.type == pygame.KEYDOWN:
            action = direction_dict.get((event.key, game_object.direction))
            if not action:
                raise NoDirectionError
            game_object.next_direction = action


def draw_lines() -> None:
    """Функция отрисовывает горизонтальные и вертикальные линии на поле."""
    # Горизонтальные линии.
    for i in range(1, GRID_HEIGHT):
        pygame.draw.line(
            screen,
            LINE_COLOR,
            (0, i * GRID_SIZE),
            (SCREEN_WIDTH, i * GRID_SIZE),
        )

    # Вертикальные линии.
    for i in range(1, GRID_WIDTH):
        pygame.draw.line(
            screen,
            LINE_COLOR,
            (i * GRID_SIZE, 0),
            (i * GRID_SIZE, SCREEN_HEIGHT),
        )


def print_game_over(snake_length: int) -> None:
    """Функция выводит в консоль информационные сообщения и длину змейки."""
    print(
        f'\nGAME OVER!'
        f'\nSnake length: {snake_length}'
        f'\nStart new game.'
    )


def get_used_positions(positions: list, *args: tuple) -> list:
    """Функция возвращает список из кортежей занятых позиций на поле."""
    return [*positions, *args]


def main():  # noqa: C901
    """Функция, которая управляет выполнением программы."""
    # Тут нужно создать экземпляры классов

    # Определяем основные игровые объекты
    snake = Snake()
    snake.draw(screen, border_color=FG_COLOR)
    apple = Apple(snake.positions)
    apple.draw(screen, border_color=FG_COLOR)

    # Добавляем при необходимости неправильную еду
    if WRONG_EAT:
        used_positions = get_used_positions(snake.positions,
                                            apple.position)
        wrong = Wrong(used_positions)
        wrong.draw(screen, border_color=FG_COLOR)

    print('\nStart new game.')

    # Определяем brain
    brain = SnakeBrain(snake, apple,
                       GRID_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT,
                       wrong)

    while True:
        # Устанавливаем скорость игры
        clock.tick(SPEED)

        # Обрабатываем действие пользователя
        try:
            handle_keys(snake)
            brain.next_step(snake, apple, wrong)
        except GameQuitError as e:
            print(e)
            pygame.quit()
            break
        except NoDirectionError as e:
            print(f'Ошибка: {e}')
        except NoCellException as e:
            print(e)

        # Перемещаю змейку
        snake.update_direction()
        snake.move()

        # Получаем занятые позиции на поле, чтобы там повторно не появилась еда
        if WRONG_EAT:
            used_positions = get_used_positions(snake.positions,
                                                apple.position,
                                                wrong.position)
        else:
            used_positions = get_used_positions(snake.positions,
                                                apple.position)

        # Проверяем, съела ли змейка яблоко и при необходимости
        # увеличиваем длину змейки и перемещаем яблоко.
        # Или проверяем, съела ли змейка несъедобную еду и при необходимости
        # уменьшаем длину змейки, перемещаем еду и перерисовываем хвост,
        # или змейка больше неиграбельна
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(used_positions)
            apple.draw(screen, border_color=FG_COLOR)
            brain.set_target(snake, apple, wrong)
        elif WRONG_EAT and snake.get_head_position() == wrong.position:
            if snake.length > 1:
                snake.downsizing(screen)
                wrong.randomize_position(used_positions)
                wrong.draw(screen, border_color=FG_COLOR)
                brain.food_scanner_up()
                brain.set_target(snake, apple, wrong)
            else:
                snake.in_game = False

        # Проверяем столкновение змейки с собой при длине змейки от 4,
        # т.к. при меньшей длине невозможно столкнуться.
        if (snake.length > CHECKED_LENGTH
                and snake.get_head_position()
                in snake.positions[CHECKED_LENGTH:]):
            snake.in_game = False

        # Если змейка неиграбельна, то сбрасываем игру
        if not snake.in_game:
            print_game_over(snake.length)
            screen.fill(BOARD_BACKGROUND_COLOR)
            snake.reset()
            apple.randomize_position(snake.positions)
            brain.reset(snake, apple, wrong)
            apple.draw(screen, border_color=FG_COLOR)

            # Если включена неправильная еда
            if WRONG_EAT:
                wrong.randomize_position(snake.positions)
                brain.reset(snake, apple, wrong)
                wrong.draw(screen, border_color=FG_COLOR)

            snake.in_game = True

        # Перерисовываю змейку
        snake.draw(screen, border_color=FG_COLOR)

        # Перерисовываю линии разметки поля и окно игры
        draw_lines()
        pygame.display.update()


if __name__ == '__main__':
    main()
