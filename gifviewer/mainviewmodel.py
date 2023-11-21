from pathlib import Path

from PyQt5.QtCore import QObject

DEFAULT_SPEED = 200


class MainViewModel(QObject):
    def __init__(self) -> None:
        super().__init__()
        self._count: int = 0
        self._files = []
        self._speed = DEFAULT_SPEED

    @property
    def count(self) -> int:
        return self._count

    @property
    def files(self) -> list:
        return self._files

    @property
    def first_file(self) -> Path:
        return self._files[0]

    @property
    def speed(self) -> int:
        return self._speed

    @speed.setter
    def speed(self, speed: int) -> None:
        self._speed = speed

    def update_files(self, path: Path) -> None:
        self._files = self._get_files(path)

    def _get_files(self, path: Path) -> list[Path]:
        files = [Path(file) for file in path.rglob("*.gif")]
        self._count = len(files)

        return sorted(files, key=lambda p: p.name.lower())
