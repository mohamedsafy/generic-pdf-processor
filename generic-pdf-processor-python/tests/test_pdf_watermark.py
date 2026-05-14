import io
import warnings

import pytest
from pypdf import PdfReader
from reportlab.lib.pagesizes import A4, letter

from generic_pdf_processor.tasks.pdf_watermark import add_watermark, create_watermark_pdf


def _make_blank_pdf(num_pages: int = 1, pagesize: tuple = letter) -> io.BytesIO:
    """Return a BytesIO containing a blank PDF with num_pages pages."""
    from reportlab.pdfgen import canvas

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=pagesize)
    for i in range(num_pages):
        c.drawString(50, pagesize[1] - 50, f"Page {i + 1}")
        c.showPage()
    c.save()
    buf.seek(0)
    return buf


def _parse_pdf(data: bytes | io.BytesIO) -> PdfReader:
    """Wrap bytes or BytesIO in a PdfReader."""
    if isinstance(data, bytes):
        data = io.BytesIO(data)
    data.seek(0)
    return PdfReader(data)



class TestAddWatermark:
    def test_does_not_emit_pypdf_deprecation_warning(self):
        pdf = _make_blank_pdf()

        with warnings.catch_warnings():
            warnings.filterwarnings("error", category=DeprecationWarning, module="pypdf")
            result = add_watermark(pdf)

        assert isinstance(result, io.BytesIO)

    def test_processed_text_in_every_page_stream(self):
        pdf = _make_blank_pdf(num_pages=3)
        result = add_watermark(pdf)
        content = result.getvalue()
        assert content.count(b"PROCESSED") >= 3

    def test_accepts_bytesio(self):
        pdf_bytes = _make_blank_pdf().getvalue()
        result = add_watermark(io.BytesIO(pdf_bytes))
        assert isinstance(result, io.BytesIO)

    def test_accepts_open_file_handle(self, tmp_path):
        pdf_path = tmp_path / "sample.pdf"
        pdf_path.write_bytes(_make_blank_pdf().getvalue())
        with open(pdf_path, "rb") as f:
            result = add_watermark(f)
        assert isinstance(result, io.BytesIO)

    def test_can_watermark_already_watermarked_pdf(self):
        pdf = _make_blank_pdf()
        once = add_watermark(pdf)
        twice = add_watermark(once)
        assert len(_parse_pdf(twice).pages) == 1

