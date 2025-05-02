from flask import Flask, request, send_file, render_template
from flask_cors import CORS
from PIL import Image, ImageOps, ImageDraw, ImageEnhance
from rembg import remove
import io
import os

app = Flask(__name__)
CORS(app)

FILTER_OPTION = 'grayscale'

def apply_grayscale(image):
    return image.convert("L").convert("RGBA")

def create_vertical_gradient(size, top_color, bottom_color):
    width, height = size
    gradient = Image.new("RGBA", (width, height))
    draw = ImageDraw.Draw(gradient)
    for y in range(height):
        ratio = y / height
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        a = int(top_color[3] * (1 - ratio) + bottom_color[3] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b, a))
    return gradient

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    os.environ["U2NET_HOME"] = "/tmp"
    file = request.files['image']
    input_image = Image.open(file).convert("RGBA")
    user_image = remove(input_image).convert("RGBA")

    user_image = ImageOps.fit(user_image, (591, 945), centering=(0.5, 0.5))
    user_image = ImageEnhance.Color(user_image).enhance(0.0)
    user_image = ImageEnhance.Brightness(user_image).enhance(1)
    user_image = ImageEnhance.Contrast(user_image).enhance(1.2)

    blue_layer = create_vertical_gradient(
        user_image.size,
        top_color=(135, 170, 220, 255),
        bottom_color=(44, 86, 144, 255)
    )

    blended = Image.alpha_composite(blue_layer, user_image)

    template_overlay = Image.open("static/template_overlay.png").convert("RGBA")
    template_overlay = ImageOps.fit(template_overlay, blended.size)
    blended = Image.alpha_composite(blended, template_overlay)

    img_io = io.BytesIO()
    blended.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')

port = int(os.environ.get("PORT", 10000))
app.run(host='0.0.0.0', port=port)


