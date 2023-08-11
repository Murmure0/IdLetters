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

app = Flask(__name__)

# Session
app.secret_key = '123' # you should not see that, shoo

# ------------------------------------------------------------------------- #
# Paths

@app.route('/', methods=['GET', 'POST'])
def translate_text():

    if request.method != 'POST':
        return render_template('translate.html', translation_result=None)
    
    # Get the text, the task (translate/Dectect lang), the lang to translate
    input_text = request.form.get('input_text')
    task = request.form.get('task')
    transl_to = request.form.get('language_to')

    if task == 'translate':
        transl_from = request.form.get('language_from')                
    elif task == 'detect':
        transl_from = translateText.detec_lang(input_text)

    if transl_from == transl_to:
        error_message = "Please select different languages for the translation."
        return render_template('translate.html', error_message=error_message)

    # Translation time
    translation_result = translateText.make_trad(input_text, transl_from, transl_to)

    # Translated text processing
    translation_result = translation_result.replace(".", ".\n")
    session['translation_result'] = translation_result
    return render_template('translate.html', translation_result=session.get('translation_result'))

@app.route('/download_pdf')
def download_pdf():
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

    # c.drawString(100, 700, text)
    styles = getSampleStyleSheet()
    style = styles['Normal']

    # Create a Paragraph object with the text
    paragraph = Paragraph(text, style)

    # Draw the Paragraph on the canvas
    paragraph.wrapOn(c, 400, 800)  # Adjust width and height as needed
    paragraph.drawOn(c, 100, 700)

    c.save()
    buffer.seek(0)
    return buffer.getvalue()

# def generate_pdf_content(text):
#     buffer = BytesIO()
#     c = canvas.Canvas(buffer, pagesize=letter)
#     c.setFont('Helvetica', 12)

#     lines = text.split('\n')
#     y_position = 700 

#     styles = getSampleStyleSheet()
#     style = styles['Normal']

#     # Create a Paragraph object with the text
#     paragraph = Paragraph(text, style)

#     # Draw the Paragraph on the canvas

#     for line in lines:
#         paragraph = Paragraph(line, style)
#         # c.drawString(100, y_position, line)
#         # y_position -= 15 

#     paragraph.wrapOn(c, 400, 1000)  # Adjust width and height as needed
#     paragraph.drawOn(c, 100, 700)
#     c.save()
#     buffer.seek(0)
#     return buffer.getvalue()



# ------------------------------------------------------------------------- #
# Running app

if __name__ == '__main__':
    app.run()