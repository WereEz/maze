"""Модуль с генерацией лабиринта и решения"""
import random
from PIL import Image, ImageDraw


def can_build_wall(maze: list[list], row: int, ind: int,
                   current_row: list[int]) -> bool:
    """
    Проверяет можно ли построить нижнюю стену
        :param maze: лабиринт
        :param row: номер строки
        :param ind: индекс элемента
        :param current_row: текущая строка генерации
        :return: True если можно иначе False
    """
    elem = current_row[ind]
    for i in range(ind+1, len(current_row)):
        if elem == current_row[i]:
            return True
    for i in range(ind-1, -1, -1):
        if elem == current_row[i] and maze[row * 2 + 2][i * 2 + 1] == 0:
            return True
    return False


def generate(width: int, height: int,
             chance_r: int = 50, chance_b: int = 50) -> list[list]:
    """
    Генерирует лабиринт используя алгоритм Эйлера
        :param width: ширина
        :param height: высота
        :param chance_r: шанс правой стены
        :param chance_b: шанс нижней стены
        :return: 2D список из -1 и 0 где -1 это стена, а 0 дорожка
    """
    output_height = height * 2 + 1
    output_width = width * 2 + 1
    maze = [[-1 for i in range(output_width)] for j in range(output_height)]
    for i in range(1, output_height-1):
        if i % 2 == 1:
            maze[i][1:-1] = [0 for j in range(1, output_width-1)]
        else:
            maze[i][1:-1:2] = [0 for j in range(1, output_width-1, 2)]
    current_row = [0] * width
    set_step = 1
    for i in range(height):
        for j in range(width):
            if current_row[j] == 0:
                current_row[j] = set_step
                set_step += 1
        # Стены справа
        for j in range(width - 1):
            create_wall = 1 if random.randint(1, 100) <= chance_r else 0

            if create_wall == 1 or current_row[j] == current_row[j + 1]:
                maze[i * 2 + 1][j * 2 + 2] = -1
            else:
                changing = current_row[j + 1]
                for k in range(width):
                    if current_row[k] == changing:
                        current_row[k] = current_row[j]
        # Стены снизу
        for j in range(width):
            create_wall = 1 if random.randint(1, 100) <= chance_b else 0
            if create_wall == 1 and can_build_wall(maze, i, j, current_row):
                maze[i * 2 + 2][j * 2 + 1] = -1
        if i != height - 1:
            for j in range(width):
                if maze[i * 2 + 2][j * 2 + 1] == -1:
                    current_row[j] = 0
    for j in range(width - 1):
        if current_row[j] != current_row[j + 1]:
            maze[-2][j * 2 + 2] = 0
            changing = current_row[j + 1]
            for k in range(width):
                if current_row[k] == changing:
                    current_row[k] = current_row[j]
    return maze


def start_wave(maze: list[list], start_pos: list[tuple[int, int]],
               end_pos: list[tuple[int, int]]) -> list[list]:
    """
    Запуск волны по алгоритму Ли
        :param maze: лабиринт
        :param start_pos: стартовая позиция
        :param end_pos: конечная позиция
        :return: 2D список
    """
    maze[start_pos[0]][start_pos[1]] = "0"
    maze[end_pos[0]][end_pos[1]] = 0
    curr_step = [start_pos]
    dist = 1
    width = len(maze[0])
    height = len(maze)
    while curr_step and maze[end_pos[0]][end_pos[1]] == 0:
        next_step = []
        for cell in curr_step:
            row = cell[0]
            col = cell[1]

            if 0 <= row-1 < height and maze[row-1][col] == 0:
                maze[row-1][col] = dist
                next_step.append([row-1, col])
            if 0 <= row+1 < height and maze[row+1][col] == 0:
                maze[row+1][col] = dist
                next_step.append([row+1, col])
            if 0 <= col-1 < width and maze[row][col-1] == 0:
                maze[row][col-1] = dist
                next_step.append([row, col-1])
            if 0 <= col+1 < width and maze[row][col+1] == 0:
                maze[row][col+1] = dist
                next_step.append([row, col+1])
        dist += 1
        curr_step = next_step
    maze[start_pos[0]][start_pos[1]] = 1
    return maze


def save_txt(maze: list[list], path: str = "maze.txt") -> None:
    """
    Сохранение лабиринта в тхт файл
        :param maze: лабиринт
        :param path: имя файла
    """
    maze_copy = [
        [-1 for i in range(len(maze[0]))] for j in range(len(maze))]
    for i in range(len(maze)):
        for j in range(len(maze[0])):
            if maze[i][j] != -1:
                maze_copy[i][j] = 0
    with open(path, "w", encoding="UTF-8") as file:
        for i in range(len(maze)):
            file.write(' '.join(map(str, maze_copy[i])))
            if i != len(maze) - 1:
                file.write("\n")


