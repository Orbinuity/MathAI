import sys
import os
import atexit
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import QApplication, QLabel, QWidget

POS_FILE = "overlayPos.dat"
ALL_POS_FILE = "overlayPositions.dat"
OFFSET = 40
MAX_TRIES = 100

if len(sys.argv) != 2:
    print(f"Usage: python {sys.argv[0]} <text>")
    sys.exit(1)


def load_all_positions():
    if os.path.exists(ALL_POS_FILE):
        with open(ALL_POS_FILE, "r") as f:
            return [tuple(map(int, line.strip().split(','))) for line in f if ',' in line]
    return []


def save_all_positions(positions):
    with open(ALL_POS_FILE, "w") as f:
        for x, y in positions:
            f.write(f"{x},{y}\n")


def rects_overlap(r1, r2):
    return QRect(r1[0], r1[1], r1[2], r1[3]).intersects(QRect(r2[0], r2[1], r2[2], r2[3]))


class TextOverlay(QWidget):
    def __init__(self, text):
        super().__init__()
        self.my_position = (100, 100)
        self.text = text
        self.initUI()
        self.set_unique_position()
        atexit.register(self.cleanup_position)

    def initUI(self):
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool |
            Qt.X11BypassWindowManagerHint |
            Qt.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_X11DoNotAcceptFocus)

        font = self.font()
        font.setPointSize(24)
        self.setFont(font)

        self.label = QLabel(self.text, self)
        self.label.setStyleSheet("""
            color: white;
            font-size: 24px;
            padding: 8px;
            border: none;
        """)
        self.label.adjustSize()
        self.resize(self.label.size())
        self.label.setGeometry(0, 0, self.width(), self.height())

        self.show()
        self.is_dragging = False

    def set_unique_position(self):
        base_x, base_y = self.load_saved_position()
        all_positions = load_all_positions()
        width, height = self.width(), self.height()

        for i in range(MAX_TRIES):
            candidate = (base_x + i * OFFSET, base_y + i * OFFSET)
            new_rect = (candidate[0], candidate[1], width, height)
            if not any(rects_overlap(new_rect, (x, y, width, height)) for x, y in all_positions):
                self.move(*candidate)
                self.my_position = candidate
                all_positions.append(candidate)
                save_all_positions(all_positions)
                return
        self.move(base_x, base_y)

    def load_saved_position(self):
        if os.path.exists(POS_FILE):
            try:
                with open(POS_FILE, "r") as f:
                    x, y = map(int, f.read().split(","))
                    return x, y
            except:
                pass
        return 100, 100

    def save_current_position(self):
        with open(POS_FILE, "w") as f:
            f.write(f"{self.x()},{self.y()}")

    def cleanup_position(self):
        all_positions = load_all_positions()
        if self.my_position in all_positions:
            all_positions.remove(self.my_position)
            save_all_positions(all_positions)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()
            self.is_dragging = True

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = False

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            delta = event.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.save_current_position()
            self.cleanup_position()
            QApplication.quit()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()
        bg_color = QColor(0, 0, 0, 160)
        painter.setBrush(bg_color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, 10, 10)
        super().paintEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    overlay = TextOverlay(sys.argv[1])
    sys.exit(app.exec_())
