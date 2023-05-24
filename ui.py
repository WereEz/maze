"""Модуль с интерфейсом"""
from maze import (find_way, generate, generation_entries, load_maze_from_img,
                  load_maze_from_txt, save_image, save_txt, start_wave)
import enum
import sys
from PyQt5.QtGui import QColor
from PyQt5 import uic, QtTest
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (QApplication, QGraphicsScene,
                             QGraphicsRectItem, QFileDialog)


class Pages(enum.Enum):
    """Перечисление страниц ui"""
    MENU = 0
    """Страница с меню"""
    MAZE = 1
    """Страница с лабиринтом"""


class Window():
    def __init__(self, parent=None):
        """Инициализует окно ui"""
        self.maze = None
        self.find = False
        self.draw = False
        self.start = None
        self.end = None
        self.way = False
        self.ui = uic.loadUi('des.ui')
        self.ui.view.setScene(QGraphicsScene())
        self.ui.show()
        self.ui.btn_start.clicked.connect(self.check_parameters)
        self.ui.btn_menu.clicked.connect(self.return_menu)
        self.ui.btn_save_txt.clicked.connect(self.save_maze_as_txt)
        self.ui.btn_save_img.clicked.connect(self.save_maze_as_img)
        self.ui.btn_load.clicked.connect(self.load_maze)
        self.ui.btn_find_way.clicked.connect(self.wave_expansion)

    def check_parameters(self):
        """Проверяет параметры будущего лабиринта"""
        if self.maze is not None:
            self.ui.field_errors.setText("")
            self.ui.stackedWidget.setCurrentIndex(Pages.MAZE.value)
            self.draw_maze()
            return

        width = self.ui.line_width.text().strip()
        if not width.isdigit():
            self.ui.field_errors.setText("Ширина это целое число")
            return
        height = self.ui.line_height.text().strip()
        if not height.isdigit():
            self.ui.field_errors.setText("Высота это целое число")
            return
        chance_r_wall = self.ui.chance_r_wall.text().strip()
        if not chance_r_wall.isdigit():
            self.ui.field_errors.setText(
                "Вероятность появления стены справа это целое число")
            return
        chance_b_wall = self.ui.chance_b_wall.text().strip()
        if not chance_b_wall.isdigit():
            self.ui.field_errors.setText(
                "Вероятность появления стены снизу это целое число")
            return
        width = int(width)
        if width > 200 or width < 10:
            self.ui.field_errors.setText("Ширина от 10 до 200")
            return
        height = int(height)
        if height > 200 or height < 10:
            self.ui.field_errors.setText("Ширина от 10 до 200")
            return
        chance_r_wall = int(chance_r_wall)
        if chance_r_wall > 100 or chance_r_wall < 0:
            self.ui.field_errors.setText(
                "Вероятность появления стены справа от  до 100")
            return
        chance_b_wall = int(chance_b_wall)
        if chance_b_wall > 100 or chance_b_wall < 0:
            self.ui.field_errors.setText(
                "Вероятность появления стены снизу от 0 до 100")
            return
        self.ui.field_errors.setText("")
        self.maze = generate(width, height, chance_r_wall, chance_b_wall)
        self.ui.stackedWidget.setCurrentIndex(Pages.MAZE.value)
        self.draw_maze()

    def wave_expansion(self):
        """Распрастранение волны"""
        if not self.find and not self.draw:
            start_pos, end_pos = generation_entries(self.maze)
            self.start = start_pos
            self.end = end_pos
            self.maze = start_wave(self.maze, start_pos, end_pos)
            maximum = self.maze[end_pos[0]][end_pos[1]]
            self.draw_maze(maximum)
            self.find = True
            self.ui.btn_find_way.setText("Показать путь")
        elif not self.draw and not self.way:
            way = find_way(self.maze, self.start, self.end)
            self.draw_maze(way=way)
            self.way = True

    def return_menu(self):
        """Возращение в меню"""
        if not self.draw:
            self.maze = None
            self.find = False
            self.way = False
            self.ui.btn_find_way.setText("Запуск волны")
            self.ui.stackedWidget.setCurrentIndex(Pages.MENU.value)

    def draw_maze(self, max_value=0, way=[], delay=1):
        """Рисование лабиринта"""
        self.draw = True
        self.counter = 0
        self.timer = QTimer()
        if not max_value and not way:
            self.ui.view.scene().clear()
            self.ui.view.scene().setBackgroundBrush(Qt.white)
            self.timer.timeout.connect(self.draw_rectangle)
        else:
            if way:
                self.timer.timeout.connect(lambda: self.draw_way(way))
            else:
                self.timer.timeout.connect(lambda: self.redraw(max_value))
        self.timer.start(delay)

    def draw_rectangle(self):
        """Рисование клеток"""
        if self.counter < len(self.maze) * len(self.maze[0]):
            y, x = divmod(self.counter, len(self.maze[0]))
            if self.maze[y][x] == -1:
                rect = QGraphicsRectItem(x*20, y*20, 20, 20)
                rect.setBrush(Qt.black)
                self.ui.view.scene().addItem(rect)
            self.counter += 1
        else:
            self.ui.view.scene().update()
            self.timer.stop()
            self.draw = False

    def redraw(self, max_value):
        """Красит градиентом волну"""
        if self.counter < len(self.maze) * len(self.maze[0]):
            y, x = divmod(self.counter, len(self.maze[0]))
            value = self.maze[y][x]
            step = 155//max_value
            if value not in [-1, 0]:
                rect = QGraphicsRectItem(x*20, y*20, 20, 20)
                color = QColor(255 - step * value, 255 - step * value, 0)
                rect.setBrush(color)
                self.ui.view.scene().addItem(rect)
            self.counter += 1
        else:
            self.ui.view.scene().update()
            self.timer.stop()
            self.draw = False

    def draw_way(self, way):
        """Красит путь"""
        for cell in way:
            QtTest.QTest.qWait(100)
            rect = QGraphicsRectItem(cell[1]*20, cell[0]*20, 20, 20)
            rect.setBrush(Qt.green)
            self.ui.view.scene().addItem(rect)
        self.ui.view.scene().update()
        self.timer.stop()
        self.draw = False

    def save_maze_as_txt(self):
        """Сохраняет лабиринт в тхт"""
        filename = QFileDialog.getSaveFileName(
            None, "Save File", "maze.txt", "Текстовые документы (*.txt)")
        if filename[0]:
            print(f"Selected path: {filename[0]}")
            if self.start is not None:
                start = self.maze[self.start[0]][self.start[1]]
                end = self.maze[self.end[0]][self.end[1]]
                self.maze[self.start[0]][self.start[1]] = -1
                self.maze[self.end[0]][self.end[1]] = -1
            save_txt(self.maze, filename[0])
            if self.start is not None:
                self.maze[self.start[0]][self.start[1]] = start
                self.maze[self.end[0]][self.end[1]] = end

    def save_maze_as_img(self):
        """Сохраняет лабиринт как изображение"""
        filename = QFileDialog.getSaveFileName(
            None, "Сохранение", "maze.png", "PNG (*.png);;JPEG (*.jpg)")
        if filename[0]:
            print(f"Selected path: {filename[0]}")
            if self.start is not None:
                start = self.maze[self.start[0]][self.start[1]]
                end = self.maze[self.end[0]][self.end[1]]
                self.maze[self.start[0]][self.start[1]] = -1
                self.maze[self.end[0]][self.end[1]] = -1
            save_image(self.maze, filename[0])
            if self.start is not None:
                self.maze[self.start[0]][self.start[1]] = start
                self.maze[self.end[0]][self.end[1]] = end

    def load_maze(self):
        """Загрузка лабиринта"""
        path = QFileDialog.getOpenFileName(
            None, "Загрузка", filter="Текстовые документы"
            + " (*.txt);;PNG (*.png);;JPEG (*.jpg)")[0]
        if path != "" and path.endswith(('png', 'jpg')):
            self.maze = load_maze_from_img(path)
        elif path != "" and path.endswith('txt'):
            self.maze = load_maze_from_txt(path)


if __name__ == "__main__":
    app = QApplication([])
    myapp = Window()
    sys.exit(app.exec_())
