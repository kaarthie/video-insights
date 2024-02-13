from fastapi import Cookie, FastAPI, Request, Response, WebSocket, WebSocketDisconnect
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import base64
import uuid
import cv2
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



socket=""
print(socket)

# class ConnectionManager:
#     def __init__(self):
#         self.active_connections = {}

#     async def connect(self, websocket: WebSocket,client_id):
#         await websocket.accept()
#         self.active_connections[client_id]=websocket

#     def disconnect(self, client_id):
#         del self.active_connections[client_id]

#     async def send_personal_message(self, message: str, client_id: str):
#         try:
#             if(self.active_connections[client_id]):
#                 await self.active_connections[client_id].send_text(message) 
#         except Exception as e:
#             print(e)

#     async def broadcast(self, message: str):
#         for connection in self.active_connections:
#             await self.active_connections[connection].send_text(message)

# manager = ConnectionManager()
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

@app.get("/set-cookie")
async def set_cookie(response: Response):
    response.set_cookie(key="my_cookie", value="123")
    return {"message": "Cookie set successfully"}

@app.get("/get-cookie")
async def get_cookie(user_id: str = Cookie(None)):
    return {"my_cookie": user_id}

@app.get("/")
async def test():
    global socket

    vid = cv2.VideoCapture(0) 
    i=0
    while i<100: 
        ret, frame = vid.read()
        _, buffer = cv2.imencode('.jpg', frame)
        img_str = base64.b64encode(buffer).decode('utf-8')
        await socket.send_text(img_str)
        i+=1
        
    return "sent"

@app.get("/test")
def test():
    return "hello"
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8004)
