from PyQt5.QtGui import QCloseEvent, QColor, QMovie, QPalette
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QWidget

import gifviewer.settings as settings
from gifviewer.__init__ import __version__
from gifviewer.gui.qtdesignerforms import mainview_ui


class MainView(QMainWindow, mainview_ui.Ui_MainView):
    TITLE_PREFIX = f"GifViewer v{__version__}"

    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        self.add_title_detail()

        # used to prevent playing animation for the first file selected
        # when the program starts and the QListWidget is created causing
        # QListWidget::currentItemChanged() to be emitted
        self.gif_list.startup = True

        self.gif_frame_palette = QPalette()
        self.update_nav_controls_visibility(False)
        self.normal_play.setVisible(False)

    def closeEvent(self, event: QCloseEvent) -> None:
        if settings.cl_args.no_confirm_exit:
            event.accept()
            return

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
        self.update_file_count(0)
        self.clear_file_list()
        self.set_dimension_text("Dimensions: 0 x 0")
        self.clear_gif_display()

    def set_dimension_text(self, text: str) -> None:
        self.dimensions_label.setText(text)

    def update_file_count(self, count: int) -> None:
        self.files_label.setText(f"Files [{count}]:")

    def set_movie(self, movie: QMovie) -> None:
        self.gif_display.setMovie(movie)

    def update_nav_controls_visibility(self, visibility: bool) -> None:
        self.frame_label.setVisible(visibility)
        self.frame_number.setVisible(visibility)
        self.frame_slider.setVisible(visibility)

    def update_speed_slider(self, speed: int) -> None:
        self.speed_slider.setValue(speed)

    def update_speed_controls_visibility(self, visible: bool) -> None:
        self.speed_label.setVisible(visible)
        self.speed_slider.setVisible(visible)

    def update_speed_label(self, speed: int) -> None:
        self.speed_label.setText(f"Speed [{speed:03d}]:")

    def update_status_message(self, message: str) -> None:
        self.statusBar().showMessage(message)

    def add_title_detail(self, detail: str = "") -> None:
        detail = f" - {detail}" if detail else detail
        self.setWindowTitle(self.TITLE_PREFIX + detail)

    def stop_movie(self) -> None:
        self.gif_display.movie().stop()

    @staticmethod
    def update_widget_palette(
        widget: QWidget, palette: QPalette, role: QPalette.ColorRole, color: QColor
    ) -> None:
        palette.setColor(role, color)
        widget.setPalette(palette)
