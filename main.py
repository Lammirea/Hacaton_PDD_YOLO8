import requests
import uvicorn

from fastapi import FastAPI, UploadFile

import showViolationImage

#http://92.53.97.223:8081
apiUrl = "http://localhost:5122/files/"

app = FastAPI()


@app.post("/detect")
async def detect(file:UploadFile,  token:str):
    filename = f"requests_files/{file.filename}"

    with open(filename, 'wb') as f:
        f.write(await file.read())


    violations = showViolationImage.isViolationImage(filename, f"detected_{file.filename}")
    file_link = post_file(f"response_files/detected_{file.filename}/{file.filename}", file.content_type, token)
    return {"violationTypes": violations, "fileLink":file_link}

def post_file(filename, content_type, token):
    files = {'formFile': (filename, open(filename, 'rb'), content_type)}
    headers = {'Authorization': token}
    id = requests.post(apiUrl, headers=headers, files=files).json()
    print(id)

    return id

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

