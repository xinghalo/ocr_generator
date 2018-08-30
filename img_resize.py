import pathlib
from PIL import Image
image_path_list = []
image_path_list.extend([path for path in pathlib.Path('./background').rglob('*.*')])
resize_rate = 0.5
for image in image_path_list:
    print(image)
    img = Image.open(image)
    img = img.resize((int(img.size[0] * resize_rate), int(img.size[1] * resize_rate)))
    img.save(image)