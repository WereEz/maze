import copy

from maze import find_way, generate, generation_entries, start_wave


def test_generate_no_cycles():
    maze = generate(10, 10)
    # падение
    # maze = [
    #    [-1, -1, -1, -1, -1],
    #    [-1, 0, 0, 0, -1],
    #    [-1, 0, -1, 0, -1],
    #    [-1, 0, 0, 0, -1],
    #    [-1, -1, -1, -1, -1]
    # ]
    # Check that there are no cycles in the maze
    visited = [[False for _ in range(len(maze[0]))] for _ in range(len(maze))]
    stack = [(1, 1)]
    while stack:
        x, y = stack.pop()
        if visited[x][y]:
            assert False, "Лабиринт имеет цикл"
        visited[x][y] = True
        if maze[x][y+1] != -1 and not visited[x][y+1]:
            stack.append((x, y+1))
        if maze[x][y-1] != -1 and not visited[x][y-1]:
            stack.append((x, y-1))
        if maze[x+1][y] != -1 and not visited[x+1][y]:
            stack.append((x+1, y))
        if maze[x-1][y] != -1 and not visited[x-1][y]:
            stack.append((x-1, y))


def test_generate_no_unreachable_areas():
    maze = generate(10, 10)
    # падение
    # maze = [
    #    [-1, -1, -1, -1, -1],
    #    [-1, 0, -1, 0, -1],
    #    [-1, 0, -1, 0, -1],
    #    [-1, 0, -1, 0, -1],
    #    [-1, -1, -1, -1, -1]
    # ]
    # Check that there are no unreachable areas in the maze
    visited = [[False for _ in range(len(maze[0]))] for _ in range(len(maze))]
    stack = [(1, 1)]
    while stack:
        x, y = stack.pop()
        visited[x][y] = True
        if maze[x][y+1] != -1 and not visited[x][y+1]:
            stack.append((x, y+1))
        if maze[x][y-1] != -1 and not visited[x][y-1]:
            stack.append((x, y-1))
        if maze[x+1][y] != -1 and not visited[x+1][y]:
            stack.append((x+1, y))
        if maze[x-1][y] != -1 and not visited[x-1][y]:
            stack.append((x-1, y))
    for i in range(len(visited)):
        for j in range(len(visited[0])):
            if maze[i][j] == 0 and not visited[i][j]:
                assert False, "Лабиринт имеет недоступные зоны"


def test_generation_entries():
    maze = [
        [-1, -1, -1, -1, -1],
        [-1, 0, -1, 0, -1],
        [-1, 0, -1, 0, -1],
        [-1, 0, 0, 0, -1],
        [-1, -1, -1, -1, -1]
    ]
    start, end = generation_entries(maze)
    width = len(maze[0])
    height = len(maze)
    if start == end:
        assert False, "Начало и конец совпали"
    pos = [start, end]
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
            assert False, "Вход/выход огорожен стенами с трех сторон"


def test_find_way():
    maze = generate(10, 10)
    start, end = generation_entries(maze)
    maze[start[0]][start[1]] = 0
    maze[end[0]][end[1]] = 0
    maze_lee = copy.deepcopy(maze)
    maze_lee = start_wave(maze_lee, start, end)
    way = find_way(maze_lee, start, end)
    if start not in way or end not in way:
        assert False, "Входа/ выхода нет в пути"
    print(start, end)
    for i in range(21):
        print(maze[i])
    for cell in way:
        print(cell)
        if maze[cell[0]][cell[1]] == -1:
            assert False, "Алгоритм поиска сломал стену"
