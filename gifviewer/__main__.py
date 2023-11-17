import sys

from PyQt5.QtWidgets import QApplication

from .gui.mainview import MainView
from .mainviewcontroller import MainViewController
from .mainviewmodel import MainViewModel


def main():
    """Blast Off!"""

    app = QApplication(sys.argv)

    main_view = MainView()

    main_view_model = MainViewModel()

    main_view_controller = MainViewController(main_view, main_view_model)
    main_view_controller.initialize_controller()

    main_view.show()
    sys.exit(app.exec())
