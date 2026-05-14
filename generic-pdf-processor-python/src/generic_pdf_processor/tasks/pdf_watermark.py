import io

from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import Color
from reportlab.pdfgen import canvas


def create_watermark_pdf(page_width: float, page_height: float) -> bytes:
    """Generate a single-page watermark PDF with 'PROCESSED' in red."""
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=(page_width, page_height))

    red = Color(1, 0, 0, alpha=0.35)
    c.setFillColor(red)

    c.saveState()
    c.translate(page_width / 2, page_height / 2)
    c.rotate(45)

    font_size = min(page_width, page_height) / 4
    c.setFont("Helvetica-Bold", font_size)

    text = "PROCESSED"
    text_width = c.stringWidth(text, "Helvetica-Bold", font_size)
    c.drawString(-text_width / 2, -font_size / 2, text)

    c.restoreState()
    c.save()

    packet.seek(0)
    return packet.read()


def add_watermark(pdf_file: io.IOBase) -> io.BytesIO:
    """Stamp every page of a PDF file with a red 'PROCESSED' watermark."""
    reader = PdfReader(pdf_file)
    writer = PdfWriter()

    for page in reader.pages:
        page_width = float(page.mediabox.width)
        page_height = float(page.mediabox.height)

        watermark_bytes = create_watermark_pdf(page_width, page_height)
        watermark_page = PdfReader(io.BytesIO(watermark_bytes)).pages[0]

        page.merge_page(watermark_page)
        writer.add_page(page)

    output = io.BytesIO()
    writer.write(output)
    output.seek(0)
    return output

