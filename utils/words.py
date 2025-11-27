from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
adjectives_file = [l.strip() for l in (BASE_DIR / "words" / "adjectives.txt").read_text().splitlines() if l.strip()]
nouns_file = [l.strip() for l in (BASE_DIR / "words" / "nouns.txt").read_text().splitlines() if l.strip()]
color_file = [l.strip() for l in (BASE_DIR / "words" / "colors.txt").read_text().splitlines() if l.strip()]