import cv2
import mediapipe as mp
import numpy as np


def remove_background(img_path):
  #Initialize mediapipe objects
  mp_face_detection = mp.solutions.face_detection
  mp_selfie_segmentation = mp.solutions.selfie_segmentation
  selfie_segmentation = mp_selfie_segmentation.SelfieSegmentation(model_selection=1)
  
  #Read image
  image = cv2.imread(img_path)

  #Find dimensions of image
  h, w, c = image.shape

  #Make a new image for background
  img = np.ones((h, w, 3), dtype = np.uint8)
  img = 255* img

  #Set upper, lower and side spaces
  x_adder = int(w/5)
  y_adder = int(h/10)

  with mp_face_detection.FaceDetection(min_detection_confidence=0.5, model_selection=0) as face_detection:
      # Convert the BGR image to RGB and process it with MediaPipe Face Detection.
      results = face_detection.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

      if results.detections == None:
        return False,''

      for detection in results.detections:
        x = detection.location_data.relative_bounding_box.xmin
        y = detection.location_data.relative_bounding_box.ymin
        ww = detection.location_data.relative_bounding_box.width
        hh = detection.location_data.relative_bounding_box.height


        x, y = int(x * w), int(y * h)
        x2,y2 = int(ww * w), int(hh * h)
        x2 += x
        y2 += y

        for i in range(y_adder):
          if y <= 0:
            break
          y-=1
        
        for i in range(x_adder):
          if x <= 0:
            break
          x-=1
        

        for i in range(y_adder):
          if y2 >= h:
            break
          y2+=1
        
        for i in range(x_adder):
          if x2 >= w:
            break
          x2+=1
        
        
        # cv2.rectangle(image, (x, y), (x2, y2), (0, 255, 0), 2)
        cropped_img = image[y:y2,x:x2]

        heightt, widthh, _ = cropped_img.shape
        bg_image = np.ones((heightt, widthh, 3), dtype = np.uint8)
        bg_image = 255* bg_image
        # get the result
        results = selfie_segmentation.process(cropped_img)
        condition = np.stack((results.segmentation_mask,) * 3, axis=-1) > 0.5
        output_image = np.where(condition, cropped_img, bg_image)
        return True,output_image


found,image = remove_background('sample.jpg')

if found:
  cv2.imwrite('Output3.jpg',image)

else:
  print('Face not found')