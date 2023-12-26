# snake_brain.py

"""Мозги Питона. (ver. 1.0)

Данный модуль описывает всё для самостоятельной охоты Змейки.
Основной код игры the_snake.py должен работать корректно, в основном
коде желательно наличие реализованного функционала неправильной еды
(по идее должен работать и без нее, но так не интересно, я не проверял).

Чтобы меньше заморачиваться при подключении к своему коду, методы
модуля принимают игровые объекты, соответствие параметров и функций
необходимо(!) проверить в методах __init__() и update().

В текущей версии Змейка определяет цель для охоты и старается двигаться
к неё по кратчайшей траектории, когда цель съедена Змейка определяет
новую цель и движется к ней. Если Змейка съела неправильную еду,
то она улучшает свой навык определения съедобной еды и в следующий раз
будет более аккуратно определять цель.
Если Змейка проиграла, то она начнёт игру снова с улучшенными навыками.

Как подключить:
-импортируем SnakeBrain, NoCellException. Исключение NoRouteException
    в текущей версии на моём коде основного приложения не происходит,
    оставлено для дебага;
-определяем экземпляр SnakeBrain после создания всех объектов и передаём
    созданные объекты:
        snake (экземпляр Змейки),
        apple (экземпляр Яблока),
        GRID_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT (константы из прекода)
        wrong (экземпляр неправильной еды);
-вместе, но желательно после handle_keys() активируем .next_step().
    Данный метод выбрасывает все исключения класса, нужно их обработать;
-при успешной проверке на съедение любой пищи активируем .set_target();
-при успешной проверке на съедение неправильной пищи дополнительно
    активируем .food_scanner_up();
-при проигрыше активируем .reset().
-наблюдаем и наслаждаемся)
"""

from random import choice
from typing import Optional

# Направления движения
UP: tuple = (0, -1)
DOWN: tuple = (0, 1)
LEFT: tuple = (-1, 0)
RIGHT: tuple = (1, 0)

# Словарь используется для пересчёта абсолютного направления движения
# в относительное: прямо, лево, право
# (<текущее направление>, <относит. направление>): <абсолютное направление>
# где: <относит. направление>: UP - прямо, LEFT и RIGHT соответственно
route_map: dict = {
    (RIGHT, UP): RIGHT,
    (RIGHT, LEFT): UP,
    (RIGHT, RIGHT): DOWN,
    (LEFT, UP): LEFT,
    (LEFT, LEFT): DOWN,
    (LEFT, RIGHT): UP,
    (UP, UP): UP,
    (UP, LEFT): LEFT,
    (UP, RIGHT): RIGHT,
    (DOWN, UP): DOWN,
    (DOWN, LEFT): RIGHT,
    (DOWN, RIGHT): LEFT,
}


class NoRouteException(Exception):
    """Класс для обработки исключения при отсутствии направления в route."""

    def __str__(self) -> str:
        """Исключение при отсутствии значения в route."""
        return (
            'brain: No route in route_map (dict)!'
        )


class NoCellException(Exception):
    """Класс для обработки исключения при отсутствии свободной ячейки."""

    def __str__(self) -> str:
        """Исключение при отсутствии свободной ячейки для движения."""
        return (
            'brain: There are no free cells for movement.'
        )


