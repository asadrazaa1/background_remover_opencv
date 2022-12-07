import os
import tempfile
from time import sleep
from uuid import uuid4

import cv2
import numpy as np
from django.core.files import File
from rest_framework import generics, status
from rest_framework.response import Response

from .dlib_method import remove_background, write_images, return_response
from .models import ProcessedImage
from .serializers import RemoveBackgroundSerializer


class RemoveBackgroundView(generics.GenericAPIView):
    """Endpoint to remove-background from an image & return the new image url"""
    serializer_class = RemoveBackgroundSerializer

    def post(self, request, *args, **kwargs):
        uploaded_file = request.FILES.get('file')
        # write the data to a temp file
        tup = tempfile.mkstemp()  # make a tmp file
        f = os.fdopen(tup[0], 'wb')  # open the tmp file for writing
        f.write(uploaded_file.read())  # write the tmp file
        f.close()
        # return the path of the file
        filepath = tup[1]  # get the filepath

        images = remove_background(filepath)
        if images != []:
            processed_images_filenames = write_images(images)
            print(processed_images_filenames)
            return return_response(processed_images_filenames)
        else:
            # return {"file": "Face not found"}
            return Response({'error': "Faces not found!"}, status=status.HTTP_400_BAD_REQUEST)