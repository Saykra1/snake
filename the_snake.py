"""Игра «Изгиб Питона» — классическая «Змейка» на Pygame."""

from random import choice

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Центральная точка экрана — стартовая позиция объектов:
SCREEN_CENTER = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))

# Все ячейки игрового поля (координаты левых верхних углов):
ALL_CELLS = {
    (x * GRID_SIZE, y * GRID_SIZE)
    for x in range(GRID_WIDTH)
    for y in range(GRID_HEIGHT)
}

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
DIRECTIONS = (UP, DOWN, LEFT, RIGHT)

# Новое направление по паре (клавиша, текущее направление).
# Разворот на 180 градусов в словарь не входит, поэтому невозможен.
TURNS = {
    (pygame.K_UP, LEFT): UP,
    (pygame.K_UP, RIGHT): UP,
    (pygame.K_DOWN, LEFT): DOWN,
    (pygame.K_DOWN, RIGHT): DOWN,
    (pygame.K_LEFT, UP): LEFT,
    (pygame.K_LEFT, DOWN): LEFT,
    (pygame.K_RIGHT, UP): RIGHT,
    (pygame.K_RIGHT, DOWN): RIGHT,
}

# Голова может столкнуться только с сегментом, индекс которого не меньше
# этого значения: на сетке нельзя вернуться в клетку быстрее, чем за 4 хода.
SELF_BITE_MIN_INDEX = 4

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Шаблон заголовка окна с рекордом:
CAPTION_TEMPLATE = 'Змейка | Рекорд: {record} | Выход: Esc'

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс игровых объектов: позиция и цвет."""

    def __init__(self, position=SCREEN_CENTER, body_color=None):
        """Задаёт позицию и цвет объекта."""
        self.position = position
        self.body_color = body_color

    def draw(self):
        """Отрисовывает объект. Переопределяется в дочерних классах."""
        pass

    def draw_cell(self, position, color=None, border=True):
        """Закрашивает одну ячейку поля цветом объекта или заданным."""
        rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, color or self.body_color, rect)
        if border:
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Яблоко, которое появляется в случайной свободной ячейке."""

    def __init__(self, occupied_cells=(), body_color=APPLE_COLOR):
        """Задаёт цвет яблока и ставит его в свободную ячейку."""
        super().__init__(body_color=body_color)
        self.randomize_position(occupied_cells)

    def randomize_position(self, occupied_cells=()):
        """Перемещает яблоко в случайную ячейку, не занятую змейкой."""
        self.position = choice(tuple(ALL_CELLS - set(occupied_cells)))

    def draw(self):
        """Отрисовывает яблоко."""
        self.draw_cell(self.position)


class Snake(GameObject):
    """Змейка: список сегментов, движение и рост."""

    def __init__(self, body_color=SNAKE_COLOR):
        """Задаёт цвет змейки и начальное состояние (движение вправо)."""
        super().__init__(body_color=body_color)
        self.reset(RIGHT)

    def reset(self, direction=None):
        """Возвращает змейку в начальное состояние: одна голова в центре.

        Если направление не передано, оно выбирается случайно.
        """
        self.length = 1
        self.positions = [self.position]
        self.direction = direction or choice(DIRECTIONS)
        self.next_direction = None
        self.last = None

    def update_direction(self):
        """Применяет направление, выбранное нажатием клавиши."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def move(self):
        """Сдвигает змейку на одну ячейку, проходя сквозь края поля."""
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction
        self.positions.insert(0, (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT,
        ))
        self.last = (
            self.positions.pop() if len(self.positions) > self.length
            else None
        )

    def has_bitten_itself(self):
        """Проверяет, столкнулась ли голова змейки с её телом."""
        return (
            self.get_head_position()
            in self.positions[SELF_BITE_MIN_INDEX:]
        )

    def draw(self):
        """Затирает след хвоста и дорисовывает новую голову."""
        # Сначала затираем хвост: голова могла занять его ячейку.
        if self.last:
            self.draw_cell(self.last, BOARD_BACKGROUND_COLOR, border=False)
        self.draw_cell(self.get_head_position())


def handle_keys(game_object):
    """Обрабатывает закрытие окна, Esc и клавиши-стрелки."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            pygame.quit()
            raise SystemExit
        if event.type == pygame.KEYDOWN:
            game_object.next_direction = TURNS.get(
                (event.key, game_object.direction),
                game_object.next_direction,
            )


def main():
    """Запускает игру и выполняет основной игровой цикл."""
    # Инициализация PyGame:
    pygame.init()
    snake = Snake()
    apple = Apple(snake.positions)
    record = snake.length
    pygame.display.set_caption(CAPTION_TEMPLATE.format(record=record))
    screen.fill(BOARD_BACKGROUND_COLOR)

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)
            if snake.length > record:
                record = snake.length
                pygame.display.set_caption(
                    CAPTION_TEMPLATE.format(record=record)
                )
        elif snake.has_bitten_itself():
            snake.reset()
            apple.randomize_position(snake.positions)
            screen.fill(BOARD_BACKGROUND_COLOR)

        snake.draw()
        apple.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
