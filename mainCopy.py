# from fastapi import FastAPI, File, UploadFile
from fastapi import UploadFile, File, Form, HTTPException,FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import uvicorn
import base64
import cv2
import matplotlib.pyplot as plt
from io import BytesIO
from IPython.display import display, clear_output
import asyncio
from matplotlib.animation import FuncAnimation

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# DB Connection

mongo_uri = "mongodb+srv://karthi:karthi2001@first.ixg5wi3.mongodb.net/videoInsights"
client = MongoClient(mongo_uri)
users_collection = client.get_database().get_collection("users")

class PhotoUploadResponse(BaseModel):
    name: str
    file: str


# Paths to the "photos"
photos_folder = Path("photos")

# Mount the "photos" folder to serve static files
app.mount("/photos", StaticFiles(directory="photos"), name="photos")

@app.get("/")
def test():
    return "working"

# class uploadRequest(BaseModel):
#     name: str
#     file: UploadFile


@app.post("/upload/video")
async def upload_video(file: UploadFile = File(...)):
    try:
        # Ensure the filename has a .mp4 extension
        filename = file.filename.lower()
        if not filename.endswith(".mp4"):
            raise HTTPException(status_code=422, detail="Invalid file format. Please upload a video in MP4 format.")

        # Read video data into memory
        video_data = await file.read()

        # Process the video in-memory using Matplotlib for asynchronous display
        cap = cv2.VideoCapture()
        cap.open(cv2.CAP_ANY, cv2.CAP_FFMPEG)  # Use FFMPEG backend with CAP_ANY
        cap.set(cv2.CAP_PROP_FPS, 30)  # You may need to adjust the frames per second based on your video's frame rate

        fig, ax = plt.subplots()

        async def update(frame):
            try:
                ret, frame = cap.read()
                if ret:
                    ax.clear()
                    ax.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    plt.pause(0.03)
                else:
                    anim.event_source.stop()
                    plt.close()
            except Exception as e:
                anim.event_source.stop()
                plt.close()
                raise e

        anim = FuncAnimation(fig, update, interval=30, blit=False)
        display(fig)

        await asyncio.sleep(0.1)  # Give time for the display to initialize

        while anim.event_source.running:
            await asyncio.sleep(0.1)

        # Close the video capture
        cap.release()

        return JSONResponse(content={"message": "Video processed successfully", "file_name": filename})
    
    except Exception as e:
        return JSONResponse(content={"error": f"Failed to process video. {str(e)}"}, status_code=500)



@app.get("/getUsers")
async def get_users():
    # Get the names and base64-encoded photos in the "photos" folder
    photos_info = []

    for photo_path in photos_folder.glob("*.jpg"):
        with photo_path.open("rb") as image_file:
            base64_encoded = base64.b64encode(image_file.read()).decode("utf-8")

        photos_info.append({"name": photo_path.stem, "base64_encoded": base64_encoded})

    # Return the photos information as a JSON response
    return JSONResponse(content={"photos": photos_info})

@app.post("/upload/photo")
async def upload_photo(name: str = Form(...), file: UploadFile = File(...)):
    try:
        # Ensure the filename has a .jpg extension
        filename = f"{name}.jpg"

        # Save the uploaded photo to the "photos" folder
        file_path = photos_folder / filename
        with file_path.open("wb") as image:
            image.write(file.file.read())

        # Convert the image to base64from IPython.display import display, clear_output

        with file_path.open("rb") as image_file:
            base64_encoded = base64.b64encode(image_file.read())

        user_data = {"name": name, "photo": base64_encoded}
        users_collection.insert_one(user_data)

        return JSONResponse(content={"message": "Photo uploaded successfully", "name": name, "file_path": str(file_path)})
    
    except Exception as e:
        return JSONResponse(content={"error": f"Failed to upload photo. {str(e)}"}, status_code=500)
    

if __name__ == "__mainCopy__":
    uvicorn.run(app,host="0.0.0.0",port=8001)