# Creating PDF
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph

# Upload pdf
import os
from os import walk
from werkzeug.utils import secure_filename

# Extract txt from pdf
from langchain.document_loaders import UnstructuredFileLoader

# Extract txt from img
from langchain.document_loaders.image import UnstructuredImageLoader

## IMPORT TXT FROM IMG ------------------------------------------------------------------------------------
def importing_img(img_file):
    if img_file.filename == '':
            flash('No selected file')
            return render_template('translate.html', translation_result=None)
    if img_file and allowed_file(img_file.filename):
        filename = secure_filename(img_file.filename)
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        img_file.save(img_path)
        txt_from_img = extract_img_txt(img_path)
        return render_template('translate.html', img_uploaded="img uploaded", txt_from_img=txt_from_img)
    return render_template('translate.html', img_uploaded="img not uploaded, extention allowed : .jpg, .jpeg, .png")

def extract_img_txt(img_path):
    loader = UnstructuredImageLoader(img_path)
    data = loader.load()
    txt_from_img = data[0].page_content
    return txt_from_img

## IMPORT TXT FROM PDF ------------------------------------------------------------------------------------
def importing_pdf(pdf_file):
    if pdf_file.filename == '':
            flash('No selected file')
            return render_template('translate.html', translation_result=None)
    if pdf_file and allowed_file(pdf_file.filename):
        filename = secure_filename(pdf_file.filename)
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        pdf_file.save(pdf_path)
        txt_from_pdf = extract_pdf_txt(pdf_path)
        return render_template('translate.html', pdf_uploaded="pdf uploaded", txt_from_pdf=txt_from_pdf)
    return render_template('translate.html', pdf_uploaded="pdf not uploaded, extention allowed : .pdf")
    
def extract_pdf_txt(pdf_file):

    loader = UnstructuredFileLoader(pdf_file)
    documents = loader.load()
    pdf_pages_content = '\n'.join(doc.page_content for doc in documents)
    
    return pdf_pages_content

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

## EXPORT TXT TO PDF --------------------------------------------------------------------------------------
def generate_pdf_content(text):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont('Helvetica', 12)

    styles = getSampleStyleSheet()
    style = styles['Normal']

    # Create a Paragraph object with the text
    paragraph = Paragraph(text, style)

    # Draw the Paragraph on the canvas
    paragraph.wrapOn(c, 400, 800)
    _, height = paragraph.wrap(400, 800)
    paragraph.drawOn(c, 100, 800 - height-75)

    c.save()
    buffer.seek(0)
    return buffer.getvalue()
