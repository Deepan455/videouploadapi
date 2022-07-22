# Video upload API
A simple API to upload videos in a file system and access it.

## 🔥 Features
- Upload video with criteria:
    - Less than 10 minutes of length
    - Less than 1GB of size
    - File format of either mp4 or mkv

- List video urls with filters of date range and file size range
- an endpoint to calculate the cost of uploading video to the platform depending on size and video length

## 📥 Installation
 Run the following command with or without a virtual environment
```shell
    pip install -r requirements.txt
    uvicorn api:app --reload
```
 The api will be available on the localhost on 'https:\\127.0.0.1:8000'