def load_maze_from_txt(path: str = "maze.txt") -> list[list]:
    """
    Загрузка лабиринта из txt
        :param path: имя файла
        :return: 2D список
    """
    maze = []
    with open(path, "r", encoding="UTF-8") as file:
        for line in file:
            maze.append(list(map(int, line.split(sep=" "))))
    return maze


def find_way(maze: list[list], start_pos: list[tuple[int, int]],
             end_pos: list[tuple[int, int]]) -> list[list[int, int]]:
    """
    Поиск пути после прохождения волны
        :param maze: лабиринт
        :param start_pos: стартовая позиция
        :param end_pos: конечная позиция
        :return: список точек пути
    """
    maze[start_pos[0]][start_pos[1]] = 0
    way = []
    curr = end_pos
    width = len(maze[0])
    height = len(maze)
    while curr != start_pos:
        way.append(curr)
        row = curr[0]
        col = curr[1]
        if 0 <= row - 1 < height and maze[row][col] - 1 == maze[row-1][col]:
            curr = [row - 1, col]
        elif 0 <= row + 1 < height and maze[row][col] - 1 == maze[row+1][col]:
            curr = [row + 1, col]
        elif 0 <= col - 1 < width and maze[row][col] - 1 == maze[row][col-1]:
            curr = [row, col - 1]
        elif 0 <= col + 1 < width and maze[row][col] - 1 == maze[row][col+1]:
            curr = [row, col + 1]
    way.append(curr)
    return way


def save_image(maze: list[list], filename: str = "maze.jpg") -> None:
    """
    Сохранение лабиринта как изображение
        :param maze: лабиринт
        :param path: путь файла
    """
    cell_size = 10
    image_width = len(maze[0]) * cell_size
    image_height = len(maze) * cell_size
    image = Image.new('RGB', (image_width, image_height), color='white')
    for row in range(len(maze)):
        for col in range(len(maze[0])):
            if maze[row][col] == -1:
                x_1 = col * cell_size
                y_1 = row * cell_size
                x_2 = x_1 + cell_size
                y_2 = y_1 + cell_size
                image_draw = ImageDraw.Draw(image)
                image_draw.rectangle((x_1, y_1, x_2, y_2), fill='black')
    image.save(filename)


def calculate_square_size(path_to_file: str) -> int:
    """
    СЧитаем размер клетки лабиринта в пикселях изображения
        :param path_to_file: путь к файлу
        :return: число пикселей в клетке лабиринта
    """
    with Image.open(path_to_file) as img:
        width, height = img.size
        for i in range(width):
            for j in range(height):
                if img.getpixel((i, j))[0] > 128:
                    diagonal = ((i ** 2 + j ** 2) ** 0.5)
                    square_size = int(diagonal / (2 ** 0.5))
                    return square_size


def load_maze_from_img(path_to_file: str = "maze.jpg") -> list[list]:
    """
    Загрузка лабиринта из изображения
        :param path: путь файла
        :return: 2D список
    """
    with Image.open(path_to_file) as img:
        maze = []

        square_size = calculate_square_size(path_to_file)
        for i in range(0, img.size[1], square_size):
            row = []
            for j in range(0, img.size[0], square_size):
                square = img.crop((j, i, j + square_size, i + square_size))
                color = sorted(square.getcolors(),
                               key=lambda x: x[0], reverse=True)[0][1]
                if (0, 0, 0) == color:
                    row.append(-1)
                else:
                    row.append(0)
            maze.append(row)

    return maze


def generation_entries(maze: list[list]) -> list[list[int, int]]:
    """
    Генерирует вход и выход лабиринта
        :param maze: лабиринт
        :return: две точки
    """
    done = False
    width = len(maze[0])
    height = len(maze)
    borders = []
    for i in range(1, height-1):
        borders.append([i, 0])
        borders.append([i, width-1])
    for i in range(1, width-1):
        borders.append([0, i])
        borders.append([height-1, i])
    while not done:
        start_pos = random.choice(borders)
        end_pos = random.choice(borders)
        if start_pos != end_pos:
            done = True
            pos = []
            pos.append(start_pos.copy())
            pos.append(end_pos.copy())
            for point in pos:
                if point[0] == 0:
                    point[0] += 1
                elif point[0] == height-1:
                    point[0] -= 1
                elif point[1] == 0:
                    point[1] += 1
                elif point[1] == width-1:
                    point[1] -= 1
                if maze[point[0]][point[1]] == -1:
                    done = False
    return start_pos, end_pos
