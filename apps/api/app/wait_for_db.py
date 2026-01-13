import time

from sqlalchemy import text

from .db import engine


def wait_for_db(max_retries: int = 30, delay: float = 2.0) -> None:
    for _ in range(max_retries):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return
        except Exception:  # noqa: BLE001
            time.sleep(delay)
    raise RuntimeError("Database not ready")


if __name__ == "__main__":
    wait_for_db()
