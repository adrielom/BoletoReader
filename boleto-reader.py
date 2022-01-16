#!/usr/bin/env python3

import os
from posixpath import basename
import sys
import cv2
from pyzbar.pyzbar import decode, ZBarConfig

from pdf2image import convert_from_path
import telegram_send

import pdfplumber

# Method to read the barcode
def BarcodeReader(image):

    img = cv2.imread(image, 0)
    detectedBarcodes = decode(img, zbarconfig=ZBarConfig.CFG_ADD_CHECK)

    if not detectedBarcodes:
        print("Barcode Not Detected or your barcode is blank/corrupted!")
    else:
        for barcode in detectedBarcodes:
            if barcode.data != "":
                return barcode.data.decode("utf-8")


# Method to concatenate the verification digits
def verification_digits_check(barcode):
    backwards_barcode = str(barcode)[::-1]
    return_string = ""
    increment = 11
    index = 0

    while index < 44:
        barcode_chunk = backwards_barcode[index : index + increment]
        ver_digit = crack_febraban_code(barcode_chunk)
        return_string += str(ver_digit) + barcode_chunk
        index += increment

    return return_string[::-1]


# Method to extract the febraban digit
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
    for c in addition:
        final_number += int(c)

    res = 10 - (final_number % 10)
    return res


# Cleans up temporary folders
def remove_folder():
    if len(os.listdir(os.path.join(os.getcwd(), basename))):
        for file in os.listdir(os.path.join(os.getcwd(), basename)):
            os.remove(os.path.join(os.getcwd(), basename, file))
        os.rmdir(os.path.join(os.getcwd(), basename))


# Reads the pdf info
def pdf_reader(path):
    pdf = pdfplumber.open(path)
    page = pdf.pages[0]
    text = page.extract_text()
    pdf.close()
    return text


if __name__ == "__main__":
    directory_path = "."

    files = [f for f in os.listdir(".") if os.path.isfile(f)]
    if len(files) <= 1:
        print(f"no documents")
        sys.exit()

    for fileName in files:
        documentRaw = os.path.join(directory_path, fileName)
        pages = []

        basename = os.path.basename(documentRaw).split(".")[0]
        extension = os.path.basename(documentRaw).split(".")[-1]

        if extension == "py":
            continue

        print(fileName)
        jpeg_config = {"quality": 100, "progressive": True, "optimize": True}

        if extension == "pdf":
            pages = convert_from_path(
                documentRaw, jpegopt=jpeg_config, fmt="jpeg", dpi=800
            )

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

        pdf_reader(documentRaw)
        print(result)
        telegram_send.send(
            messages=[
                f"Conta \n {pdf_reader(documentRaw)} \n\n CÓDIGO DE BARRAS -> \n\n",
                f"{verification_digits_check(result)}",
                f"--------------------------",
            ]
        )

        os.remove(fileName)
