"""Классическая игра Змейка.

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

# Инициализация PyGame
pygame.init()

# Константы для размеров
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# =====================================================================
# Ниже возможно переопределить константы
# Все цвета задаются кортежем в кодировке RGB: (R, G, B)

# Цвета фона - черный
BOARD_BACKGROUND_COLOR = (0, 0, 0)  # ТЗ, тёмная тема
# BOARD_BACKGROUND_COLOR = (200, 200, 200)  # Светлая тема

# Скорость движения змейки
SPEED = 20  # ТЗ
# SPEED = 12  # Альтернативный

# Цвет линий игрового поля
LINE_COLOR = (20, 20, 20)  # Тёмная тема
# LINE_COLOR = (120, 120, 120)  # Светлая тема

# Включить/выключить неправильную еду
WRONG_EAT = True

# Цвет неправильной еды
WRONG_COLOR = (255, 255, 0)  # Тёмная тема
# WRONG_COLOR = (229, 230, 25)  # Светлая тема

# Цвет яблок
APPLE_COLOR = (255, 0, 0)  # ТЗ, тёмная тема
# APPLE_COLOR = (255, 20, 20)  # Светлая тема

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)  # ТЗ, тёмная тема
# SNAKE_COLOR = (20, 50, 0)  # Светлая тема

# =====================================================================

# Настройка игрового окна
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
screen.fill(BOARD_BACKGROUND_COLOR)

# Заголовок окна игрового поля
pygame.display.set_caption('Змейка')

# Настройка времени
clock = pygame.time.Clock()


# Тут опишите все классы игры
class GameObject:
    """Базовый класс GameObject, от которого наследуются другие
    игровые объекты. Содержит общие атрибуты игровых объектов и
    заготовку метода для отрисовки объекта на игровом поле — draw.
    """

    # Задаю по умолчанию
    body_color: Optional[tuple] = None

    def __init__(self):
        self.position = (
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2
        )

    def draw(self) -> None:
        """Абстрактный метод, для дочерних классов."""
        pass


class Apple(GameObject):
    """Класс Apple, описывает яблоко и действия с ним.
    Данный класс является родителем для класса Wrong - класс неправильной еды.
    Содержит атрибуты и методы для яблока.
    """

    # Цвет яблока
    body_color: tuple = APPLE_COLOR

    def __init__(self):
        super().__init__()
        self.position = self.randomize_position()

    def randomize_position(self, positions: list = []) -> tuple:
        """Выбирает случайную не занятую ячейку на игровом поле."""
        # Выбираем свободную ячейку на поле
        while True:
            rnd_position: tuple = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            )
            if rnd_position not in positions:
                break
        return rnd_position

    # Метод draw класса Apple, из прекода
    def draw(self, surface):
        """Отрисовывает яблоко на игровом экране."""
        rect = pygame.Rect(
            (self.position[0], self.position[1]),
            (GRID_SIZE, GRID_SIZE)
        )
        pygame.draw.rect(surface, self.body_color, rect)
        pygame.draw.rect(surface, (93, 216, 228), rect, 1)


class Wrong(Apple):
    """Класс Wrong, описывает неправильную еду и действия с ней.
    Данный класс является дочерним классом Apple.
    """

    # Цвет неправильной еды
    body_color: tuple = WRONG_COLOR

    def __init__(self):
        super().__init__()


class Snake(GameObject):
    """Класс Snake, описывает змейку и её поведение.
    Содержит атрибуты и методы для змейки. Также добален новый метод
    downsizing() для уменьшения змейки в случае съедания неправильной еды.
    """

    # Цвет змейки
    body_color: tuple = SNAKE_COLOR

    def __init__(self):
        super().__init__()
        # Сбрасываем змейку в первоначальное значение
        self.reset()

    def reset(self) -> None:
        """Сбрасывает змейку в начальное состояние."""
        self.length: int = 1
        self.positions: list = [self.position]
        self.direction: tuple = choice([RIGHT, LEFT, UP, DOWN])
        self.next_direction: Optional[tuple] = None
        self.last: Optional[tuple] = None

        # Змейка в порядке, она в игре
        self.isgame: bool = True

    def update_direction(self) -> None:
        """Метод обновления направления после нажатия на кнопку."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self) -> None:
        """Обновляет позицию змейки на поле."""
        # Обрабатываем позицию головы змейки с целью получить следующую
        # относительную позицию на поле (в ячейках окна)
        head = [coord // GRID_SIZE for coord in self.get_head_position()]
        if self.direction[0]:  # LEFT or RIGHT
            head[0] += self.direction[0]
            if head[0] < 0:
                head[0] = GRID_WIDTH - 1
            elif head[0] >= GRID_WIDTH:
                head[0] = 0
        else:  # UP or DOWN
            head[1] += self.direction[1]
            if head[1] < 0:
                head[1] = GRID_HEIGHT - 1
            elif head[1] >= GRID_HEIGHT:
                head[1] = 0

        # Получаем абсолютную позицию на поле (в пикселях окна)
        head = [grid * GRID_SIZE for grid in head]
        # Добавляем новую голову
        self.positions.insert(0, tuple(head))

        # Обрабатываем хвост змейки
        if len(self.positions) - 1 >= self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    # Метод draw класса Snake, из прекода
    def draw(self, surface):
        """Отрисовывает змейку."""
        for position in self.positions[:-1]:
            rect = (
                pygame.Rect((position[0], position[1]), (GRID_SIZE, GRID_SIZE))
            )
            pygame.draw.rect(surface, self.body_color, rect)
            pygame.draw.rect(surface, (93, 216, 228), rect, 1)

        # Отрисовка головы змейки
        head = self.positions[0]
        head_rect = pygame.Rect((head[0], head[1]), (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, self.body_color, head_rect)
        pygame.draw.rect(surface, (93, 216, 228), head_rect, 1)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pygame.Rect(
                (self.last[0], self.last[1]),
                (GRID_SIZE, GRID_SIZE)
            )
            pygame.draw.rect(surface, BOARD_BACKGROUND_COLOR, last_rect)

    def get_head_position(self) -> tuple:
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def downsizing(self):
        """Убирает последний элемент змейки."""
        self.last = self.positions.pop()
        self.length -= 1


# Функция обработки действий пользователя, из прекода
def handle_keys(game_object) -> None:
    """Обрабатывает действия пользователя по управлению змейкой."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


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


def get_used_positions(positions, *args) -> list:
    """Функция возвращает список из кортежей занятых позиций на поле."""
    return positions + [position for position in args]


def main():
    """Функция, которая управляет выполнением программы."""
    # Тут нужно создать экземпляры классов

    # Определяем основные игровые объекты
    snake = Snake()
    apple = Apple()
    apple.draw(screen)

    # Добавляем при необходимости неправильную еду
    if WRONG_EAT:
        wrong = Wrong()
        wrong.draw(screen)

    print('\nStart new game.')

    while True:
        clock.tick(SPEED)

        # Тут опишите основную логику игры
        # Обрабатываем действия пользователя и/или перемещаем змейку
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        # Перерисовываем змейку
        snake.draw(screen)

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
            apple.position = apple.randomize_position(used_positions)
            apple.draw(screen)
        elif WRONG_EAT and snake.get_head_position() == wrong.position:
            if snake.length > 1:
                snake.downsizing()
                snake.draw(screen)
                wrong.position = wrong.randomize_position(used_positions)
                wrong.draw(screen)
            else:
                snake.isgame = False

        # Проверяем столкновения змейки с собой при длине змейки от 4,
        # т.к. при меньшей длине невозможно столкнуться.
        if (snake.length > 3
                and snake.get_head_position() in snake.positions[3:]):
            snake.isgame = False

        # Если змейка неиграбельна, то сбрасываем игру
        if not snake.isgame:
            print_game_over(snake.length)
            screen.fill(BOARD_BACKGROUND_COLOR)
            snake.reset()
            apple.position = apple.randomize_position(snake.positions)
            apple.draw(screen)

            # Если включена неправильная еда
            if WRONG_EAT:
                wrong.position = wrong.randomize_position(snake.positions)
                wrong.draw(screen)

            snake.isgame = True

        # Перерисовываем линии разметки поля и окно игры
        draw_lines()
        pygame.display.update()


if __name__ == '__main__':
    main()
