from flask import Flask, request, Response
import base64
import mimetypes
from google import genai
from google.genai import types

app = Flask(__name__)

# সরাসরি API কী ব্যবহার করুন
API_KEY = "AIzaSyA6a7BCzd0ut64DW6aTeOXDPwBQUar7zok"

def generate_image(prompt):
    client = genai.Client(api_key=API_KEY)  # সরাসরি API কী ব্যবহার

    model = "gemini-2.0-flash-exp-image-generation"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt),
            ],
        ),
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
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if chunk.candidates and chunk.candidates[0].content and chunk.candidates[0].content.parts:
            if chunk.candidates[0].content.parts[0].inline_data:
                inline_data = chunk.candidates[0].content.parts[0].inline_data
                return {
                    "mime_type": inline_data.mime_type,
                    "data": base64.b64encode(inline_data.data).decode('utf-8')
                }
    return None

@app.route('/gen')
def generate():
    prompt = request.args.get('p', '')
    if not prompt:
        return "Please provide a prompt using ?p= parameter", 400
    
    image_data = generate_image(prompt)
    if not image_data:
        return "Failed to generate image", 500

    html = f"""
    <html>
        <body>
            <h1>Generated Image for: {prompt}</h1>
            <img src="data:{image_data['mime_type']};base64,{image_data['data']}" 
                 style="max-width: 100%; height: auto;">
        </body>
    </html>
    """
    return Response(html, mimetype='text/html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
