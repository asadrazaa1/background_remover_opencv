import cv2
import mediapipe as mp
import numpy as np
import face_recognition as fr


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
    y_adder = int(h / 10)

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
        output_images.append(output_image)

    return output_images

# images = remove_background('10029.jpg')
#
# if images != []:
#     for i in range(len(images)):
#         cv2.imwrite(str(i)+'.jpg',images[i])
# else:
#   print('Face not found')
