# App
from flask import Flask, render_template, request, Response,session

#Creating PDF
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

app = Flask(__name__)
app.secret_key = '123'


@app.route('/', methods=['GET', 'POST'])
def translate_text():
    if request.method == 'POST':
        input_text = request.form['input_text']

        translation_result = input_text  # TRANSLATE FUNCTION

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
    # Create a buffer for the PDF content
    buffer = BytesIO()

    # Create a PDF canvas
    c = canvas.Canvas(buffer, pagesize=letter)

    # Set the font and font size
    c.setFont('Helvetica', 12)

    # Write the text to the PDF
    c.drawString(100, 700, text)

    # Save the PDF to the buffer
    c.save()

    # Reset the buffer position
    buffer.seek(0)

    # Return the PDF content as bytes
    return buffer.getvalue()

if __name__ == '__main__':
    app.run()