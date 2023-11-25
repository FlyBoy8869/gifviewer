"""mainview.py controller."""

from pathlib import Path

from PyQt5.QtCore import QObject, QRect, Qt, pyqtSlot
from PyQt5.QtGui import QIntValidator, QMovie, QPalette
from PyQt5.QtWidgets import QFileDialog, QListWidgetItem, QWidget

from gifviewer import helpers
import gifviewer.settings as settings


class MainViewController(QObject):
    """Implements the mainview controller."""

    ANIMATION_PLAYING_FRAME_COLOR = Qt.GlobalColor.red

    def __init__(self, view, model) -> None:
        super().__init__()
        self._view = view
        self._model = model
        self._frame_validator = QIntValidator(0, 0)
        self._original_base_role_color = view.frame.palette().color(QPalette.Base)
        self._folder_browser = FolderBrowser(start_folder=settings.cl_args.start_in)

        self._view.pushButtonBrowse.clicked.connect(self._browse_for_folder)
        self._view.actionBrowse.triggered.connect(self._browse_for_folder)
        self._view.loop.toggled.connect(self._loop_toggled)

        self._view.frame_slider.setMinimum(0)

        self._view.speed_slider.setValue(self._model.speed)
        self._view.speed_slider.valueChanged.connect(self._update_speed)
        self._view.speed_slider.sliderReleased.connect(self._speed_changed)

        self._view.gif_list.currentItemChanged.connect(
            lambda item, _: self._set_gif_display_movie_from_string(item.file_path)
        )
        self._view.gif_list.itemPressed.connect(
            lambda item: self._set_gif_display_movie_from_string(item.file_path)
        )

        self._view.single_step.toggled.connect(self._single_step_toggled)

    def initialize_controller(self) -> None:
        self._view.frame_number.setValidator(self._frame_validator)
        self._set_speed_text(self._model.speed)
        self._model.update_files(self._folder_browser.current_folder)

    @pyqtSlot(bool)  # QPushButton::clicked(), QAction::triggered()
    def _browse_for_folder(self, _: bool) -> None:
        if path := self._folder_browser.browse(self._view, "Select Folder"):
            self._view.reset()
            self._model.update_files(path)
            self._populate_gif_list(self._model.files)
            self._set_gif_display_movie_from_string(self._model.first_file)

    def _loop_toggled(self, checked: bool) -> None:
        if checked:
            self._view.single_step.setChecked(False)
            self._play_movie()
        else:
            self._stop_movie()

    def _play_movie(self) -> None:
        self._view.update_widget_palette(
            self._view.frame,
            QPalette(self._view.frame.palette()),
            QPalette.Base,
            self.ANIMATION_PLAYING_FRAME_COLOR,
        )
        self._view.gif_display.movie().start()

    @pyqtSlot(list)
    def _populate_gif_list(self, files: list[Path]) -> None:
        # handles the folder containing no gif files
        if not files:
            self._view.single_step.setEnabled(False)
            self._view.loop.setEnabled(False)
            return

        # populate widget
        for file in files:
            list_widget_item = QListWidgetItem(file.name)
            list_widget_item.file_path = file
            self._view.gif_list.addItem(list_widget_item)

        # update
        self._view.update_file_count_label(self._model.count)
        self._view.gif_list.setCurrentItem(self._view.gif_list.item(0))
        self._view.update_speed_slider(self._model.speed)
        self._update_status_bar()

        self._view.single_step.setEnabled(True)
        self._view.loop.setEnabled(True)

    @pyqtSlot(Path)
    def _set_gif_display_movie_from_string(self, path: Path) -> None:
        def _initialize_new_movie(path_: Path) -> QMovie:
            movie_: QMovie = QMovie(path_.as_posix())
            # sets CacheMode to CacheAll, so we can jump to
            # specific frames when using single step mode
            movie_.setCacheMode(QMovie.CacheMode.CacheAll)
            movie_.setSpeed(self._model.speed)
            # noinspection PyUnresolvedReferences
            movie_.frameChanged.connect(self._stop_movie_if_looping_not_selected)
            # noinspection PyUnresolvedReferences
            movie_.updated.connect(self._update_dimensions_label)
            return movie_

        current_movie: QMovie = self._view.movie()
        if current_movie and current_movie.state() == QMovie.MovieState.Running:
            self._view.normal_play.setChecked(True)

        movie: QMovie = _initialize_new_movie(path)
        self._view.set_movie(movie)
        self._view.add_title_detail(path.as_posix())

        self._view.normal_play.setChecked(True)
        self._view.update_nav_controls_visibility(False)

        self._play_movie()

    @pyqtSlot(bool)
    def _single_step_toggled(self, checked: bool) -> None:
        def _reset_gif() -> None:
            frame = 0
            self._view.frame_slider.setValue(frame)
            self._view.frame_number.setText(str(frame))
            movie.jumpToFrame(frame)

        if not checked:
            helpers.disconnect_lambda_slots(signal=self._view.frame_slider.valueChanged)
            helpers.disconnect_lambda_slots(
                signal=self._view.frame_number.returnPressed
            )
            self._view.update_speed_controls_visibility(True)
            self._view.update_nav_controls_visibility(False)
            return

        self._stop_movie()

        movie = self._view.movie()
        frame_count = movie.frameCount() - 1
        self._view.frame_slider.setMaximum(frame_count)

        self._view.frame_slider.valueChanged.connect(
            lambda frame: movie.jumpToFrame(frame)
        )
        self._view.frame_slider.valueChanged.connect(
            lambda frame: self._view.frame_number.setText(str(frame))
        )

        self._frame_validator.setTop(frame_count)

        self._view.frame_number.returnPressed.connect(
            lambda: self._view.frame_slider.setValue(
                int(self._view.frame_number.text())
            )
        )

        _reset_gif()
        self._view.loop.setChecked(False)
        self._view.update_speed_controls_visibility(False)
        self._view.update_nav_controls_visibility(True)

    @pyqtSlot()  # QSlider::sliderReleased()
    def _speed_changed(self) -> None:
        if movie := self._view.movie():
            movie.setSpeed(self._model.speed)
            self._play_movie()

    def _stop_movie(self) -> None:
        # change the frame color
        self._view.update_widget_palette(
            self._view.frame,
            QPalette(self._view.frame.palette()),
            QPalette.Base,
            self._original_base_role_color,
        )
        self._view.gif_display.movie().stop()

    @pyqtSlot(int)  # QMovie::frameChanged()
    def _stop_movie_if_looping_not_selected(self, frame_number) -> None:
        # this method is used instead of the QMovie::finished() signal
        # because infinite looping gifs don't cause the signal to be emitted
        if self._view.loop.isChecked():
            return

        # this allows the gif to play through once,
        # stopping playback when the last frame is reached
        (frame_number == self._view.movie().frameCount() - 1) and (self._stop_movie())

    @pyqtSlot(int)  # QSlider::valueChanged()
    def _set_speed_text(self, speed: int) -> None:
        self._view.update_speed_label(speed)

    @pyqtSlot(QRect)  # QMovie::updated()
    def _update_dimensions_label(self, _) -> None:
        movie = self._view.movie()
        width, height = helpers.get_pixmap_dimensions(movie.currentPixmap())
        self._view.set_dimension_text(f"Dimensions: {width} x {height}")

        # update only needs to happen once, when the file is selected
        movie.updated.disconnect(self._update_dimensions_label)

    def _update_speed(self, speed: int) -> None:
        self._model.speed = speed
        self._view.update_speed_label(speed)

    def _update_status_bar(self) -> None:
        self._view.clear_status_message()

        # only show message if more than one item is on the list
        # as the first item is automatically displayed
        if self._view.gif_list.count() > 1:
            self._view.update_status_message("Select file to preview animation.")


class FolderBrowser:
    """Opens a folder browser dialog."""

    def __init__(self, *, start_folder: str = "."):
        self._current_folder = Path(start_folder)

    @property
    def current_folder(self) -> Path:
        return self._current_folder

    def browse(self, parent: QWidget, caption: str) -> Path | None:
        """Browse for a folder starting at the last folder selected."""
        return self._browse(parent, caption, self._current_folder)

    def browse_from(self, parent, caption, folder) -> Path | None:
        """Browse for a folder starting at the given folder."""
        return self._browse(parent, caption, folder)

    def _browse(self, parent, caption, folder) -> Path | None:
        if path := QFileDialog.getExistingDirectory(
            parent, caption, folder.parent.as_posix()
        ):
            self._current_folder = Path(path)
            return self._current_folder

        return None
