# App
from flask import Flask, render_template, request, Response,session,flash

# External functions
import sys
sys.path.insert(0, 'appli/toolBox/')
from toolBox import translateText, fromFiles

# Upload pdf
import os
from os import walk
from werkzeug.utils import secure_filename

# Extract txt from pdf
from langchain.document_loaders import UnstructuredFileLoader

# Extract txt from img
from langchain.document_loaders.image import UnstructuredImageLoader
import cv2
import numpy as np

# Debug
import logging

# ------------------------------------------------------------------------- #
# APP
app = Flask(__name__)

# Session
app.secret_key = '123' # you should not see that, shoo

# ------------------------------------------------------------------------- #
# PDF upload 

# UPLOAD_FOLDER = "appli\\uploads"
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

    # # Get text from PDF/Img/Text zone:
    selected_language = request.form['language']
    session['prev_lang'] = "en"
    session['title'] = 'Translate your files from the selected language to the desired one'
    # session['body'] = "You don't know from which language to translate ? Choose "Identify for me" but the process will be slower."
    if selected_language:
        try:
            session['title'] = translateText.make_trad_ppl(session.get('title'), session.get('prev_lang'), selected_language)
        except OSError as error:
            error_message = f"Sorry, translation from {transl_from} to {transl_to} not available yet."
        return render_template('translate.html', title=session.get('title'))


    if 'input_pdf' in request.files:
        pdf_file = request.files['input_pdf']
        if pdf_file.filename != '':
            return importing_pdf(pdf_file)

    
    if 'input_img' in request.files:
        img_file = request.files['input_img']
        if img_file.filename != '':
            return importing_img(img_file)

    input_text = request.form.get('input_text')

    # Get the langs from/to translate
    transl_from = request.form.get('language_from')
    transl_to = request.form.get('language_to')

    # Identify the language from the text given
    if transl_from == 'idk':
        # Pipeline ------------------------------------------------------------------------
        try :

            transl_from = translateText.detect_lang_ppl(input_text)

        except Exception as e:
            error_message= f"Sorry the translation from {transl_from} to {transl_to} is not availble."
        # API -----------------------------------------------------------------------------
        # try :
        #     json_lang = translateText.detec_lang_API(input_text)
        #     transl_from = json_lang[0]['label']
        # except Exception as e:
        #     error_message=f'error : {json_lang}|{e}'

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
        try:
            if len(input_text) > 500:
                translation_result = translateText.large_txt_translation(input_text,transl_from, transl_to)
            else :
                translation_result = translateText.make_trad_ppl(input_text, transl_from, transl_to)
        except OSError as error:
            error_message = f"Sorry, translation from {transl_from} to {transl_to} not available yet."

        if error_message:
            return render_template('translate.html', error_message=error_message)
        # Translated text processing
        langs = f"Translation done from {transl_from} to {transl_to}."
        translation_result = translation_result.replace(". ", ".<br />")
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


## IMPORT TXT FROM IMG ------------------------------------------------------------------------------------
def importing_img(img_file):
    if img_file.filename == '':
            flash('No selected file')
            return render_template('translate.html', translation_result=None)
    if img_file and allowed_file(img_file.filename):
        filename = secure_filename(img_file.filename)
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        img_file.save(img_path)
        txt_from_img = extract_img_txt(img_path, filename)
        return render_template('translate.html', img_uploaded="img uploaded", txt_from_img=txt_from_img)
    return render_template('translate.html', img_uploaded="img not uploaded, extention allowed : .jpg, .jpeg, .png")

def extract_img_txt(img_path, filename):
    # Enhance Brightness:
    # image = cv2.imread(img_path)
    # brightness_factor=1.2
    # contrast_factor=1.2
    # enhanced_image = cv2.convertScaleAbs(image, alpha=contrast_factor, beta=brightness_factor)
    # # enhanced_image.save(img_path)
    # output_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    # cv2.imwrite(output_path, enhanced_image)

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


# ------------------------------------------------------------------------- #
# Running app

if __name__ == '__main__':
    # Debug:
    # logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # app.run(debug=True, port=4995)
    app.run(port=4995)
