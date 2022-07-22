from typing import Optional
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.staticfiles import StaticFiles 
from tempfile import NamedTemporaryFile
from os import listdir, getcwd, path
from os.path import exists, join
from datetime import datetime
import cv2, math, platform

app = FastAPI()
app.mount("/videos", StaticFiles(directory="videos"), name="video")

@app.get("/")
def index():
    welcome = {"welcome":"Welcome to the video api"}
    url_list = {"urlpaths" : [{"path": route.path, "name": route.name} for route in app.routes]} #list of all urls
    return [welcome,url_list]

@app.get("/videos")
def videolist(request:Request,before:Optional[str]=None, after:Optional[str]=None, lessthansize:Optional[int]=None, morethansize:Optional[int]=None):
    urlpath = getcwd() #current working directory
    list = listdir(join(urlpath,"videos"))
    new = []
    afterdate = datetime.strptime(after,'%Y-%m-%dT%H:%M').timestamp() if bool(after) else None
    beforedate = datetime.strptime(before,'%Y-%m-%dT%H:%M').timestamp() if bool(before) else None

    for x in list:
        if(platform.system() == 'Windows'):
            time = path.getctime(join(urlpath,"videos",x))
            size = path.getsize(join(urlpath,"videos",x))

            #applying filter based on date
            datefilter = (not bool(afterdate) or bool(time > afterdate)) and (not bool(beforedate) or bool(time<beforedate))
            
            #applying filter based on the size of file
            sizefilter = (not bool(lessthansize) or bool(lessthansize>size) and (not bool(morethansize)) or bool(morethansize<size))
            
            if (datefilter and sizefilter):
                new.append(request.url._url + "/" + x)

    return {"videos":new}

@app.post("/uploadvdo/")
async def create_upload_vdo(file: UploadFile):
    contents = await file.read()
    length = len(contents)

    # file size validation
    if(length > 1024*1024*1024):
        return {"Error": "File too large"}


    # video format validation
    if not file.content_type in ['video/mp4','video/x-matroska']:
        return {"Error":"File type not supported."}

    file_copy = NamedTemporaryFile()
    try:
        file_copy.write(contents)

        # calculate the video length 
        cap = cv2.VideoCapture(file_copy.name)
        frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        count = math.floor(frames/fps)

        if(count > 600):
            return {"Error":"The video should not exceed 10 minutes"}
            
        ext = file.filename[-3:]
        name = file.filename[:-4]
        file_location = f"videos/{file.filename}"

        #update file name if it already exists
        n = 0
        while(exists(file_location)):
            file_location = f"videos/{name}_{n}.{ext}"
            n+=1

        #write the file
        with open(file_location,"wb+") as f:
            f.write(contents)

    finally:
        file_copy.close()    

    return {"filename":file_location}

@app.post("/pricing/")
def price_of_video(size:int,length:int,type:Optional[str] = None):

    # validate file formats 
    if(type not in ["mp4","xmp","x-matroska"]):
        return {"Error":"Unsupported file type"}

    for_size = 5 if size < 500*1024*1024 else 12.5 #pricing based on video size
    for_length = 12.5 if length < 6*60+18 else 20 #pricing based on video length
    return {"price":for_size+for_length,"video format":type}