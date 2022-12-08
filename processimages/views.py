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
        processed_images_filenames = []

        if images != []:
            for i in images:
                filename = str(uuid4()) + '.png'
                img = np.array(i)
                processed_images_filenames.append(filename)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
                cv2.imwrite('processed_images/' + filename, img)

            processed_objects = []
            for each_filename in processed_images_filenames:
                file = File(open('processed_images/' + each_filename, 'rb'))
                object = ProcessedImage.objects.create(file=file)
                processed_objects.append(object.id)

            queryset = ProcessedImage.objects.filter(id__in=processed_objects)
            file_urls = []
            for each in queryset:
                file_urls.append("http://backgroundremover-env.eba-rtjya83c.eu-west-2.elasticbeanstalk.com" + each.file.url)
                # file_urls.append("http://127.0.0.1:8000" + each.file.url)

            return Response({'detail': file_urls}, status=status.HTTP_200_OK)
        else:
            # return {"file": "Face not found"}
            return Response({'error': "Faces not found!"}, status=status.HTTP_400_BAD_REQUEST)