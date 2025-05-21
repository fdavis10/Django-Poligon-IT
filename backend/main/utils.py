from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile


def compress_image(image_field, quality=75, max_size=(837, 900)):
    img = Image.open(image_field)
    img.convert('RGB')
    img.thumbnail(max_size)

    buffer = BytesIO()
    img.save(buffer, format='JPEG', quality=quality)
    return ContentFile(buffer.getvalue)