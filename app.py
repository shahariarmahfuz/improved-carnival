import os
import uuid
import base64
import mimetypes
from flask import Flask, send_from_directory, jsonify
from google import genai
from google.genai import types

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/images'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def save_binary_file(file_name, data):
    with open(file_name, "wb") as f:
        f.write(data)

def generate_image(prompt):
    client = genai.Client(api_key=os.environ.get("AIzaSyA6a7BCzd0ut64DW6aTeOXDPwBQUar7zok"))
    
    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)],
        )
    ]
    
    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192,
        response_modalities=["image", "text"],
        response_mime_type="text/plain",
    )
    
    for chunk in client.models.generate_content_stream(
        model="gemini-2.0-flash-exp-image-generation",
        contents=contents,
        config=generate_content_config,
    ):
        if chunk.candidates and chunk.candidates[0].content.parts:
            if chunk.candidates[0].content.parts[0].inline_data:
                unique_id = str(uuid.uuid4()).upper()
                inline_data = chunk.candidates[0].content.parts[0].inline_data
                file_extension = mimetypes.guess_extension(inline_data.mime_type)
                filename = f"{unique_id}_output{file_extension}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                save_binary_file(file_path, inline_data.data)
                return filename
    return None

@app.route('/gen')
def generate_image_route():
    prompt = request.args.get('p')
    if not prompt:
        return jsonify({"error": "Missing prompt parameter"}), 400
    
    try:
        filename = generate_image(prompt)
        if filename:
            image_url = f"/images/{filename}"
            return jsonify({
                "image_url": image_url,
                "download_url": f"/download/{filename}"
            })
        return jsonify({"error": "Image generation failed"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/download/<filename>')
def download_image(filename):
    return send_from_directory(
        app.config['UPLOAD_FOLDER'], 
        filename, 
        as_attachment=True
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
