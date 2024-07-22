from time import sleep
from typing import Any, Dict, Generator
from os import listdir
import cv2
from subprocess import DEVNULL, PIPE, Popen

from encoders.encoder import Encoder
from encoders.mjpeg_encoder import MJPEGEncoder
from encoders.mpeg4_encoder import MPEG4Encoder
from flask import Flask, Response  
import cv2  


ACTUAL_FPS = 60
method_to_encoder: Dict[str, Encoder] = {
    "mpeg4": MPEG4Encoder(),
    "mjpeg": MJPEGEncoder(),
}

def frame_stream() -> Generator[bytes, Any, None]:
    """
    Frame generator with variable framerate.
    """

    # get list of image names
    images = sorted(listdir("./frames"))

    # yield frames until generator is closed
    try:

        while True:

            for image in images:

                with open(f"./frames/{image}", "rb") as image_fd:

                        # yield frame
                        yield image_fd.read()

                        # sleep until next frame needs to be queued
                        sleep(1/ACTUAL_FPS)

    except GeneratorExit:
        pass
