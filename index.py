from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from googletrans import Translator, LANGUAGES  # Install this package using `pip install googletrans==4.0.0-rc1`
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all origins

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize the translator
translator = Translator()

# In-memory storage for FAQs
faqs = []

# Translation function using Google Translate API
def translate_text(text, target_language):
    try:
        translation = translator.translate(text, dest=target_language)
        return translation.text
    except Exception as e:
        raise Exception(f"Translation failed: {str(e)}")

# Fetch all FAQs
@app.route('/faqs', methods=['GET'])
def get_faqs():
    return jsonify(faqs)

# Fetch a single FAQ by ID
@app.route('/faqs/<int:faq_id>', methods=['GET'])
def get_faq(faq_id):
    faq = next((f for f in faqs if f["id"] == faq_id), None)
    if faq is None:
        return jsonify({"error": "FAQ not found"}), 404
    return jsonify(faq)

# Serve uploaded images
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Create a new FAQ
@app.route('/faqs', methods=['POST'])
def create_faq():
    question = request.form.get('question')
    answer = request.form.get('answer')
    image = request.files.get('image')

    if not question:
        return jsonify({"error": "Bad request, 'question' is required"}), 400

    new_faq = {
        'id': faqs[-1]['id'] + 1 if faqs else 1,
        'question': question,
        'answer': answer if answer else ""
    }

    if image:
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        new_faq['image'] = f"/uploads/{filename}"
    print(new_faq)
    faqs.append(new_faq)
    return jsonify(new_faq), 201

# Update an FAQ
@app.route('/faqs/<int:faq_id>', methods=['PUT'])
def update_faq(faq_id):
    faq = next((f for f in faqs if f["id"] == faq_id), None)
    if faq is None:
        return jsonify({"error": "FAQ not found"}), 404

    question = request.form.get('question')
    answer = request.form.get('answer')
    image = request.files.get('image')

    if question:
        faq['question'] = question
    if answer:
        faq['answer'] = answer
    if image:
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        faq['image'] = f"/uploads/{filename}"

    return jsonify(faq)

# Delete an FAQ
@app.route('/faqs/<int:faq_id>', methods=['DELETE'])
def delete_faq(faq_id):
    faq = next((f for f in faqs if f["id"] == faq_id), None)
    if faq is None:
        return jsonify({"error": "FAQ not found"}), 404
    faqs.remove(faq)
    return jsonify({'result': True})

# Translation endpoint
@app.route('/translate', methods=['POST'])
def translate():
    if not request.json or 'text' not in request.json or 'targetLanguage' not in request.json:
        return jsonify({"error": "Bad request, 'text' and 'targetLanguage' are required"}), 400
    
    text = request.json['text']
    target_language = request.json['targetLanguage']

    if target_language not in LANGUAGES:
        return jsonify({"error": "Unsupported target language"}), 400

    try:
        translated_text = translate_text(text, target_language)
        return jsonify({"translatedText": translated_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True,port=5050,host="0.0.0.0")
