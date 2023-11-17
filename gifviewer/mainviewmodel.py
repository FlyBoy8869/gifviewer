from pathlib import Path
from typing import List

from PyQt5.QtCore import QObject, pyqtSignal


class MainViewModel(QObject):
    files_changed = pyqtSignal(list)
    first_file = pyqtSignal(Path)

    def __init__(self) -> None:
        super().__init__()
        self._count: int = 0
        self._current_path = Path(".")

    @property
    def count(self) -> int:
        return self._count

    @property
    def current_path(self) -> Path:
        return self._current_path

    @current_path.setter
    def current_path(self, path: Path) -> None:
        print(f"path to save: {path=}")
        self._current_path = path

    def update_files(self) -> None:
        # files = self._get_files(path)
        files = self._get_files(self._current_path)
        self.files_changed.emit(files)
        if files:
            self.first_file.emit(files[0])

    def _get_files(self, path: Path) -> List[Path]:
        files = [Path(file) for file in path.rglob("*.gif")]
        self._count = len(files)

        return sorted(files, key=lambda p: p.name.lower())
