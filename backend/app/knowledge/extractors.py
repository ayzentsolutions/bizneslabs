from abc import ABC, abstractmethod

class TextExtractor(ABC):
    @abstractmethod
    def extract(self, filename: str, data: bytes) -> str:
        raise NotImplementedError

class PlainTextExtractor(TextExtractor):
    def extract(self, filename: str, data: bytes) -> str:
        return data.decode("utf-8", errors="replace")

class ExtractorRegistry:
    def __init__(self):
        self._extractors = {"txt": PlainTextExtractor(), "md": PlainTextExtractor(), "csv": PlainTextExtractor()}
    def get(self, filename: str) -> TextExtractor:
        suffix=filename.rsplit(".",1)[-1].lower() if "." in filename else "txt"
        return self._extractors.get(suffix, self._extractors["txt"])
