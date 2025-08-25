from rest_framework.validators import ValidationError
#  to see how it actually works check out models.ProductImages
def validate_image_size(file):
    max_image_size_kb = 200
    if file.size > max_image_size_kb * 1024:
        raise ValidationError(f'the size of the uploaded image can not be more that {max_image_size_kb} KB!')
    