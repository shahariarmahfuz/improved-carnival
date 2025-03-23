# app.py
import os
import uuid
import base64
import mimetypes
from flask import Flask, request, send_from_directory, jsonify
import google.generativeai as genai
from google.generativeai.types import GenerationConfig

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/images'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def save_binary_file(file_path, data):
    with open(file_path, "wb") as f:
        f.write(data)

def generate_image(prompt):
    try:
        # Initialize Generative AI
        genai.configure(api_key=os.environ.get("AIzaSyA6a7BCzd0ut64DW6aTeOXDPwBQUar7zok"))
        model = genai.GenerativeModel('gemini-2.0-flash-exp-image-generation')

        # Generate content
        response = model.generate_content(
            contents=[prompt],
            generation_config=GenerationConfig(
                temperature=1,
                top_p=0.95,
                top_k=40,
                max_output_tokens=8192,
            )
        )

        # Process response
        if response and response.parts:
            # Generate unique filename
            unique_id = uuid.uuid4().hex
            file_extension = ".png"
            filename = f"{unique_id}_output{file_extension}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # Decode and save image
            image_data = base64.b64decode(response.parts[0].text)
            save_binary_file(file_path, image_data)
            return filename
            
        return None

    except Exception as e:
        print(f"Error in image generation: {str(e)}")
        return None

@app.route('/gen', methods=['GET'])
def handle_image_generation():
    prompt = request.args.get('p')
    if not prompt:
        return jsonify({"error": "Prompt parameter 'p' is required"}), 400

    try:
        generated_filename = generate_image(prompt)
        if generated_filename:
            return jsonify({
                "status": "success",
                "image_url": f"/images/{generated_filename}",
                "download_link": f"/download/{generated_filename}"
            })
        return jsonify({"error": "Failed to generate image"}), 500

    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "Internal server error"
        }), 500

@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        filename,
        mimetype='image/png'
    )

@app.route('/download/<filename>')
def download_image(filename):
    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        filename,
        as_attachment=True,
        download_name=filename
    )

@app.route('/')
def health_check():
    return jsonify({
        "status": "active",
        "service": "Gemini Image Generator",
        "version": "1.0.0"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
