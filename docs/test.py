# 使用正则表达式提取链接
import re
from openai import OpenAI

with open("testcode.html", "r", encoding="utf-8") as f:
    text = f.read()
    pattern = r'<img[^>]*src="(data:image/[^;]+;base64,[^"]+)"[^>]*>'
    # 使用 re.search() 函数在文本中查找第一个匹配的链接地址
    match = re.search(pattern, text)
    if match:
        img = match.group(1)
        print("img:", img)

aiclient = OpenAI(
    # 此为默认路径，您可根据业务所在地域进行配置
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    # 从环境变量中获取您的 API Key。此为默认方式，您可根据需要进行修改
    api_key="7f5744e3-acfc-43de-a35c-3bd3cf92f5e4",
)

response = aiclient.chat.completions.create(
    # 指定您创建的方舟推理接入点 ID，此处已帮您修改为您的推理接入点 ID
    model="doubao-1-5-vision-pro-32k-250115",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "请返回这个图片中彩色的单词给我，不要返回其他的内容"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": img
                    },
                },
            ],
        }
    ],
)
print(response.choices[0])
print("content: ", response.choices[0].message.content)
