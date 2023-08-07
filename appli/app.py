# App
from flask import Flask, render_template, request, Response,session

#Creating PDF
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from translator import myUpperCase
# ------------------------------------------------------------------------- #

app = Flask(__name__)

# Session
app.secret_key = '123'

# ------------------------------------------------------------------------- #

@app.route('/', methods=['GET', 'POST'])
def translate_text():

    if request.method == 'POST':
        input_text = request.form['input_text']

        translation_result = myUpperCase(input_text)  # TRANSLATE FUNCTION

        session['translation_result'] = translation_result
        return render_template('translate.html', translation_result=session.get('translation_result'))
    
    return render_template('translate.html', translation_result=None)

@app.route('/download_pdf')
def download_pdf():
    translation_result = session.get('translation_result')

    pdf_content = generate_pdf_content(translation_result)

    return Response(pdf_content, headers={
        'Content-Disposition': 'attachment; filename=translated_text.pdf',
        'Content-Type': 'application/pdf'
    })


def generate_pdf_content(text):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont('Helvetica', 12)
    c.drawString(100, 700, text)
    c.save()
    buffer.seek(0)
    return buffer.getvalue()

if __name__ == '__main__':
    app.run()