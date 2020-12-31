## Face Detection service project

### Installation Process:

* Clone the project & create virtual environment
* Install packages from requirements.txt file
* Install also below packsges
    * sudo apt-get install libleptonica-dev
    * sudo apt-get install tesseract-ocr tesseract-ocr-dev
    * sudo apt-get install libtesseract-dev
* Now run `python3 manage.py runserver`


### API Reference
```
Endpoint: `/api/v1/face-detect/`
Request Method: `POST`
Content-type: `json`
Request Body:
```

```
"image1": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAA.....",
"image2": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAA.....",
```

Response Body:

```
{
    "result": {
        "match": true,
        "accuracy": "99.94"
    },
    "status": true
}
```