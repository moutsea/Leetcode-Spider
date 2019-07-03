from PIL import Image, ImageDraw, ImageFont


# text是需要生成的标题
# slug是题目标识，用来存储文件
def add_text(img, slug, text):
    draw = ImageDraw.Draw(img)
    fillcolor = "#FFFFFF"
    width, height = img.size
    sz = 34
    paragraph = [text]
    words = text.split(' ')
    l = 0
    for i in words:
        l += len(i)

    # 超过20个字符分成两行
    if l > 20:
        sz = 30
        strlen = 0
        sr = []
        id = 0
        while strlen + id < 20:
            strlen += len(words[id])
            sr.append(words[id])
            id += 1
        paragraph[0] = ' '.join(sr)
        paragraph.append(' '.join(words[id:]))
    myfont = ImageFont.truetype('/Library/Fonts/Arial.ttf', size=sz)
    for i in range(len(paragraph)):
        draw.text((width / 2 - len(paragraph[i]) * 8, height - 50 * (2 - i) - 15), paragraph[i], font=myfont,
                  fill=fillcolor)
    # 路径，需要修改成你自己的路径
    img.save('/Users/charles.yin/Documents/leetcode/picture/' + slug + '.jpg', 'jpeg')
    return 0


def generate_image(slug, title):
    image = Image.open('/Users/charles.yin/Documents/leetcode/picture/empty.png')
    add_text(image, slug, title)
    return '/Users/charles.yin/Documents/leetcode/picture/' + slug + '.jpg'
