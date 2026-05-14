import io

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


class TestCreateWatermarkPdf:
    def test_returns_bytes(self):
        result = create_watermark_pdf(612, 792)
        assert isinstance(result, bytes)

    def test_returns_non_empty_bytes(self):
        result = create_watermark_pdf(612, 792)
        assert len(result) > 0

    def test_output_is_valid_pdf(self):
        result = create_watermark_pdf(612, 792)
        reader = _parse_pdf(result)
        assert len(reader.pages) == 1

    def test_letter_page_dimensions(self):
        w, h = letter
        result = create_watermark_pdf(w, h)
        page = _parse_pdf(result).pages[0]
        assert float(page.mediabox.width) == pytest.approx(w, abs=1)
        assert float(page.mediabox.height) == pytest.approx(h, abs=1)

    def test_a4_page_dimensions(self):
        w, h = A4
        result = create_watermark_pdf(w, h)
        page = _parse_pdf(result).pages[0]
        assert float(page.mediabox.width) == pytest.approx(w, abs=1)
        assert float(page.mediabox.height) == pytest.approx(h, abs=1)

    def test_landscape_page_dimensions(self):
        w, h = 1190, 842
        result = create_watermark_pdf(w, h)
        page = _parse_pdf(result).pages[0]
        assert float(page.mediabox.width) == pytest.approx(w, abs=1)
        assert float(page.mediabox.height) == pytest.approx(h, abs=1)

    def test_square_page_dimensions(self):
        result = create_watermark_pdf(500, 500)
        page = _parse_pdf(result).pages[0]
        assert float(page.mediabox.width) == pytest.approx(500, abs=1)
        assert float(page.mediabox.height) == pytest.approx(500, abs=1)

    def test_exactly_one_page(self):
        result = create_watermark_pdf(612, 792)
        assert len(_parse_pdf(result).pages) == 1

    def test_pdf_stream_contains_processed_text(self):
        result = create_watermark_pdf(612, 792)
        assert b"PROCESSED" in result

    def test_different_sizes_produce_different_outputs(self):
        r1 = create_watermark_pdf(612, 792)
        r2 = create_watermark_pdf(595, 842)
        assert r1 != r2

    def test_same_inputs_produce_identical_outputs(self):
        r1 = create_watermark_pdf(612, 792)
        r2 = create_watermark_pdf(612, 792)
        assert r1 == r2

    def test_very_small_page(self):
        result = create_watermark_pdf(10, 10)
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_very_large_page(self):
        result = create_watermark_pdf(5000, 7000)
        page = _parse_pdf(result).pages[0]
        assert float(page.mediabox.width) == pytest.approx(5000, abs=1)

    def test_float_dimensions(self):
        result = create_watermark_pdf(595.276, 841.89)
        assert len(result) > 0


class TestAddWatermark:
    def test_returns_bytesio(self):
        pdf = _make_blank_pdf()
        result = add_watermark(pdf)
        assert isinstance(result, io.BytesIO)

    def test_output_is_valid_pdf(self):
        pdf = _make_blank_pdf()
        result = add_watermark(pdf)
        _parse_pdf(result)

    def test_output_position_is_zero(self):
        pdf = _make_blank_pdf()
        result = add_watermark(pdf)
        assert result.tell() == 0

    def test_single_page_count_preserved(self):
        pdf = _make_blank_pdf(num_pages=1)
        result = add_watermark(pdf)
        assert len(_parse_pdf(result).pages) == 1

    def test_multi_page_count_preserved(self):
        pdf = _make_blank_pdf(num_pages=5)
        result = add_watermark(pdf)
        assert len(_parse_pdf(result).pages) == 5

    def test_ten_page_count_preserved(self):
        pdf = _make_blank_pdf(num_pages=10)
        result = add_watermark(pdf)
        assert len(_parse_pdf(result).pages) == 10

    def test_letter_dimensions_preserved(self):
        w, h = letter
        pdf = _make_blank_pdf(pagesize=(w, h))
        result = add_watermark(pdf)
        page = _parse_pdf(result).pages[0]
        assert float(page.mediabox.width) == pytest.approx(w, abs=1)
        assert float(page.mediabox.height) == pytest.approx(h, abs=1)

    def test_a4_dimensions_preserved(self):
        w, h = A4
        pdf = _make_blank_pdf(pagesize=(w, h))
        result = add_watermark(pdf)
        page = _parse_pdf(result).pages[0]
        assert float(page.mediabox.width) == pytest.approx(w, abs=1)
        assert float(page.mediabox.height) == pytest.approx(h, abs=1)

    def test_output_larger_than_input(self):
        pdf = _make_blank_pdf()
        original_size = len(pdf.getvalue())
        result = add_watermark(pdf)
        assert len(result.getvalue()) > original_size

    def test_processed_text_in_output(self):
        pdf = _make_blank_pdf()
        result = add_watermark(pdf)
        assert b"PROCESSED" in result.getvalue()

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

    def test_result_is_re_readable(self):
        pdf = _make_blank_pdf()
        result = add_watermark(pdf)
        first_read = result.read()
        result.seek(0)
        second_read = result.read()
        assert first_read == second_read

    def test_can_watermark_already_watermarked_pdf(self):
        pdf = _make_blank_pdf()
        once = add_watermark(pdf)
        twice = add_watermark(once)
        assert len(_parse_pdf(twice).pages) == 1

