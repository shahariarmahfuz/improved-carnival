from flask import Flask, request, Response
import base64
import google.generativeai as genai

app = Flask(__name__)

# সরাসরি API কী ব্যবহার করুন
API_KEY = "AIzaSyA6a7BCzd0ut64DW6aTeOXDPwBQUar7zok"

# Gemini AI ক্লায়েন্ট ইনিশিয়ালাইজ করুন
genai.configure(api_key=API_KEY)

def generate_image(prompt):
    model = genai.GenerativeModel("gemini-pro-vision")  # মডেল সিলেক্ট করুন
    
    # প্রম্পট ব্যবহার করে কন্টেন্ট তৈরি করুন
    contents = [
        {
            "role": "user",
            "parts": [{"text": prompt}]
        }
    ]
    
    # জেনারেশন কনফিগারেশন
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
    }

    # ইমেজ জেনারেট করুন
    response = model.generate_content(
        contents=contents,
        generation_config=generation_config,
    )

    # রেসপন্স থেকে ইমেজ ডেটা এক্সট্রাক্ট করুন
    if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
        if response.candidates[0].content.parts[0].inline_data:
            inline_data = response.candidates[0].content.parts[0].inline_data
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
