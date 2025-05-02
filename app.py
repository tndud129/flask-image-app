from flask import Flask, request, send_file, render_template
from flask_cors import CORS
from PIL import Image, ImageOps, ImageDraw
from PIL import ImageEnhance
from rembg import remove
from PIL import Image
import io
import os

app = Flask(__name__)
CORS(app)

# ✅ 적용할 스크린 옵션: 'grayscale' 또는 'original'
FILTER_OPTION = 'grayscale'

# ⚫ 흑백 필터
def apply_grayscale(image):
    return image.convert("L").convert("RGBA")

# ✅ 그라데이션 배경 생성 함수 (위로 올림)
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
    file = request.files['image']

    # ✅ 1. 배경 제거
    input_image = Image.open(file).convert("RGBA")
    user_image = remove(input_image).convert("RGBA")


    # ✅ 2. 크기 맞춤
    user_image = ImageOps.fit(user_image, (591, 945), centering=(0.5, 0.5))

    # ✅ 3. 이미지 보정: 채도 0, 밝기 +20%, 대비 +50%
    user_image = ImageEnhance.Color(user_image).enhance(0.0)
    user_image = ImageEnhance.Brightness(user_image).enhance(1)
    user_image = ImageEnhance.Contrast(user_image).enhance(1.2)

    # ✅ 4. 그라데이션 배경 생성
    blue_layer = create_vertical_gradient(
        user_image.size,
        top_color=(135, 170, 220, 255),
        bottom_color=(44, 86, 144, 255)
    )

    # ✅ 5. 배경 + 이미지 합성
    blended = Image.alpha_composite(blue_layer, user_image)

    # ✅ 6. 템플릿 오버레이 추가
    template_overlay = Image.open("static/template_overlay.png").convert("RGBA")
    template_overlay = ImageOps.fit(template_overlay, blended.size)
    blended = Image.alpha_composite(blended, template_overlay)

    # ✅ 7. 이미지 전송
    img_io = io.BytesIO()
    blended.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')


if __name__ != '__main__':
    app = app


