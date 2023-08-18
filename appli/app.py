# App
from flask import Flask, render_template, request, Response,session,flash

# External functions
import sys
sys.path.insert(0, 'appli/toolBox/')
from toolBox import translateText, fromFiles

# Debug
import logging

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

    # Default
    if request.method == 'GET':
        return render_template('translate.html', translation_result=None)

    # Get text from PDF/Img/Text zone:

    if 'input_pdf' in request.files:
        pdf_file = request.files['input_pdf']
        if pdf_file.filename != '':
            return fromFiles.importing_pdf(pdf_file)

    
    if 'input_img' in request.files:
        img_file = request.files['input_img']
        if img_file.filename != '':
            return fromFiles.importing_img(img_file)

    input_text = request.form.get('input_text')

    # Get the langs from/to translate
    transl_from = request.form.get('language_from')

    # Identify the language from the text given
    if transl_from == 'idk':
        # Pipeline -----------------------------------------------------------------------
        transl_from = translateText.detect_lang_ppl(input_text)
        # API -----------------------------------------------------------------------------
        # try :
        #     json_lang = translateText.detec_lang_API(input_text)
        #     transl_from = json_lang[0]['label']
        # except Exception as e:
        #     error_message=f'error : {json_lang}|{e}'
    transl_to = request.form.get('language_to')

    # Error checking
    error_message = None
    if not input_text and not pdf_file:
        error_message = "Please provide a text or a pdf for the translation."

    if transl_from == transl_to:
        error_message = f"Please select different languages for the translation.Checked: {transl_from} and {transl_to}"

    if error_message:
        return render_template('translate.html', error_message=error_message)

    # Translation 
    if input_text :

        # API -----------------------------------------------------------------------------
        # translation_result_json = translateText.make_trad_API(input_text, transl_from, transl_to)
        # try:
        #     translation_result= translation_result_json[0]['translation_text']
        # except Exception as e:
        #     error_message=f"La traduction a foiré | erreur: {translation_result_json}"
        #     return render_template('translate.html', error_message=error_message)

        # Pipeline -----------------------------------------------------------------------
        translation_result = translateText.make_trad_ppl(input_text, transl_from, transl_to)

        # Translated text processing
        langs = f"Translation done from {transl_from} to {transl_to}."
        translation_result = translation_result.replace(".", ".<br />")
        session['translation_result'] = translation_result

        return render_template('translate.html', translation_result=session.get('translation_result'), langs=langs, translation_done=True, input_text=input_text)

    return render_template('translate.html', translation_result=None)


@app.route('/download_pdf')
def download_pdf():
    # Create the pdf from the processed text
    translation_result = session.get('translation_result')
    pdf_content = fromFiles.generate_pdf_content(translation_result)

    return Response(pdf_content, headers={
        'Content-Disposition': 'attachment; filename=translated_text.pdf',
        'Content-Type': 'application/pdf'
    })

# ------------------------------------------------------------------------- #
# Running app

if __name__ == '__main__':
    # Debug:
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    app.run(debug=True, port=4995)
    # app.run(port=4995)
