"""
A module for the Stable Diffusion REST API(https://platform.stability.ai/docs/api-reference#tag/Generate/paths/~1v2beta~1stable-image~1generate~1core/post).
You need a key(https://platform.stability.ai/account/keys) and credits(https://platform.stability.ai/account/credits).
You can generate, edit images.
"""

import os
import requests
import random


API_KEY = os.environ["STABILITYAI_API_KEY"]
ROOT_DIR = "D:/StabilityAI"
INPUT_IMAGE = f"{ROOT_DIR}/input/rena_viewport.png"
OUTPUT_FORMAT = "png"
STYLE = "anime"
SEED = random.randint(0, 100000)
outputImage = f'{ROOT_DIR}/output/{SEED}_{os.path.basename(INPUT_IMAGE)}'


response = requests.post(
    f"https://api.stability.ai/v2beta/stable-image/control/structure",
    headers={
        "authorization": API_KEY,
        "accept": "image/*"
    },
    files={
        "image": open(INPUT_IMAGE, "rb")
    },
    data={
        "prompt": f"master piece, high quality, {STYLE}",
        "negative_prompt": "realistic, deformed, low quality, bad anatomy",
        "output_format": OUTPUT_FORMAT,
        "control_strength": 0.7,
        "seed": SEED
    },
)

if response.status_code == 200:
    with open(outputImage, 'wb') as f:
        f.write(response.content)
        print("Image generated successfully!")
else:
    raise Exception(str(response.json()))