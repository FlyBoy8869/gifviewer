import contextlib

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap


def disconnect_lambda_slots(*, signal: pyqtSignal) -> None:
    # ignore first run - when no slots connected
    with contextlib.suppress(TypeError):
        signal.disconnect()


def get_pixmap_dimensions(pixmap: QPixmap) -> tuple[int, int]:
    size = pixmap.size()
    return size.width(), size.height()
