from PyQt5.QtGui import QCloseEvent, QColor, QMovie, QPalette
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QWidget

from gifviewer.__init__ import __version__

from ._qtdesignerforms import mainview_ui


class MainView(QMainWindow, mainview_ui.Ui_MainView):
    TITLE_PREFIX = f"GifViewer v{__version__}"

    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        self.set_title()

        # used to prevent playing animation for the first file selected
        # when the program starts and the QListWidget is created causing
        # QListWidget::currentItemChanged() to be emitted
        self.gif_list.startup = True

        self.gif_frame_palette = QPalette()
        self.set_nav_controls_visible(False)
        self.normal_play.setVisible(False)

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._confirm_exit():
            event.accept()
        else:
            event.ignore()

    def _confirm_exit(self) -> bool:
        result = QMessageBox.question(
            self,
            "Exit?",
            "Are you sure?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        return result == QMessageBox.Yes

    def clear_gif_display(self) -> None:
        self.gif_display.clear()

    def clear_dimensions_label(self) -> None:
        self.dimensions_label.setText("Dimensions:")

    def clear_file_list(self) -> None:
        self.gif_list.clear()

    def clear_status_message(self) -> None:
        self.statusBar().clearMessage()

    # def hide_navigation_controls(self):
    #     self._set_nav_controls_visibility(False)

    def movie(self) -> QMovie:
        return self.gif_display.movie()

    def play_movie(self) -> None:
        self.gif_display.movie().start()

    def reset(self) -> None:
        self.set_file_count(0)
        self.clear_file_list()
        self.set_dimension_text("Dimensions: 0 x 0")
        self.clear_gif_display()

    def set_dimension_text(self, text: str) -> None:
        self.dimensions_label.setText(text)

    def set_file_count(self, count: int) -> None:
        self.files_label.setText(f"Files [{count}]:")

    def set_movie(self, movie: QMovie) -> None:
        self.gif_display.setMovie(movie)

    def set_nav_controls_visible(self, visibility: bool) -> None:
        self.frame_label.setVisible(visibility)
        self.frame_number.setVisible(visibility)
        self.frame_slider.setVisible(visibility)

    def set_speed(self, speed: int) -> None:
        self.speed_slider.setValue(speed)

    def set_speed_controls_visible(self, visible: bool) -> None:
        self.speed_label.setVisible(visible)
        self.speed_slider.setVisible(visible)

    def update_speed_label(self, speed: int) -> None:
        self.speed_label.setText(f"Speed [{speed:03d}]:")

    def set_status_message(self, message: str) -> None:
        self.statusBar().showMessage(message)

    def set_title(self, title: str = "") -> None:
        if title:
            print(title)
            title = f" - {title}"

        self.setWindowTitle(self.TITLE_PREFIX + title)

    def speed(self) -> int:
        return self.speed_slider.value()

    def stop_movie(self) -> None:
        self.gif_display.movie().stop()

    @staticmethod
    def update_widget_palette(
        widget: QWidget, palette: QPalette, role: QPalette.ColorRole, color: QColor
    ) -> None:
        palette.setColor(role, color)
        widget.setPalette(palette)
