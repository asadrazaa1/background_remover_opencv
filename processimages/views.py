import os
import tempfile
from uuid import uuid4

import cv2
from django.core.files import File
from rest_framework import generics, status
from rest_framework.response import Response

from .dlib_method import remove_background
from .models import ProcessedImage
from .serializers import RemoveBackgroundSerializer, ProcessedImageSerializer


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
            for i in range(len(images)):
                # cv2.imwrite(str(BASE_DIR) + 'processed_images/' + str(uuid4()) + '.jpg', images[i])
                # filename = "static/processed_images/" + str(uuid4()) + '.jpg'
                filename = str(uuid4()) + '.jpg'
                processed_images_filenames.append(filename)
                cv2.imwrite(filename, images[i])
        else:
            # return {"file": "Face not found"}
            return Response({'error': "Faces not found!"}, status=status.HTTP_400_BAD_REQUEST)

        processed_objects = []
        for each_filename in processed_images_filenames:
            file = File(open(each_filename, 'rb'))
            object = ProcessedImage.objects.create(file=file)
            processed_objects.append(object.id)
            os.remove(each_filename)

        queryset = ProcessedImage.objects.filter(id__in=processed_objects)

        return Response({'detail': queryset.values_list('file', flat=True)}, status=status.HTTP_200_OK)
