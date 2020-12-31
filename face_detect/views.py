from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from face_detect.utils import FaceDetect
import logging
import base64

logger = logging.getLogger(__name__)


class FaceDetecAPIView(APIView):

    def post(self, request, *args, **kwargs):
        KEY_LIST = ["image1", "image2"]
        key_error_list = []
        error_key_dict = {}

        for KEY in KEY_LIST:
            if KEY not in request.data or len(request.data[KEY]) == 0:
                error_key_dict[KEY] = KEY + " not found"
                key_error_list.append(KEY)
        
        if bool(error_key_dict) > 0:
            error_dict = {
                "type": "Error",
                "message": error_key_dict,
                "data": None
            }
            return Response(data=error_dict, status=status.HTTP_400_BAD_REQUEST)

        image1 = request.data["image1"]
        image2 = request.data["image2"]
        try:
            base64.b64encode(base64.b64decode(image1)) == image1
        except:
            error_key_dict["image1"] = "Image file is not valid"

        try:
            res = base64.b64encode(base64.b64decode(image2)) == image2
        except:
            error_key_dict["image2"] = "Image file is not valid"

        if bool(error_key_dict) > 0:
            error_dict = {
                "type": "Error",
                "message": error_key_dict,
                "data": None
            }
            return Response(data=error_dict, status=status.HTTP_406_NOT_ACCEPTABLE)

        try:
            result = FaceDetect.face_recognise(image1=image1, image2=image2)
            data = {
                "verified": True if float(result["accuracy"]) >= float(80) else False,
                "accuracy": result["accuracy"]
            }

            response_data = {
                "type":"Success",
                "message": "Verification Process Successful.",
                "data": data
            }
            return Response(data=response_data, status=status.HTTP_200_OK)
        except:
            data = {"type": "Error", "message": "Internal server error", "data": None}
            return Response(data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)