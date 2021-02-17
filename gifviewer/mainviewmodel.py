from pathlib import Path
from typing import List


class MainViewModel:
    def __init__(self) -> None:
        self._count: int = 0

    @property
    def count(self) -> int:
        return self._count

    def get_files(self, path: Path) -> List[Path]:
        files = [Path(file) for file in path.rglob("*.gif")]
        self._count = len(files)

        return sorted(files, key=lambda p: p.name.lower())
