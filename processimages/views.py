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
            for i in images:
                # cv2.imwrite(str(BASE_DIR) + 'processed_images/' + str(uuid4()) + '.jpg', images[i])
                # filename = "static/processed_images/" + str(uuid4()) + '.jpg'
                filename = str(uuid4()) + '.png'
                print(filename)
                processed_images_filenames.append(filename)
                i.save('processed_images/' + filename, 'PNG')

                print(filename + "saved")

                processed_objects = []
                for each_filename in processed_images_filenames:
                    file = File(open(each_filename, 'rb'))
                    object = ProcessedImage.objects.create(file=file)
                    processed_objects.append(object.id)
                    os.remove(each_filename)

                queryset = ProcessedImage.objects.filter(id__in=processed_objects)
                file_urls = []
                for each in queryset:
                    file_urls.append(
                        "http://backgroundremover-env.eba-rtjya83c.eu-west-2.elasticbeanstalk.com" + each.file.url)

                return Response({'detail': file_urls}, status=status.HTTP_200_OK)
        else:
            # return {"file": "Face not found"}
            return Response({'error': "Faces not found!"}, status=status.HTTP_400_BAD_REQUEST)


