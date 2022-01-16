from distutils.command.config import config
import os
from posixpath import basename, dirname
from turtle import backward
import cv2
from pyzbar.pyzbar import decode, ZBarSymbol, ZBarConfig

from pdf2image import convert_from_path


# Make one method to decode the barcode
def BarcodeReader(image):

    # read the image in numpy array using cv2
    img = cv2.imread(image, 0)
    # Decode the barcode image
    detectedBarcodes = decode(img, zbarconfig=ZBarConfig.CFG_ADD_CHECK)
    print(detectedBarcodes)
    # If not detected then print the message
    if not detectedBarcodes:
        print("Barcode Not Detected or your barcode is blank/corrupted!")
    else:

        # Traverse through all the detected barcodes in image
        for barcode in detectedBarcodes:
            if barcode.data != "":
                # Print the barcode data
                print(barcode.type)
                return barcode.data.decode("utf-8")


def verification_digits_check(barcode):
    # barcode w/ verification digits = 83610000000-6 67560182202-5 20115002988-6 44240340039-7
    # barcode without v. digits = 83610000000675601822022011500298844240340039
    # barcode backwards = 93004304244 88920051102 20228106576 00000001638
    backwards_barcode = str(barcode)[::-1]
    return_string = barcode
    increment = 11
    index = 0

    while index < 45:
        ver_digit = crack_febraban_code(backwards_barcode[index : index + increment])
        return_string = (
            return_string[: index + increment]
            + str(ver_digit)
            + return_string[index + increment + 1 :]
        )
        index += increment

    return return_string


# 67560182202
# 0 1 2 3 4  5 6 7 8  9 10
# 2 0 2 2 8  1 0 6 5  7 6
# 2 1 2 1 2  1 2 1 2  1 2
# 4 0 4 2 16 1 0 6 10 7 12


def crack_febraban_code(number_str):
    addition = ""
    index = 0
    final_number = 0

    for character in number_str:
        number = int(character)
        if index == 0 or index % 2 == 0:
            addition += str(number * 2)
        else:
            addition += str(number)
        index += 1
    print(addition)
    for c in addition:
        final_number += int(c)

    res = 10 - (final_number % 10)
    # res = addition % 11
    return res


def remove_folder():
    if len(os.listdir(os.path.join(os.getcwd(), basename))):
        for file in os.listdir(os.path.join(os.getcwd(), basename)):
            print("here")
            os.remove(os.path.join(os.getcwd(), basename, file))
        os.rmdir(os.path.join(os.getcwd(), basename))


if __name__ == "__main__":
    # Take the image from user
    fileName = r"Boleto Ultragaz.pdf"
    imageRaw = os.path.join(r"/home/adrielom/Downloads/", fileName)
    pages = []

    basename = os.path.basename(imageRaw).split(".")[0]
    extension = os.path.basename(imageRaw).split(".")[-1]

    jpeg_config = {"quality": 100, "progressive": True, "optimize": True}

    if extension == "pdf":
        pages = convert_from_path(imageRaw, jpegopt=jpeg_config, fmt="jpeg", dpi=800)

    if not os.path.exists(basename):
        folder = os.mkdir(basename)

    index = 0
    result = ""

    for page in pages:
        image = os.path.join(basename, f"{basename}-{index}.jpeg")
        page.save(image, "jpeg")
        result = BarcodeReader(image)
        index += 1
    remove_folder()

    # print(result)
    # print(verification_digits_check(result))
