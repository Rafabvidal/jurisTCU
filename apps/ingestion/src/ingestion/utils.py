import pathlib
from unicodedata import normalize as unicode_normalize

WORKSPACE = pathlib.Path(__file__).parent

DATA_FOLDER = WORKSPACE / "data"

def normalize_topic(text: str) -> str:
    return (
        unicode_normalize("NFKD", text)
        .encode("ascii", "ignore")
        .decode("utf-8")
        .lower()
        .replace(" ", "_")
        .replace("/", "_")
    )
