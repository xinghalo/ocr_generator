import random
import utils
import tqdm
from PIL import Image, ImageFont, ImageDraw


name = ['产品名称', '品名', '产品名']
price = ['价格', '零售价', '建议零售价', '价目', 'RMB']
brand = ['品牌', '商标']

def get_source(sample_file_path):
    samples = []
    with open(sample_file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            arr = line.strip('\n').split('$')
            if len(arr) == 4:
                samples.append(arr)

    return samples

def get_key(arr, value, is_price=False):
    prefix = ''

    if random.random() > 0.1:
        index = random.randrange(1, len(arr))
        prefix = arr[index]+' : '

    if is_price and random.random() > 0.1:
        prefix += ' ¥ '

    prefix += value

    if is_price and random.random() > 0.5:
        prefix += ' 元 '

    return prefix

def generate(samples, threshold = 25):
    texts = []

    for sample in samples:

        name_text = get_key(name, sample[0])
        if len(name_text) <= threshold:
            texts.append(name_text)

        texts.append(get_key(price, sample[1], True))
        texts.append(get_key(price, sample[1], True))
        texts.append(get_key(price, sample[1], True))
        texts.append(get_key(price, sample[1], True))
        texts.append(get_key(price, sample[1], True))
        texts.append(get_key(price, sample[1], True))
        texts.append(get_key(price, sample[1], True))

        texts.append(get_key(brand, sample[2]))

        for property in sample[3].split('^'):
            if property != '':
                kv = property.split(':')
                texts.append("%s : %s" % (kv[0], kv[1]))

    return texts

def putContent2Image(content, background_image_path, font_path, add_rectangle=0, resize_rate=2):
    image = Image.open(background_image_path)

    image = image.resize((280, 32), Image.ANTIALIAS)

    # 确定字体的大小

    font_size = min(280//len(content), 28)

    # 获得文字起始点
    left_center_point = (random.randint(0, max(0, image.size[0] - font_size * len(content))),
                         (random.randint(0, 32 - font_size) + font_size) // 2)

    # 计算文字颜色，我这里只需要灰白的，直接RGB相等然后随机就行了
    color = utils.setColor(image)

    for character in content:
        image, points = putOneCharacter2Image(character, image, font_path, font_size, left_center_point, color)
        left_center_point = (max(points[1][0], points[2][0]), left_center_point[1])

    return image

def putOneCharacter2Image(character, background_image, font_path, font_size, left_center_point, color=None):
    background = background_image.convert('RGBA')
    font = ImageFont.truetype(font_path, font_size)
    width, height = font.getsize(character)

    txt = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    # 得到四个点的坐标
    points_in_txt = utils.getPointsOfImageRectangle(width, height)
    draw = ImageDraw.Draw(txt)
    draw.text((0, 0), character, font=font, fill=(255, 255, 255, 255))  # draw text, full opacity

    txt, points_in_txt = utils.augmentImage(txt, points_in_txt)
    points = utils.mergeBgimgAndTxtimgPoints(left_center_point, points_in_txt)
    #assert points[0][0] >= 0 and points[0][1] >= 0
    #assert points[2][0] <= background.size[0] and points[2][1] <= background.size[1]
    # out_image = Image.alpha_composite(background, txt)
    out_image = utils.mergeImageAtPoint(background, txt, tuple(points[0]), color)
    out_image = out_image.convert('RGB')
    return out_image, points

def text_to_image(texts):

    bg_img_list = utils.getBackgroundListFromDir('./background')
    font_list = utils.getFontListFromDir('./fonts')

    # 随机背景和字体
    for i in tqdm.tqdm(range(0, len(texts))):
        background_image_path, font_path = map(utils.getRandomOneFromList, [bg_img_list, font_list])
        image = putContent2Image(texts[i], background_image_path, font_path)
        # part_images = utils.cropImageByPoints(image, points)
        saveImage(image, i)
        save_annotation(texts[i], i)

def saveImage(image, image_index):
    image_save_dir = '/data1/ocr/ctc/images'
    utils.saveImage2Dir(image, image_save_dir, image_name=str(image_index))

def save_annotation(content, image_index):
    ann_name = ''.join([str(image_index), '.jpg'])
    ann_path = '/data1/ocr/ctc/label.txt'
    with open(ann_path, 'a+', encoding='utf-8') as file:
        file.write("%s %s\n" % (ann_name, content))

if __name__ == '__main__':
    samples = get_source('/Users/xingoo/PycharmProjects/ocr-online/tests/sample.csv')
    texts = generate(samples)
    text_to_image(texts)

    # print(random.randrange(1, 3))
    # print(random.randrange(1, 3))
    # print(random.randrange(1, 3))
    # print(random.randrange(1, 3))
    # print(random.randrange(1, 3))