import io
from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import Color
from reportlab.pdfgen import canvas


def create_watermark_pdf(page_width: float, page_height: float) -> bytes:
    """Generate a single-page watermark PDF with 'PROCESSED' in red."""
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=(page_width, page_height))
 
    # Semi-transparent red
    red = Color(1, 0, 0, alpha=0.35)
    c.setFillColor(red)
 
    # Rotate 45° around page center and draw text
    c.saveState()
    c.translate(page_width / 2, page_height / 2)
    c.rotate(45)
 
    font_size = min(page_width, page_height) / 4
    c.setFont("Helvetica-Bold", font_size)
 
    # Centre the text on the origin before the translate
    text = "PROCESSED"
    text_width = c.stringWidth(text, "Helvetica-Bold", font_size)
    c.drawString(-text_width / 2, -font_size / 2, text)
 
    c.restoreState()
    c.save()
 
    packet.seek(0)
    return packet.read()

def add_watermark(pdf_file: io.IOBase) -> io.BytesIO:
    """
    Stamp every page of *pdf_file* with a large red 'PROCESSED' watermark.
 
    Parameters
    ----------
    pdf_file : file-like object
        Any readable binary file-like object containing a valid PDF
        (e.g. an open file handle, BytesIO, Django InMemoryUploadedFile, etc.).
 
    Returns
    -------
    io.BytesIO
        A BytesIO object positioned at 0 that contains the watermarked PDF.
    """
    reader = PdfReader(pdf_file)
    writer = PdfWriter()
 
    for page in reader.pages:
        # Use each page's actual dimensions for a perfectly fitted watermark
        page_width  = float(page.mediabox.width)
        page_height = float(page.mediabox.height)
 
        watermark_bytes = create_watermark_pdf(page_width, page_height)
        watermark_page  = PdfReader(io.BytesIO(watermark_bytes)).pages[0]
 
        # Merge watermark on top of the original page content
        page.merge_page(watermark_page)
        writer.add_page(page)
 
    output = io.BytesIO()
    writer.write(output)
    output.seek(0)
    return output