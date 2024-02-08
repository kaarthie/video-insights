import asyncio
import websockets
import cv2
import numpy as np

async def send_video_frames(websocket, path):
    video_path = './videos/vidSam.mp4'
    cap = cv2.VideoCapture(video_path)

    start_message = await websocket.recv()
    if start_message != "start":
        await websocket.send("Invalid start message. Please send 'start' to begin receiving video frames.")
        return

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Convert the frame to JPEG format
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        
        # Convert the buffer to bytes and send it as a Blob object
        await websocket.send(buffer.tobytes())

    cap.release()

start_server = websockets.serve(send_video_frames, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
