from flask import Flask, request, render_template, send_file
import cv2
import numpy as np
from PIL import Image
app = Flask(__name__)

MAX_COLOR_VALUE = 256
MAX_BIT_VALUE = 8


def make_image(data, resolution):
    image = Image.new("RGB", resolution)
    image.putdata(data)
    return image


def remove_n_least_significant_bits(value, n):
    value = value >> n
    return value << n


def get_n_least_significant_bits(value, n):
    value = value << MAX_BIT_VALUE - n
    value = value % MAX_COLOR_VALUE
    return value >> MAX_BIT_VALUE - n


def get_n_most_significant_bits(value, n):
    return value >> MAX_BIT_VALUE - n


def shit_n_bits_to_8(value, n):
    return value << MAX_BIT_VALUE - n

def encode(image_to_hide, image_to_hide_in, n_bits): #takes two image objects (image_to_hide and image_to_hide_in) and the number of LSBs to be used to hide the first image in the second image (n_bits).

    width, height = image_to_hide.size

    hide_image = image_to_hide.load()
    hide_in_image = image_to_hide_in.load()

    data = []

    for y in range(height):
        for x in range(width):

            # (107, 3, 10)
            # most sig bits
            r_hide, g_hide, b_hide = hide_image[x,y]

            r_hide = get_n_most_significant_bits(r_hide, n_bits)
            g_hide = get_n_most_significant_bits(g_hide, n_bits)
            b_hide = get_n_most_significant_bits(b_hide, n_bits)

            # remove lest n sig bits
            r_hide_in, g_hide_in, b_hide_in = hide_in_image[x,y]

            r_hide_in = remove_n_least_significant_bits(r_hide_in, n_bits)
            g_hide_in = remove_n_least_significant_bits(g_hide_in, n_bits)
            b_hide_in = remove_n_least_significant_bits(b_hide_in, n_bits)

            data.append((r_hide + r_hide_in,
                         g_hide + g_hide_in,
                         b_hide + b_hide_in))

    return make_image(data, image_to_hide.size)

def decode(image_to_decode, n_bits):
    width, height = image_to_decode.size
    encoded_image = image_to_decode.load()

    data = []

    for y in range(height):
        for x in range(width):
            r_encoded, g_encoded, b_encoded = encoded_image[x, y]

            r_encoded = get_n_least_significant_bits(r_encoded, n_bits)
            g_encoded = get_n_least_significant_bits(g_encoded, n_bits)
            b_encoded = get_n_least_significant_bits(b_encoded, n_bits)

            r_encoded = shit_n_bits_to_8(r_encoded, n_bits)
            g_encoded = shit_n_bits_to_8(g_encoded, n_bits)
            b_encoded = shit_n_bits_to_8(b_encoded, n_bits)

            data.append((r_encoded, g_encoded, b_encoded))

    return make_image(data, image_to_decode.size)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/encode", methods=["POST"])
def encode_flask():
    image_to_hide_input = request.files["hide_image"]
    image_to_hide_in_input = request.files["hide_in_image"]
    n_bits = int(request.form["n_bits"])

    type(image_to_hide_input)
    image_to_hide = Image.open(image_to_hide_input)
    image_to_hide_in = Image.open(image_to_hide_in_input)
    type(image_to_hide_input)
    encoded_image_path = "./encoded.png"
    encode(image_to_hide, image_to_hide_in, n_bits).save(encoded_image_path)
    return send_file(encoded_image_path, as_attachment=True, mimetype='image/png', download_name='encoded image')

@app.route("/decode", methods=["POST"])
def decode_flask():
    encoded_image_in = request.files["decode_image"]
    decoded_image_path = "./decoded.png"
    n_bits = int(request.form["n_bits"])
    encoded_image = Image.open(encoded_image_in)
    decode(encoded_image, n_bits).save(decoded_image_path)
    return send_file(decoded_image_path, as_attachment=True, mimetype='image/png', download_name='decoded image')

if __name__ == "__main__":
    app.run(debug=True)
