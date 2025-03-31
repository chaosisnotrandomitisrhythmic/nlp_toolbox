from typing import Any, Generator, List


def batch(
    iterable: List[Any], batch_size: int = 32
) -> Generator[List[Any], None, None]:
    """
    Batch the iterable into smaller lists of the given size.
    """
    if iterable == []:
        return []
    if batch_size < 1:
        raise ValueError("batch_size must be at least 1")

    iterable_len = len(iterable)

    for batch_start_index in range(0, iterable_len, batch_size):
        yield iterable[
            batch_start_index : min(batch_start_index + batch_size, iterable_len)
        ]
