from pathlib import Path

from PyQt5.QtCore import QObject, pyqtSignal


class MainViewModel(QObject):
    files_changed = pyqtSignal(list)
    first_file = pyqtSignal(Path)

    def __init__(self) -> None:
        super().__init__()
        self._count: int = 0

    @property
    def count(self) -> int:
        return self._count

    def update_files(self, path: Path) -> None:
        files = self._get_files(path)
        self.files_changed.emit(files)
        if files:
            self.first_file.emit(files[0])

    def _get_files(self, path: Path) -> list[Path]:
        files = [Path(file) for file in path.rglob("*.gif")]
        self._count = len(files)

        return sorted(files, key=lambda p: p.name.lower())
