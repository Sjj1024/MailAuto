import base64

import requests

headers = {
    "Authorization": f"Bearer ",
    "Content-Type": "application/json"
}

# 需要传给大模型的图片
image_path = "../assets/down.png"


def encode_image(img_path):
    with open(img_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


# 将图片转为Base64编码
base64_image = f"data:image/png;base64,{encode_image(image_path)}"

data = {
    "model": "doubao-1-5-vision-pro-32k-250115",
    "messages": [
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
    ]
}

response = requests.post(
    "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
    json=data,
    headers=headers,
    proxies=None  # 明确不使用代理
)


res_json = response.json()
content = res_json.get("choices")[0].get("message").get("content")
print(content)