class SnakeBrain():
    """Класс реализует самостоятельное движение Змейки."""

    # Уровень пищевого сканера Змейки
    food_scanner: int = 1

    def __init__(self, snake, apple, grid_size, screen_width,
                 screen_height, wrong=None) -> None:
        """Инициализатор мозгов Змейки."""
        # Инициализация параметров экрана
        self._grid_size: int = grid_size
        self._screen_width: int = screen_width
        self._screen_height: int = screen_height

        # Инициализация Змеи
        self._snake_positions: list = snake.positions
        self._snake_direction: tuple = snake.direction
        self._snake_head = snake.get_head_position()

        # Инициализация яблока
        self._apple_position: tuple = apple.position

        # Инициализация неправильной еды
        if wrong:
            self._wrong: Optional[bool] = True
            self._wrong_position: tuple = wrong.position
        else:
            self._wrong = None

        # Установка цели охоты
        self.set_target(snake, apple, wrong)

        print(f'brain: Activate. Food scanner level {self.food_scanner}.')

    def update(self, snake, apple, wrong=None) -> None:
        """Обновление параметров игры."""
        # Обновление Змейки
        self._snake_positions = snake.positions
        self._snake_direction = snake.direction
        self._snake_head = snake.get_head_position()

        # Обновление яблока
        self._apple_position = apple.position

        # Обновление неправильной еды
        if wrong:
            self._wrong = True
            self._wrong_position = wrong.position
        else:
            self._wrong = None

    def set_target(self, snake, apple, wrong=None) -> None:
        """Устанавливает цель Змейке."""
        self.update(snake, apple, wrong)
        if self._wrong:
            target_list: list = [
                (self._apple_position) for _ in range(self.food_scanner)] + [
                    self._wrong_position]
        else:
            target_list = [self._apple_position]
        # print(target_list)

        # Выбираем случайную цель
        self.target = choice(target_list)
        # print(f'brain: Target position {self.target}')

    def reset(self, snake, apple, wrong=None) -> None:
        """Сбрасываем Змейку."""
        # self.food_scanner = 1
        self.set_target(snake, apple, wrong)
        self.update(snake, apple, wrong)

    def food_scanner_up(self) -> None:
        """Увеличивает уровень умственной активности Змейки."""
        self.food_scanner += 1
        print(f'brain: Ooops! Food scanner level up to {self.food_scanner}.')

    def _step_coord(self, head, direction) -> tuple:
        """Вычисляет координаты ячейки по направлению."""
        # Вычисляю новую позицию головы
        step: list = list(head)
        step[0] = (
            head[0] + direction[0] * self._grid_size) % self._screen_width
        step[1] = (
            head[1] + direction[1] * self._grid_size) % self._screen_height
        return tuple(step)

    def _get_possible_steps(self, head) -> set:
        """Определяет множество возможных для движения ячеек."""
        # Список всех направлений для следующего движения
        steps: list = []
        # Напавление прямо UP, влево LEFT, вправо RIGHT
        for current in [UP, LEFT, RIGHT]:
            direction = route_map.get((self._snake_direction, current))
            if direction is not None:
                steps.append(self._step_coord(head, direction))
            else:
                print(f'_snake_direction={self._snake_direction} '
                      f'current={current}')
                raise NoRouteException

        # print(f'steps={steps}')

        # Занятые ячейки на поле
        if self._wrong:
            used_positions: list = [*self._snake_positions,
                                    self._apple_position,
                                    self._wrong_position]
        else:
            used_positions = [*self._snake_positions,
                              self._apple_position]

        # Удаляем позицию цели из списка занятых позиций
        # print('apple=', self._apple_position, 'wrong=', self._wrong_position)
        # print(used_positions, self.target)
        used_positions.remove(self.target)

        # Список позиций, доступных для движения
        possible_steps: set = set(steps) - set(used_positions)
        if not possible_steps:
            raise NoCellException

        return possible_steps

    def next_step(self, snake, apple, wrong=None) -> None:
        """Определяет следующий шаг Змейки."""
        # Обновление параметров игрового поля
        self.update(snake, apple, wrong)

        # Список возможных для движения ячеек
        possible_steps: set = self._get_possible_steps(self._snake_head)

        # Логика выбора направления к цели
        # ТУТ МОЖНО ЧОЙС(поссиблстепс) и ниже уже НЕ [1:]будет
        next: tuple = tuple(possible_steps)[0]
        for step in list(possible_steps)[1:]:
            use_x: bool = (
                abs(step[0] - self.target[0]) < abs(next[0] - self.target[0])
            )
            use_y: bool = (
                abs(step[1] - self.target[1]) < abs(next[1] - self.target[1])
            )

            if any([use_x, use_y]):
                next = step

        # Координаты целевой ячейки для движения
        next_cell: list = list(next)

        # Разница между координатами в ячейках
        dx_cells = (next_cell[0] - self._snake_head[0]) // self._grid_size
        dy_cells = (next_cell[1] - self._snake_head[1]) // self._grid_size

        # Если змейка достигает границы, корректирую координаты
        grid_width = self._screen_width // self._grid_size
        grid_height = self._screen_height // self._grid_size

        if abs(dx_cells) == grid_width - 1:
            dx_cells //= -(grid_width - 1)

        if abs(dy_cells) == grid_height - 1:
            dy_cells //= -(grid_height - 1)

        # Направление
        direction = (dx_cells, dy_cells)

        # print(f'target={self.target} direction={tuple(direction)} '
        #       f'possible={possible_steps} next_cell={next_cell} '
        #       f'head={head}')
        snake.next_direction = tuple(direction)
