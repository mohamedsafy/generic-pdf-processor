import io
from collections.abc import Iterable

from generic_pdf_processor.tasks.pdf_watermark import add_watermark


class UnknownPdfTaskError(ValueError):
    """Raised when a requested PDF processing task is not supported."""

    def __init__(self, task: str) -> None:
        super().__init__(f"Task '{task}' was not found")
        self.task = task


def process_pdf(file: io.IOBase, tasks: Iterable[str]) -> io.BytesIO | io.IOBase:
    processed_file: io.BytesIO | io.IOBase = file

    for task in tasks:
        if task == "add_watermark":
            processed_file = add_watermark(processed_file)
            continue

        raise UnknownPdfTaskError(task)

    return processed_file

