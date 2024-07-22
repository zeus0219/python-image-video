#!/usr/bin/python3.8

from typing import Any, Generator
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse,StreamingResponse
from uvicorn import run
import cv2  
camera = cv2.VideoCapture(0)  # Use 0 for the default camera  
from encoders.encoder import Encoder
from utils.streaming_utils import method_to_encoder, frame_stream
def generate_frames():  
    while True:  
        success, frame = camera.read()  # Capture frame-by-frame  
        if not success:  
            break  
        else:  
            # Encode the frame in JPEG format  
            processed_frame = cv2.bitwise_not(frame)  
            cv2.putText(processed_frame, "Mobile Camera Stream", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)  # Red text  
            ret, buffer = cv2.imencode('.jpg', processed_frame)  
            frame = buffer.tobytes()  

            # Yield the output frame in the specific format required for streaming  
            yield (b'--frame\r\n'  
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  



app = FastAPI()
@app.get("/live/{method}")
async def live(method: str):
    """
    Returns encoded frames via chunked response based on requested method.
    """
    
    # resolve encoding solution
    encoder: Encoder = method_to_encoder.get(method, None)
    if not encoder:
        raise HTTPException(status_code=400, detail=f"Unsupported encoder method: '{method}'.")

    # get encoder stream with connection close handler
    stream: Generator[bytes, Any, None] = encoder.encode(frame_stream())
    async def _end_stream():
        stream.close()

    # encode and return chunks
    return StreamingResponse(stream, media_type=encoder.get_content_type(), background=_end_stream)

@app.get("/video_feed")  
async def video_feed():  
    return StreamingResponse(generate_frames(), media_type='multipart/x-mixed-replace; boundary=frame')  
@app.get("/", response_class=HTMLResponse)  
async def index():  
    # Simple HTML page to display the video feed  
    return """  
    <!doctype html>  
    <html>  
        <head>  
            <title>Camera Stream</title>  
        </head>  
        <body>  
            <h1>Video Stream</h1>  
            <img src="/video_feed" width="640" height="480">  
        </body>  
    </html>  
    """  

def main():
    run("server:app", host="0.0.0.0", port=20000, workers=10)

if __name__ == "__main__":
    try:  
        main()
    except KeyboardInterrupt:  
        pass  
    finally:  
        # Release the camera when the server stops  
        camera.release()  
