# Creating PDF
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph,SimpleDocTemplate, Paragraph, Spacer

## EXPORT TXT TO PDF --------------------------------------------------------------------------------------
def generate_pdf_content(text):
    buffer = BytesIO()
    # c = canvas.Canvas(buffer, pagesize=letter)
    # c.setFont('Helvetica', 12)

    doc = SimpleDocTemplate(buffer, pagesize=letter)

    styles = getSampleStyleSheet()
    style = styles['Normal']

    # # Create a Paragraph object with the text
    # paragraph = Paragraph(text, style)

    paragraphs = []
    text_list = text.split("\n") 

    # # Draw the Paragraph on the canvas
    # paragraph.wrapOn(c, 400, 800)
    # _, height = paragraph.wrap(400, 800)
    # paragraph.drawOn(c, 100, 800 - height-75)

    for para_text in text_list:
        paragraph = Paragraph(para_text, style)
        paragraphs.append(paragraph)
        paragraphs.append(Spacer(1, 0.2 * inch))  # Add some space between paragraphs

    doc.build(paragraphs)
    # c.save()
    buffer.seek(0)
    return buffer.getvalue()

# def generate_pdf_content(text):
#     buffer = BytesIO()
#     c = canvas.Canvas(buffer, pagesize=letter)
#     c.setFont('Helvetica', 12)

#     styles = getSampleStyleSheet()
#     style = styles['Normal']

#     # Create a Paragraph object with the text
#     paragraph = Paragraph(text, style)

#     # Draw the Paragraph on the canvas
#     paragraph.wrapOn(c, 400, 800)
#     _, height = paragraph.wrap(400, 800)
#     paragraph.drawOn(c, 100, 800 - height-75)

#     c.save()
#     buffer.seek(0)
#     return buffer.getvalue()
