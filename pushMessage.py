import requests

class WxPusher:
    def __init__(self, app_token="AT_qcQ4PiA2zvMMnP8gdjFlfPeV9JDpSmS2", default_uids=None):
        self.default_app_token = app_token
        self.api_url = "https://wxpusher.zjiecode.com/api/send/message"
        self.default_uids = default_uids if default_uids is not None else ["UID_kTKkS3r3vUaiNwxxcGrg0kVqyyJA"]

    def send_message(self, content, uids=None, summary=None, content_type=1, app_token=None):
        """
        发送消息到微信

        :param content: 消息内容
        :param uids: 接收消息的用户 UID 列表
        :param summary: 消息摘要（可选）
        :param content_type: 消息类型，1 为文本（默认）
        :param app_token: 可选的应用 Token
        """
        payload = {
            "appToken": app_token if app_token else self.default_app_token,
            "content": content,
            "summary": summary if summary else content,
            "contentType": content_type,
            "uids": uids if uids is not None else self.default_uids
        }

        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(self.api_url, json=payload, headers=headers)
        
        if response.status_code == 200:
            print("消息发送成功")
        else:
            print(f"消息发送失败，错误信息：{response.text}")

# 示例调用
if __name__ == "__main__":
    content = "这是一个测试消息"
    summary = "测试消息摘要"

    wx_pusher = WxPusher()
    wx_pusher.send_message(content, summary=summary)
