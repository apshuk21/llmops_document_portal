from pathlib import Path

class FakeUpload:
    def __init__(self, file_path: Path):
        self.name = file_path.name
        self._buffer = file_path.read_bytes()

    @property
    def buffer(self):
        return self._buffer