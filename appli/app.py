# App
from flask import Flask, render_template, request, Response,session
import requests
# Creating PDF
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph

# Upload pdf
import os
from flask import flash, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from os import walk

# Extract txt from pdf
from langchain.document_loaders import UnstructuredFileLoader

# External functions
import sys
sys.path.insert(0, 'appli/toolBox/')
from toolBox import translateText


# Debug
import logging

# ------------------------------------------------------------------------- #

    # TODODOO :
    # estimer quelle longueur de texte on peut envoyer dans l'api

    # extraire le text du pdf grace à langChain : voir test/langChain.ipynb
    # afficher le text dans la zone de text et demander aux gens d'enlever 
    # les informations qui les concernent
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
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# ------------------------------------------------------------------------- #
# Paths

@app.route('/', methods=['GET', 'POST'])
def translate_text():
    # Default
    first_page = True
    if request.method == 'GET':
        return render_template('translate.html', translation_result=None, first_page=first_page)

    # Get the text
    # from the text zone
    input_text = request.form.get('input_text')
    # from pdf : uploading pdf in /uploads
    if not input_text:
        pdf_file = request.files['input_pdf']
        return importing_pdf(pdf_file, first_page)

    # Get the langs from/to translate
    transl_from = request.form.get('language_from')
    # Identify the language from the text given
    if transl_from == 'idk':
        transl_from = translateText.detec_lang(input_text)
    transl_to = request.form.get('language_to')

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
        translation_result = translateText.make_trad(input_text, transl_from, transl_to)
        try:
            translation_result= translation_result[0]['translation_text']
        except Exception as e:
            error_message=f"La traduction du pdf a foiré :{e}"
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

def importing_pdf(pdf_file, first_page=True):
    if pdf_file.filename == '':
            flash('No selected file')
            return render_template('translate.html', translation_result=None)
    if pdf_file and allowed_file(pdf_file.filename):
        filename = secure_filename(pdf_file.filename)
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        pdf_file.save(pdf_path)
        patate = extract_pdf_txt(pdf_path)
        first_page = False
        return render_template('translate.html', pdf_uploaded="pdf uploaded", patate=patate, first_page=first_page)
    return render_template('translate.html', pdf_uploaded="pdf not uploaded, extention allowed : .pdf", first_page=first_page)
    
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
    paragraph.drawOn(c, 100, 675)

    c.save()
    buffer.seek(0)
    return buffer.getvalue()

# ------------------------------------------------------------------------- #
# Running app

if __name__ == '__main__':
    # Debug:
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    app.run(debug=True)
    # app.run()
