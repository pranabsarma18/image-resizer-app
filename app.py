from flask import Flask, render_template, request, send_file
from PIL import Image
from io import BytesIO

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/resize', methods=['POST'])
def resize_image():
    try:
        if 'file' not in request.files:
            return "No file part"

        file = request.files['file']

        if file.filename == '':
            return "No selected file"

        # Get user-specified dimensions (default to 300x300 if not provided)
        width = int(request.form.get('width', 300))
        height = int(request.form.get('height', 300))

        # Get user-specified target size in kilobytes (default to 1024 KB if not provided)
        target_size_kb = int(request.form.get('target_size_kb', 1024))

        # Resize the image
        original_image = Image.open(file)
        resized_image = original_image.resize((width, height))

        # Compress the image to achieve the target size
        output_buffer = BytesIO()
        quality = 95  # Initial quality value

        while True:
            resized_image.save(output_buffer, format="JPEG", quality=quality)
            size_kb = len(output_buffer.getvalue()) / 1024

            if size_kb <= target_size_kb:
                break

            # Adjust quality to achieve the target size
            quality -= 5

            # Break the loop if quality drops too low
            if quality <= 0:
                return "Error: Unable to achieve the target size."

            # Reset the buffer for the next iteration
            output_buffer.seek(0)
            output_buffer.truncate()

        # Send the resized and compressed image as a response
        output_buffer.seek(0)
        return send_file(output_buffer, mimetype='image/jpeg', as_attachment=True, download_name='resized_image.jpg')

    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
