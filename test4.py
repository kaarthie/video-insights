import cv2
import numpy as np
import asyncio
import websockets
from fastapi import FastAPI, WebSocket, File, UploadFile

app = FastAPI()

async def send_video_frames(websocket: WebSocket, video_data: bytes):
    cap = cv2.VideoCapture(video_data)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Convert the frame to JPEG format
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        
        # Convert the buffer to bytes and send it as a Blob object
        await websocket.send_bytes(buffer.tobytes())

    cap.release()

@app.post("/video_stream")
async def video_stream(websocket: WebSocket, file: UploadFile = File(...)):
    if not file.content_type.startswith("video"):
        return {"error": "File is not a video"}

    # WebSocket communication
    await send_video_frames(websocket, await file.read())

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
