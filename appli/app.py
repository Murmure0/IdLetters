# App
from flask import Flask, render_template, request, Response,session

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

# External functions
import sys
sys.path.insert(0, 'C:/Users/admindc/Desktop/finalProject/appli/toolBox/')
from toolBox import translateText

# Debug
import logging

# ------------------------------------------------------------------------- #
# APP
app = Flask(__name__, static_folder="C:/Users/admindc/Desktop/finalProject/appli/static")

# Session
app.secret_key = '123' # you should not see that, shoo

# ------------------------------------------------------------------------- #
# PDF upload
UPLOAD_FOLDER = "appli/uploads/"
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# ------------------------------------------------------------------------- #
# Paths

@app.route('/', methods=['GET', 'POST'])
def translate_text():
    # Default
    if request.method != 'POST':
        return render_template('translate.html', translation_result=None)

    # Get the text
    input_text = request.form.get('input_text')
    pdf_file = request.files['input_pdf']
    # pdf_file = request.files.get('input_pdf')
    # Get the langs from/to translate
    transl_from = request.form.get('language_from')
    # Identify the language from the text given
    if transl_from == 'idk':
        transl_from = translateText.detec_lang(input_text)
    transl_to = request.form.get('language_to')

    # Error checking
    if not transl_to or not transl_from:
        error_message = "Please check the button for the translation."
        return render_template('translate.html', error_message=error_message)

    if not input_text and not pdf_file:
        error_message = "Please provide a text or a pdf for the translation."
        return render_template('translate.html', error_message=error_message)

    if transl_from == transl_to:
        error_message = "Please select different languages for the translation."
        return render_template('translate.html', error_message=error_message)
    

    # Translation of text
    if input_text :
        translation_result = translateText.make_trad(input_text, transl_from, transl_to)

        # Translated text processing
        langs = f"Translation done from {transl_from} to {transl_to}."
        translation_result = translation_result.replace(".", ".<br />")
        session['translation_result'] = translation_result
        return render_template('translate.html', translation_result=session.get('translation_result'), langs=langs)
    # Process pdf
    elif pdf_file :
        if pdf_file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if pdf_file and allowed_file(pdf_file.filename):
            filename = secure_filename(pdf_file.filename)
            pdf_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # session['filename'] = filename
            # session['pdf_file'] = pdf_file
            
            # submit_action_pdf()
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


# @app.route('/submit_action_pdf', methods=['GET','POST'])
# def submit_action_pdf():
#     pdf_file = session.get('pdf_file')
#     filename = session.get('filename')
#     if not pdf_file:
#         return render_template('index copy.html')
#     if not filename: # pas de filename
#         return render_template('index.html')
#     pdf_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#     return render_template('translate.html', translation_result=None)
    # logging(f"name pdf = {filename}")
#     return redirect(url_for('download_file', name=filename))

# @app.route('/uploads/<name>')
# def download_file(name):
#     return send_from_directory(app.config["UPLOAD_FOLDER"], name)

# ------------------------------------------------------------------------- #
# ToolBox

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