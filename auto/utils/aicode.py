import base64
import os
import openai
from openai import OpenAI


# 配置请求时不使用代理
openai.proxy = None
openai.api_base = "https://ark.cn-beijing.volces.com/api/v3"

# 删除代理环境变量，防止 openai 走代理
os.environ.pop("http_proxy", None)
os.environ.pop("https_proxy", None)
os.environ.pop("HTTP_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)

# 请确保您已将 API Key 存储在环境变量 ARK_API_KEY 中
# 初始化Ark客户端，从环境变量中读取您的API Key
client = OpenAI(
    # 此为默认路径，您可根据业务所在地域进行配置
    # base_url="https://ark.cn-beijing.volces.com/api/v3",
    # 从环境变量中获取您的 API Key。此为默认方式，您可根据需要进行修改
    api_key="",
)

# 需要传给大模型的图片
image_path = "../assets/down.png"


# 定义方法将指定路径图片转为Base64编码
def encode_image(img_path):
    with open(img_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


# 将图片转为Base64编码
base64_image = f"data:image/png;base64,{encode_image(image_path)}"

response = client.chat.completions.create(
    # 指定您创建的方舟推理接入点 ID，此处已帮您修改为您的推理接入点 ID
    model="doubao-1-5-vision-pro-32k-250115",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "请返回这种图片中橙色的单词给我"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": base64_image
                    },
                },
            ],
        }
    ],
)

print(response.choices[0])
print("content: ", response.choices[0].message.content)
