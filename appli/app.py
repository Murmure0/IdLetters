# App
from flask import Flask, render_template, request, Response,session

# Creating PDF
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph

# import re
import sys
sys.path.insert(0, 'C:/Users/admindc/Desktop/finalProject/appli/toolBox/')
from toolBox import translateText

# ------------------------------------------------------------------------- #

app = Flask(__name__, static_folder="C:/Users/admindc/Desktop/finalProject/appli/static")

# Session
app.secret_key = '123' # you should not see that, shoo

# ------------------------------------------------------------------------- #
# Paths

@app.route('/', methods=['GET', 'POST'])
def translate_text():

    # Default
    if request.method != 'POST':
        return render_template('translate.html', translation_result=None)

    # Get the langs from/to translate
    transl_from = request.form.get('language_from')
    transl_to = request.form.get('language_to')

    # Get the text
    input_text = request.form.get('input_text')

    # Identify the language from the text given
    if transl_from == 'idk':
        transl_from = translateText.detec_lang(input_text)

    # Error checking
    if not transl_to or not transl_from:
        error_message = "Please check the button for the translation."
        return render_template('translate.html', error_message=error_message)

    if transl_from == transl_to:
        error_message = "Please select different languages for the translation."
        return render_template('translate.html', error_message=error_message)

    # Translation time
    translation_result = translateText.make_trad(input_text, transl_from, transl_to)

    # Translated text processing
    langs = f"Translation done from {transl_from} to {transl_to}."
    translation_result = translation_result.replace(".", ".<br />")
    session['translation_result'] = translation_result
    return render_template('translate.html', translation_result=session.get('translation_result'), langs=langs)

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
    app.run()