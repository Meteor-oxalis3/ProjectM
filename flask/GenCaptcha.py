import random
import string
from io import BytesIO
from captcha.image import ImageCaptcha

def captcha(send_file, session):
    image = ImageCaptcha(width=200, height=100)
    captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    
    # 保存验证码到 session
    session['captcha_text'] = captcha_text.upper()
    
    # 生成验证码图片
    image_data = image.generate(captcha_text)

    img_io = BytesIO()
    img_io.write(image_data.getvalue())
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png')