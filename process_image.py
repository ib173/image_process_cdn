import requests
import os
import base64
import shutil
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import tostring
import PIL
from PIL import Image
import io

def process_and_post(url):
    url = clean_img_link(url)
    name = download_image(url)
    img_path = process_image(name)
    guid = post_image(img_path)
    guid = concat_guid(guid)
    return guid


def clean_img_link(url):
    postfixes = ['.jpg', '.png', '.gif', '.jpeg']
    for postfix in postfixes:
        try:
            val = url.rindex(postfix)
            url = url[:val + len(postfix)]
            return url
        except:
            pass
    return # default image url as string

def concat_guid(guid_val):
    i = guid_val.index('<AttachmentGuid>')
    guid_final = guid_val[i+16:]
    guid_final = guid_final[0:guid_final.index("</")]
    return guid_final

def download_image(url):
    image_name = url[url.rindex('/')+1:]
    # print(image_name)
    # url = 'http://example.com/image.jpg'
    r = requests.get(url)
    # tmp/input.pdf
    i = Image.open(io.BytesIO(r.content))
    i.save("tmp/"+image_name)
    return image_name


def post_image(img_path):
    url = #REST Endpoint
    # img_path = "C:/Users/iannb/Desktop/news_image.jpg"
    with open(img_path, "rb") as image_file:
        image_base64 = base64.b64encode(image_file.read())
    image_base64_clean = image_base64.decode('ascii')
    image_str = str(image_base64_clean)
    statfile = os.stat(img_path)
    file_size = str(statfile.st_size)
    root = ET.Element('CMS_Attachment')
    ET.SubElement(root, "AttachmentName").text = "NEWTESTFILEtest"
    ET.SubElement(root, "AttachmentExtension").text = ".jpg"
    ET.SubElement(root, "AttachmentSize").text = file_size
    ET.SubElement(root, "AttachmentMimeType").text = "image/jpeg"
    ET.SubElement(root, "AttachmentImageWidth").text = "438"
    ET.SubElement(root, "AttachmentImageHeight").text = "604"
    ET.SubElement(root, "AttachmentBinary").text = image_str

    #This is also very important magic
    tree = ET.ElementTree(root)
    payload = tree.getroot()
    new_payload = tostring(payload)
    clean_payload = new_payload.decode('ascii')

    headers = {
        'Authorization': "",
        'Content-Type': "application/xml",
        'Host': ""}
    response = requests.post(url, headers=headers, data=clean_payload)
    #print(clean_payload)
    guid = response.text
    return guid

def process_image(name):
    img_path = 'tmp/' + name
    # print(img_path)
    with Image.open(img_path) as img:
        width, height = img.size
    image = read_image(img_path)
    image_crop = calc_square_crop(img)
    left, top, right, bottom = image_crop
    image = crop(image, left, top, right, bottom)
    image = resize_image(image, 500, 500)
    # image.show()
    return img_path


def read_image(path):
    try:
        image = PIL.Image.open(path)
        return image
    except Exception as e:
        print(e)

def resize_image(image, height, width):
    resized_image = image.resize((height, width) ,PIL.Image.ANTIALIAS)
    return resized_image
def crop(image, left, top, right, bottom):
    cropped = image.crop((left, top, right, bottom))
    return cropped
def calc_square_crop (image):
    #makes image square and centered
    width, height = image.size
    if width == height:
    #image is already square
        left = 0;
        right = width
        top = 0
        bottom = height
    elif width > height:
        #image is landscape
        left = (width - height)/2
        right = width - left
        top = 0
        bottom = height
    elif height > width:
        #image is portait
        top = (height - width)/2
        bottom = height - top
        left = 0
        right = width
    else:
        print ("how did this even happen")
    return ((left, top, right, bottom))
