from pathlib import Path

from PyQt5.QtCore import QObject, QRect, Qt, pyqtSlot
from PyQt5.QtGui import QIntValidator, QMovie, QPalette
from PyQt5.QtWidgets import QFileDialog, QListWidgetItem

from gifviewer import helpers


class MainViewController(QObject):
    DEFAULT_MOVIE_SPEED = 100
    ANIMATION_PLAYING_FRAME_COLOR = Qt.red

    def __init__(self, view, model) -> None:
        super().__init__()
        self._view = view
        self._model = model
        self._frame_validator = QIntValidator(0, 0)
        self._current_file_path = None
        self.original_base_role_color = view.frame.palette().color(QPalette.Base)

        self._view.pushButtonBrowse.clicked.connect(self._browse_for_folder)
        self._view.actionBrowse.triggered.connect(self._browse_for_folder)
        self._view.loop.toggled.connect(self._play_movie)
        self._view.speed_slider.valueChanged.connect(self._update_speed_label)
        self._view.speed_slider.sliderReleased.connect(self._speed_changed)

        self._view.gif_list.currentItemChanged.connect(
            lambda current, _: current and self._set_gif_display_movie_from_string(current.file_path)
        )
        self._view.gif_list.itemPressed.connect(
            lambda item: self._set_gif_display_movie_from_string(item.file_path)
        )

        self._model.files_changed.connect(self._populate_gif_list)
        self._model.first_file.connect(self._set_gif_display_movie_from_string)

        self._view.single_step.toggled.connect(self._single_step_toggled)

    def initialize_controller(self) -> None:
        self._view.frame_number.setValidator(self._frame_validator)

        self._update_speed_label(self.DEFAULT_MOVIE_SPEED)
        self._model.update_files_from_path(Path("/Users/charles/Downloads/assets"))

    @pyqtSlot(bool)  # QPushButton::clicked(), QAction::triggered()
    def _browse_for_folder(self, _: bool) -> None:
        path = QFileDialog.getExistingDirectory(self._view, "Select Directory", ".")
        if path:
            self._view.reset()
            self._model.update_files_from_path(Path(path))

    def _play_movie(self) -> None:
        self._view.update_widget_palette(
            self._view.frame,
            QPalette(self._view.frame.palette()),
            QPalette.Base,
            self.ANIMATION_PLAYING_FRAME_COLOR
        )
        self._view.play_movie()

    @pyqtSlot(list)
    def _populate_gif_list(self, files: list[Path]) -> None:
        if not files:
            self._current_file_path = None
            self._view.single_step.setEnabled(False)
            self._view.loop.setEnabled(False)
            return

        # populate
        for file in files:
            list_widget_item = QListWidgetItem(file.name)
            list_widget_item.file_path = file
            self._view.gif_list.addItem(list_widget_item)

        # update
        self._view.set_file_count(self._model.count)
        self._view.gif_list.setCurrentItem(self._view.gif_list.item(0))
        self._view.set_speed(self.DEFAULT_MOVIE_SPEED)
        self._update_status_bar()

        self._view.single_step.setEnabled(True)
        self._view.loop.setEnabled(True)

    @pyqtSlot(Path)
    def _set_gif_display_movie_from_string(self, path: Path) -> None:
        if path == self._current_file_path:
            # trigger QRadioButton::toggled() signals
            # which will cause nav controls to be disabled and hidden
            self._view.normal_play.setChecked(True)
            self._play_movie()
            return

        current_movie = self._view.movie()
        if current_movie and current_movie.state() == QMovie.Running:
            self._view.normal_play.setChecked(True)

        speed = self._view.speed()

        movie: QMovie = QMovie(path.as_posix())
        movie.setCacheMode(QMovie.CacheAll)
        movie.setSpeed(speed)
        # noinspection PyUnresolvedReferences
        movie.frameChanged.connect(self._stop_movie_if_looping_not_selected)
        # noinspection PyUnresolvedReferences
        movie.updated.connect(self._update_dimensions_label)

        self._current_gif_frame_count = movie.frameCount() - 1
        self._current_file_path = path

        self._view.set_movie(movie)
        self._view.set_title(path.as_posix())

        self._view.normal_play.setChecked(True)
        self._view.set_nav_controls_visible(False)

        self._play_movie()

    @pyqtSlot(bool)
    def _single_step_toggled(self, checked: bool) -> None:
        def _setup_starting_frame(*, current_frame, last_frame):
            if current_frame == last_frame:
                current_frame = 0
            self._view.frame_slider.setValue(current_frame)
            self._view.frame_number.setText(str(current_frame))
            movie.jumpToFrame(current_frame)

        if not checked:
            helpers.disconnect_lambda_slots(signal=self._view.frame_slider.valueChanged)
            helpers.disconnect_lambda_slots(signal=self._view.frame_number.returnPressed)
            self._view.set_speed_controls_visible(True)
            self._view.set_nav_controls_visible(False)
            return

        self._stop_movie()

        movie = self._view.movie()
        frame_count = movie.frameCount() - 1

        self._view.frame_slider.setMinimum(0)
        self._view.frame_slider.setMaximum(frame_count)

        self._view.frame_slider.valueChanged.connect(lambda frame: movie.jumpToFrame(frame))
        self._view.frame_slider.valueChanged.connect(lambda frame: self._view.frame_number.setText(str(frame)))

        self._frame_validator.setTop(frame_count)

        self._view.frame_number.returnPressed.connect(
            lambda: self._view.frame_slider.setValue(int(self._view.frame_number.text()))
        )

        _setup_starting_frame(current_frame=movie.currentFrameNumber(), last_frame=frame_count)

        self._view.set_speed_controls_visible(False)

        self._view.set_nav_controls_visible(True)

    @pyqtSlot()  # QSlider::sliderReleased()
    def _speed_changed(self) -> None:
        speed = self._view.speed()
        if movie := self._view.movie():
            movie.setSpeed(speed)
            self._play_movie()

    def _stop_movie(self) -> None:
        # change the frame color
        self._view.update_widget_palette(
            self._view.frame,
            QPalette(self._view.frame.palette()),
            QPalette.Base,
            self.original_base_role_color
        )

        self._view.stop_movie()

    @pyqtSlot(int)  # QMovie::frameChanged()
    def _stop_movie_if_looping_not_selected(self, frame_number) -> None:
        # this method is used instead of the QMovie::finished() signal
        # because infinite looping gifs don't cause the signal to be emitted
        if self._view.loop.isChecked():
            return
        frame_number == self._view.movie().frameCount() - 1 and self._stop_movie()

    @pyqtSlot(int)  # QSlider::valueChanged()
    def _update_speed_label(self, speed: int) -> None:
        self._view.set_speed_text(speed)

    @pyqtSlot(QRect)  # QMovie::updated()
    def _update_dimensions_label(self, _) -> None:
        movie = self._view.movie()
        width, height = helpers.get_pixmap_dimensions(movie.currentPixmap())
        self._view.set_dimension_text(f"Dimensions: {width} x {height}")

        # update only needs to happen once, when the file is selected
        movie.updated.disconnect(self._update_dimensions_label)

    def _update_status_bar(self) -> None:
        self._view.clear_status_message()

        # only show message if more than one item is on the list as the first item is automatically displayed
        if self._view.gif_list.count() > 1:
            self._view.set_status_message("Select file to preview animation.")
