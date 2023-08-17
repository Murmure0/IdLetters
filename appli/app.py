# App
from flask import Flask, render_template, request, Response,session,flash
import requests
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

# External functions
import sys
sys.path.insert(0, 'appli/toolBox/')
from toolBox import translateText


# Debug
import logging

# ------------------------------------------------------------------------- #

    # TODODOO :
    # 1024 token/appel API :

    # voir comment gerer un pdf a plusieurs pages
    # segmenté le text s'il est trop long pour l'API et append dans un pdf à download


# ------------------------------------------------------------------------- #
# APP
app = Flask(__name__)

# Session
app.secret_key = '123' # you should not see that, shoo

# ------------------------------------------------------------------------- #
# PDF upload 

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {'pdf','jpg', 'jpeg', 'png', 'heif', 'heic'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# ------------------------------------------------------------------------- #
# Paths

@app.route('/', methods=['GET', 'POST'])
def translate_text():
    first_page=True
    # Default
    if request.method == 'GET':
        return render_template('translate.html', translation_result=None)

    # Get text from text zone
    try:
        input_text = request.form.get('input_text')
    except Exception as e:
        error_message= f"Pas de texte soumis : {input_text}|erreur:{e}"
    # Get the langs from/to translate
    transl_from = request.form.get('language_from')


    # Identify the language from the text given
    if transl_from == 'idk':
        try :
            json_lang = translateText.detec_lang(input_text)
            transl_from = json_lang[0]['label']
        except Exception as e:
            error_message=f'error : {json_lang}|{e}'
    transl_to = request.form.get('language_to')

    # Get text from PDF : redirect to text zone 
    if not input_text:
        pdf_file = request.files['input_pdf']
        if not pdf_file:
            img_file = request.files['input_img']
            return importing_img(img_file)
        return importing_pdf(pdf_file)


    # Error checking
    error_message = None
    if not input_text and not pdf_file:
        error_message = "Please provide a text or a pdf for the translation."

    if transl_from == transl_to:
        error_message = f"Please select different languages for the translation.Checked: {transl_from} and {transl_to}"

    if not input_text and not pdf_file and (not transl_to or not transl_from):
        error_message = "Please check the button for the translation."

    if error_message:
        return render_template('translate.html', error_message=error_message)

    # Translation 
    if input_text :
        translation_result_json = translateText.make_trad(input_text, transl_from, transl_to)
        try:
            translation_result= translation_result_json[0]['translation_text']
        except Exception as e:
            error_message=f"La traduction a foiré | erreur: {translation_result_json}"
            return render_template('translate.html', error_message=error_message)
        # Translated text processing
        langs = f"Translation done from {transl_from} to {transl_to}."
        translation_result = translation_result.replace(".", ".<br />")
        session['translation_result'] = translation_result

        return render_template('translate.html', translation_result=session.get('translation_result'), langs=langs, translation_done=True)

    return render_template('translate.html', translation_result=None)


@app.route('/download_pdf')
def download_pdf():
    # Create the pdf from the processed text
    translation_result = session.get('translation_result')
    pdf_content = generate_pdf_content(translation_result)

    return Response(pdf_content, headers={
        'Content-Disposition': 'attachment; filename=translated_text.pdf',
        'Content-Type': 'application/pdf'
    })


# ------------------------------------------------------------------------- #
# ToolBox

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
    loader = UnstructuredImageLoader("imgTestOnem.jpg")
    data = loader.load()
    txt_from_img = data[0].page_content
    return txt_from_img

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

# ------------------------------------------------------------------------- #
# Running app

if __name__ == '__main__':
    # Debug:
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    app.run(debug=True, port=4995)
    # app.run(port=4995)
