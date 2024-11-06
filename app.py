import os
from flask import Flask, render_template, request, send_file, redirect, url_for
from PIL import Image
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/images'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit upload size to 16 MB

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def get_next_directory():
    """Generate the next incrementally numbered directory."""
    existing_dirs = [int(name) for name in os.listdir(app.config['UPLOAD_FOLDER']) if name.isdigit()]
    next_dir = str(max(existing_dirs) + 1) if existing_dirs else '1'
    new_dir_path = os.path.join(app.config['UPLOAD_FOLDER'], next_dir)
    os.makedirs(new_dir_path, exist_ok=True)
    return new_dir_path

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'webp_file' not in request.files:
            return redirect(request.url)
        
        webp_file = request.files['webp_file']
        
        if webp_file.filename == '':
            return redirect(request.url)
        
        if webp_file and webp_file.filename.lower().endswith('.webp'):
            # Get the next available directory for this upload
            upload_dir = get_next_directory()
            webp_path = os.path.join(upload_dir, 'image.webp')
            webp_file.save(webp_path)
            
            # Convert to JPG
            jpg_path = os.path.join(upload_dir, 'image.jpg')
            with Image.open(webp_path) as img:
                rgb_im = img.convert('RGB')
                rgb_im.save(jpg_path, 'JPEG')

            # Convert to PNG
            png_path = os.path.join(upload_dir, 'image.png')
            with Image.open(webp_path) as img:
                img.save(png_path, 'PNG')

            return render_template('index.html', jpg_path=jpg_path, png_path=png_path, convert_done=True)

    return render_template('index.html')

@app.route('/download/<path:filename>', methods=['GET'])
def download(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
