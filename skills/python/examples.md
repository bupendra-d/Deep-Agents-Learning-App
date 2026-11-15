# Python Example

```python
from pathlib import Path
import csv

def read_csv(path: str) -> list[dict[str, str]]:
    file_path = Path(path)
    with file_path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))
```

Use `pathlib` for paths and `csv.DictReader` for CSV rows.
