import PyQt5.QtGui as QtGui
from PyQt5.QtWidgets import QMainWindow, QMessageBox

from ._qtdesignerforms import mainview_ui

from gifviewer.__init__ import __version__


class MainView(QMainWindow, mainview_ui.Ui_MainView):
    TITLE_PREFIX = f"GifViewer v{__version__}"

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.set_title()

        # used to prevent playing animation for the first file selected
        # when the program starts and the QListWidget is created causing
        # QListWidget::currentItemChanged() to be emitted
        self.gif_list.startup = True

        self.gif_frame_palette = QtGui.QPalette()
        self.set_nav_controls_visible(False)
        self.normal_play.setVisible(False)

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        if self._confirm_exit():
            event.accept()
        else:
            event.ignore()

    def _confirm_exit(self):
        result = QMessageBox.question(
            self, "Exit?", "Are you sure?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if result == QMessageBox.Yes:
            return True
        
        return False

    def clear_gif_display(self):
        self.gif_display.clear()

    def clear_dimensions_label(self):
        self.dimensions_label.setText("Dimensions:")

    def clear_file_list(self):
        self.gif_list.clear()

    def clear_status_message(self):
        self.statusBar().clearMessage()

    # def hide_navigation_controls(self):
    #     self._set_nav_controls_visibility(False)

    def movie(self):
        return self.gif_display.movie()

    def play_movie(self):
        self.gif_display.movie().start()

    def reset(self):
        self.set_file_count(0)
        self.clear_file_list()
        self.set_dimension_text("Dimensions: 0 x 0")
        self.clear_gif_display()

    def set_dimension_text(self, text):
        self.dimensions_label.setText(text)

    def set_file_count(self, count):
        self.files_label.setText(f"Files [{count}]:")

    def set_movie(self, movie):
        self.gif_display.setMovie(movie)

    def set_nav_controls_visible(self, visibility):
        self.frame_label.setVisible(visibility)
        self.frame_number.setVisible(visibility)
        self.frame_slider.setVisible(visibility)

    def set_speed(self, speed):
        self.speed_slider.setValue(speed)

    def set_speed_controls_visible(self, visible):
        self.speed_label.setVisible(visible)
        self.speed_slider.setVisible(visible)

    def set_speed_text(self, speed):
        self.speed_label.setText(f"Speed [{speed:03d}]:")

    def set_status_message(self, message):
        self.statusBar().showMessage(message)

    def set_title(self, title: str = ""):
        if title:
            print(title)
            title = " - " + title

        self.setWindowTitle(self.TITLE_PREFIX + title)

    # def show_navigation_controls(self):
    #     self._set_nav_controls_visibility(True)

    def speed(self) -> int:
        return self.speed_slider.value()

    def stop_movie(self):
        self.gif_display.movie().stop()

    @staticmethod
    def update_widget_palette(widget, palette, role, color):
        palette.setColor(role, color)
        widget.setPalette(palette)
