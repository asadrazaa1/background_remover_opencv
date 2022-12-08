import os
from time import sleep

import cv2
import mediapipe as mp
import numpy as np
import face_recognition as fr
from uuid import uuid4
from PIL import Image
from django.core.files import File
from rest_framework import status
from rest_framework.response import Response

from processimages.models import ProcessedImage


def remove_background(img_path):
    # Initialize mediapipe objects
    mp_selfie_segmentation = mp.solutions.selfie_segmentation
    selfie_segmentation = mp_selfie_segmentation.SelfieSegmentation(model_selection=1)

    # Read image
    image = cv2.imread(img_path)

    # Take dimensions of image
    h, w, _ = image.shape

    # Make background image
    img = np.ones((h, w, 3), dtype=np.uint8)
    img = 255 * img

    # Set extra sides and upper sides
    x_adder = int(w / 5)
    y_adder = int(h / 5)

    # Find face locations in the image
    face_locations = fr.face_locations(image)

    # Set output images
    output_images = []

    for (top, right, bottom, left) in face_locations:

        for i in range(y_adder):
            if top <= 0:
                break
            top -= 1

        for i in range(x_adder):
            if left <= 0:
                break
            left -= 1

        for i in range(y_adder):
            if bottom >= h:
                break
            bottom += 1

        for i in range(x_adder):
            if right >= w:
                break
            right += 1

        # Crop image to face part
        cropped_img = image[top:bottom, left:right]

        # Make background image
        heightt, widthh, _ = cropped_img.shape
        bg_image = np.ones((heightt, widthh, 3), dtype=np.uint8)
        bg_image = 255 * bg_image

        # Get the result for removed background
        results = selfie_segmentation.process(cropped_img)
        condition = np.stack((results.segmentation_mask,) * 3, axis=-1) > 0.5

        # Combine output image with background
        output_image = np.where(condition, cropped_img, bg_image)

        output_image = Image.fromarray(output_image)
        output_image = output_image.convert("RGBA")

        datas = output_image.getdata()

        newData = []

        for item in datas:
            if item[0] == 255 and item[1] == 255 and item[2] == 255:
                newData.append((255, 255, 255, 0))
            else:
                newData.append(item)

        output_image.putdata(newData)

        output_image = output_image.convert("RGBA")
        data = np.array(output_image)
        red, green, blue, alpha = data.T
        data = np.array([blue, green, red, alpha])
        data = data.transpose()
        output_image = Image.fromarray(data)

        output_images.append(output_image)

    return output_images


def write_images(images):
    processed_images_filenames = []
    for i in images:
        # cv2.imwrite(str(BASE_DIR) + 'processed_images/' + str(uuid4()) + '.jpg', images[i])
        # filename = "static/processed_images/" + str(uuid4()) + '.jpg'
        filename = str(uuid4()) + '.png'
        img = np.array(i)
        processed_images_filenames.append(filename)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
        print(cv2.imwrite('processed_images/' + filename, img))
    return processed_images_filenames


def return_response(processed_images_filenames):
    processed_objects = []
    for each_filename in processed_images_filenames:
        file = File(open(each_filename, 'rb'))
        object = ProcessedImage.objects.create(file=file)
        processed_objects.append(object.id)
        os.remove(each_filename)

    queryset = ProcessedImage.objects.filter(id__in=processed_objects)
    file_urls = []
    for each in queryset:
        # file_urls.append("http://backgroundremover-env.eba-rtjya83c.eu-west-2.elasticbeanstalk.com" + each.file.url)
        file_urls.append("http://127.0.0.1:8000" + each.file.url)

    return Response({'detail': file_urls}, status=status.HTTP_200_OK)