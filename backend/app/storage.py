import os
import uuid

DATA_DIR = "data"


def save_file(file_bytes: bytes, original_filename: str) -> str:
    os.makedirs(DATA_DIR, exist_ok=True)

    unique_name = f"{uuid.uuid4().hex}_{original_filename}"
    path = os.path.join(DATA_DIR, unique_name)

    with open(path, "wb") as f:
        f.write(file_bytes)

    return path
