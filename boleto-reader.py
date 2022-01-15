import os
from posixpath import basename, dirname
import cv2
from pyzbar.pyzbar import decode, ZBarSymbol

from pdf2image import convert_from_path


# Make one method to decode the barcode
def BarcodeReader(image):

    # read the image in numpy array using cv2
    img = cv2.imread(image, 0)
    # Decode the barcode image
    detectedBarcodes = decode(img, symbols=[ZBarSymbol.I25])

    # If not detected then print the message
    if not detectedBarcodes:
        print("Barcode Not Detected or your barcode is blank/corrupted!")
    else:

        # Traverse through all the detected barcodes in image
        for barcode in detectedBarcodes:

            # Locate the barcode position in image
            (x, y, w, h) = barcode.rect

            # Put the rectangle in image using
            # cv2 to heighlight the barcode
            cv2.rectangle(
                img, (x - 10, y - 10), (x + w + 10, y + h + 10), (255, 0, 0), 2
            )

            if barcode.data != "":
                # Print the barcode data
                print(barcode.type)
                return barcode.data.decode("utf-8")


def remove_folder():
    if len(os.listdir(os.path.join(os.getcwd(), basename))):
        for file in os.listdir(os.path.join(os.getcwd(), basename)):
            print("here")
            os.remove(os.path.join(os.getcwd(), basename, file))
        os.rmdir(os.path.join(os.getcwd(), basename))


if __name__ == "__main__":
    # Take the image from user
    fileName = r"Boleto unid. 301 01 Eldorado 122021.pdf"
    imageRaw = os.path.join(r"/home/adrielom/Downloads/", fileName)
    # imageRaw = r"/home/adrielom/Documentos/Contas/Boleto Ultragaz.pdf"
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

    print(result)
