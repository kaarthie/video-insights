from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Cookie, Request, Response, WebSocket, WebSocketDisconnect, Body
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import uvicorn, base64, cv2, os, asyncio, websockets
from typing import Optional
from dotenv import load_dotenv
load_dotenv()
import google.generativeai as genai
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

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

socket=""
print(socket)

class PhotoUploadResponse(BaseModel):
    name: str
    file: str


# Paths to the "photos"
photos_folder = Path("photos")

# Mount the "photos" folder to serve static files
app.mount("/photos", StaticFiles(directory="photos"), name="photos")



class uploadRequest(BaseModel):
    name: str
    file: UploadFile

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, response:Response):
    global socket
    await websocket.accept()
    socket= websocket
    # client_id=uuid.uuid4()
    # print("hello")
    # await manager.connect(websocket,client_id)
    try:
        # while True:
        data = await websocket.receive_text()
        print(data)
            # await manager.(f"You wrote: {data}", client_id)
            # await manager.broadcast(f"Client #{client_id} says: {data}")
        await websocket.send_text("hello")
    except WebSocketDisconnect:
        # manager.disconnect(client_id)
        # await manager.broadcast(f"Client #{client_id} left the chat")
        print("error")
    # response.set_cookie(key="user_id",value=client_id)
    # return




@app.get("/")
async def test(video_name: Optional[str] = None):
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        cap.release()
    global socket


    video_path = f"videos/{video_name}"
    print(video_path)
    vid = cv2.VideoCapture(video_path)
    if not vid.isOpened():
        return {"error": f"Unable to open video file '{video_path}'"}

    i = 0
    while True: 
        ret, frame = vid.read()
        if not ret:
            break  # Break out of the loop if there are no more frames
        
        _, buffer = cv2.imencode('.jpg', frame)
        img_str = base64.b64encode(buffer).decode('utf-8')
        
        # Construct response object
        response_object = {"status": "success", "image": img_str}
        
        # Add frame details for every 20th frame
        if i % 20 == 0:
            response_object["frameNumber"] = i
        
        await socket.send_json(response_object)
        i += 1
        
    return {"status": "success", "message": "All frames sent."}

@app.get("/webcam")
async def stream_webcam():
    for i in range(3):  # Assuming up to 10 cameras
       cap = cv2.VideoCapture(i)
       if cap.isOpened():
           cap.release()
    cap = cv2.VideoCapture(0)  # Open webcam (assuming it's the default device)

    if not cap.isOpened():
        return {"error": "Unable to open webcam."}
    i = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        _, buffer = cv2.imencode('.jpg', frame)
        img_str = base64.b64encode(buffer).decode('utf-8')

        # Construct response object
        response_object = {"status": "success", "image": img_str}

        # Add frame details for every 20th frame
        if i % 20 == 0:
            response_object["frameNumber"] = i

        await socket.send_json(response_object)
        i += 1

    cap.release()  # Release the webcam capture after streaming frames

    return {"status": "success", "message": "Webcam frames sent"}

@app.delete("/pause")
async def pause_streaming():
    global pause_flag
    pause_flag = True
    return {"status": "success", "message": "Streaming paused."}


@app.get("/videos")
async def get_videos_with_first_frames():

    videos_folder = "videos"
    video_files = [file for file in os.listdir(videos_folder) if file.endswith(".mp4")]

    videos_data = []
    for video_file in video_files:
        video_path = os.path.join(videos_folder, video_file)
        vid = cv2.VideoCapture(video_path)
        if vid.isOpened():
            ret, frame = vid.read()
            if ret:
                _, buffer = cv2.imencode('.jpg', frame)
                img_str = base64.b64encode(buffer).decode('utf-8')
                videos_data.append({"name": video_file, "first_frame": img_str})
        vid.release()

    return videos_data

@app.post('/uploadVideo')
async def upload_video(file: UploadFile = File(...)):
    try:
        # Ensure the filename has a .mp4 extension
        filename = file.filename.lower()
        if not filename.endswith(".mp4"):
            raise HTTPException(status_code=422, detail="Invalid file format. Please upload a video in MP4 format.")

        # Create the "videos" folder if it doesn't exist
        if not os.path.exists("videos"):
            os.makedirs("videos")

        # Save the uploaded video to the "videos" folder
        video_path = os.path.join("videos", filename)
        with open(video_path, "wb") as video_file:
            video_file.write(await file.read())

        # Display the video using cv2.imshow()
        cap = cv2.VideoCapture(0)
        while True:
            success, img = cap.read()
            if not success:
                break
            cv2.imshow("Video", img)
            if cv2.waitKey(15) & 0xFF == ord('q'):
                break

        # Close the video capture
        cap.release()
        cv2.destroyAllWindows()

        return JSONResponse(content={"message": "Video processed successfully", "file_name": filename})
    
    except Exception as e:
        return JSONResponse(content={"error": f"Failed to process video. {str(e)}"}, status_code=500)

@app.get("/test")
def test():
    return "hello"

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

        # Convert the image to base64
        with file_path.open("rb") as image_file:
            base64_encoded = base64.b64encode(image_file.read())

        user_data = {"name": name, "photo": base64_encoded}
        users_collection.insert_one(user_data)

        return JSONResponse(content={"message": "Photo uploaded successfully", "name": name, "file_path": str(file_path)})
    
    except Exception as e:
        return JSONResponse(content={"error": f"Failed to upload photo. {str(e)}"}, status_code=500)

async def send_video_frames(websocket: websockets.WebSocketServerProtocol, video_path: str):
    cap = cv2.VideoCapture(video_path)

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        # Convert the frame to JPEG format
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue

        # Convert the buffer to bytes and send it as a Blob object
        await websocket.send_bytes(buffer.tobytes())

    cap.release()

@app.get("/set-cookie")
async def set_cookie(response: Response):
    response.set_cookie(key="my_cookie", value="123")
    return {"message": "Cookie set successfully"}

@app.get("/get-cookie")
async def get_cookie(user_id: str = Cookie(None)):
    return {"my_cookie": user_id}

@app.post("/askGemini")
async def gemini_response(prompt: str = Body(..., description="The context or background information for the question."),
                          question: str = Body(..., description="The specific question you want answered."),
                          max_tokens: Optional[int] = None):
    model = genai.GenerativeModel("gemini-pro")
    try:
        response = model.generate_content([prompt, question])
        print(response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"API error: {e}")

    if max_tokens:
        return response.text[:max_tokens]
    else:
        return response.text

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)