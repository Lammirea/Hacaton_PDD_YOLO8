import base64

#import requests
import uvicorn
from fastapi import FastAPI, UploadFile



import showViolationImage
import showViolationVideo

apiUrl = "http://localhost:5122/files/"

app = FastAPI()


@app.post("/detect")
async def detect(file:UploadFile):
    filename = f"requests_files/{file.filename}"

    with open(filename, 'wb') as f:
        f.write(await file.read())

    if "image" in file.content_type:
        violations = showViolationImage.isViolationImage(filename, f"detected_{file.filename}")
        return {"violationTypes": violations, "Base64Content": toBase64(f"response_files/detected_{file.filename}/{file.filename}")}

    if "video" in file.content_type:
        violations = showViolationVideo.loadVideo(filename, f"detected_{file.filename}")
        return {"violationTypes": violations, "Base64Content": toBase64(f"response_files/detected_{file.filename}/instance-segmentation.mp4")}


def post_file(filename, content_type, token):
    files = {'formFile': (filename, open(filename, 'rb'), content_type)}
    headers = {'Authorization': token}
    print(id)

    return id

def toBase64(filename):
    with open(filename, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
        return encoded_string

if __name__ == "__main__":
     uvicorn.run(app, host="0.0.0.0", port=8000)

