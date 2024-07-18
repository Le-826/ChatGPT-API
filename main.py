from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import base64
import requests
import os
import aiohttp
import time

app = FastAPI()
load_dotenv()

# OpenAI API Key
api_key = os.getenv("OPENAI_API_KEY")


# Function to encode the image from file object
def encode_image(image_file):
    try:
        return base64.b64encode(image_file.read()).decode("utf-8")
    except Exception as e:
        raise ValueError(f"Error encoding image: {e}")


# Function to get response from OpenAI API
async def get_openai_response(base64_image):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "system",
                "content": "你是一位专业的妇科医生，你的任务是为胎心曲线图打分."
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "为这张胎心曲线图打分。总分为0-10分，加速时间分数, 加速幅度分数, 胎动次数分数, 胎心基线分数, 振动幅度分数每项为0到2分。只输出每项打分的分数和总分"},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                    },
                ],
            }
        ],
        "max_tokens": 300,
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
            ) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            raise ValueError(f"Request to OpenAI API failed: {e}")


@app.get("/")
def index():
    return ('ChatGPT API server running ...')


@app.post("/analyze_image")
async def analyze_image(image: UploadFile = File(...)):
    try:
        base64_image = encode_image(image.file)
        r = await get_openai_response(base64_image)
        response_content = r["choices"][0]["message"]["content"]
        return JSONResponse(content=response_content)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, debug=False)
