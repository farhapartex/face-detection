from django.conf import settings
from face_detection.utils.preprocessing.image import ImageConverter
from face_detection.utils.preprocessing.image import ImagePreprocessing
from face_detection.face_detection.one_shot import FaceRecognition
import os
import cv2
import time, datetime


class FaceDetect(object):

    @classmethod
    def check_media_directory(cls):
        media_directory = str(settings.BASE_DIR) + "/images"
        if not os.path.isdir(media_directory):
            os.mkdir(media_directory)

    @classmethod
    def check_directory(cls, dir_name):
        cls.check_media_directory()

        if dir_name == "known":
            known_media_directory = str(settings.BASE_DIR) + "/images/known_images"
            media_directory = known_media_directory
            if not os.path.isdir(known_media_directory):
                os.mkdir(known_media_directory)

            compress_directory = str(settings.BASE_DIR) + "/images/known_images/compress_files"
            if not os.path.isdir(compress_directory):
                os.mkdir(compress_directory)
        elif dir_name == "face":
            face_directory = str(settings.BASE_DIR) + "/images/faces/"
            media_directory = face_directory
            if not os.path.isdir(face_directory):
                os.mkdir(face_directory)
            return media_directory
        else:
            unknown_media_directory = str(settings.BASE_DIR) + "/images/unknown_images"
            media_directory = unknown_media_directory
            if not os.path.isdir(unknown_media_directory):
                os.mkdir(unknown_media_directory)

        return media_directory

    @classmethod
    def convert_base64_to_image(cls, img_data, file_type):
        img_path = cls.check_directory("known") if file_type == "known" else cls.check_directory("unknown")
        file_name = str(datetime.datetime.now())
        # img_format = img_extension
        image_convert = ImageConverter(image_name=file_name + '.png', output_dir=img_path)
        img_path = image_convert.from_base64(image_data=img_data)

        return img_path

    @classmethod
    def crop_image(cls, img_path, img_type):
        dir_path = str(settings.BASE_DIR) + "/images/"
        dir_path += "known_images" if img_type == "known" else "unknown_images"
        print("dir path" + dir_path)
        ip = ImagePreprocessing(source=dir_path)
        ip.face_crop(image=img_path, output_dir=dir_path)

        return dir_path

    @classmethod
    def crop_face(cls, img_path, img_type):
        image = cv2.imread(img_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.3,
            minNeighbors=3,
            minSize=(30, 30)
        )
        dir_path = cls.check_directory("face")
        current_time = str(datetime.datetime.now().timestamp())
        file_path = dir_path + current_time
        os.mkdir(file_path)
        index = 1
        img_list = []
        for (x, y, w, h) in faces:
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            roi_color = image[y:y + h, x:x + w]
            print("[INFO] Object found. Saving locally.")
            img_name = file_path + "/" + str(index) + img_type +"_face.png"
            cv2.imwrite(img_name, roi_color)
            print("File saved!")
            img_list.append(index)
            index += 1
        #print(file_path, img_list)
        return file_path, img_list

    @classmethod
    def remove_files_from_dir(cls, dir_name):
        for img in os.listdir(dir_name):
            try:
                img_file_path = os.path.join(dir_name, img)
                os.remove(img_file_path)
            except Exception as e:
                continue

    @classmethod
    def face_recognise(cls, image1, image2):
        base_dir = str(settings.BASE_DIR)
        image1_img_path = cls.convert_base64_to_image(image1, "known")
        converted_selfie_path = cls.convert_base64_to_image(image2, "unknown")
        selfie_dir_path, selfie_img_list = cls.crop_face(converted_selfie_path, "selfie")
        image1_dir_path = cls.crop_image(image1_img_path, "known")

        accurecy = []
        if len(selfie_img_list) == 0:
            return {
                "accuracy": 0.0
            }

        for img_index in selfie_img_list:
            fr = FaceRecognition(known_data_directory=image1_dir_path)
            fr.save()
            img_path = selfie_dir_path + "/" + str(img_index) + "selfie_face.png"
            result = fr.nid_verification(img_path, display=False)
            accurecy.append(float(result["accuracy"]))

        cls.remove_files_from_dir(selfie_dir_path)
        cls.remove_files_from_dir(os.path.join(base_dir, "images/unknown_images"))
        cls.remove_files_from_dir(os.path.join(base_dir, "images/known_images"))
        os.rmdir(selfie_dir_path)

        return {
            "accuracy": max(accurecy)
        }