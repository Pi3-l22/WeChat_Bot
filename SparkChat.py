import SparkApi
from loguru import logger  # 日志输出

# 以下密钥信息从星火控制台获取
appid = "YOUT_APP_ID"  # 填写控制台中获取的 APPID 信息
api_secret = "YOUR_API_SECRET"  # 填写控制台中获取的 APISecret 信息
api_key = "YOUR_API_KEY"  # 填写控制台中获取的 APIKey 信息
# 用于配置大模型版本，默认“general/generalv2”
domain = "generalv3"  # v3.0版本
# 云端环境的服务地址
Spark_url = "ws://spark-api.xf-yun.com/v3.1/chat"  # v3.1环境的地址
# 存放历史对话内容
text = {}  # 区分不同用户的历史消息


# {user1:[text1, text2, ...], user2:[text1, text2, ...], ...}


def getText(role, content, user):
    jsoncon = {"role": role, "content": content}
    if user not in text:
        text[user] = []
        text[user].append(jsoncon)
    else:
        text[user].append(jsoncon)
    return text[user]


def getlength(usertext):
    length = 0
    for content in usertext:
        temp = content["content"]
        leng = len(temp)
        length += leng
    return length


def checklen(text):
    while getlength(text) > 8000:
        del text[0]
    return text


def main(Input, user):
    # text.clear()
    # Input = input("\n" + "我:")
    question = checklen(getText("user", Input, user))
    SparkApi.answer = ""
    # print("星火:", end="")
    SparkApi.main(appid, api_key, api_secret, Spark_url, domain, question)
    getText("assistant", SparkApi.answer, user)
    return SparkApi.answer


# 清空历史消息
def clear_history(wcf, msg):
    user = msg.sender
    try:
        text[user].clear()
    except KeyError:
        pass
    logger.info('{}清空星火历史消息', user)
    # print(f'[+] {user} 清空星火历史消息')
    wcf.send_text('[+] 清空星火历史消息', user)


# 讯飞星火大模型 聊天
def spark_chat(wcf, msg):
    content = msg.content
    if msg.is_at(wxid=wcf.self_wxid):  # 如果是群聊中@我
        self_name = wcf.get_user_info()['name']
        content = content.replace(f'@{self_name}', '')
        answer = main(content, msg.roomid)
        logger.info('{}: {}', msg.roomid, content)
        # print(f'[+] {msg.roomid}: {content}')
        print(f'[+] 星火: {answer}')
        wcf.send_text(answer, msg.roomid)
    elif not msg.from_group():  # 如果是私聊
        answer = main(content, msg.sender)
        logger.info('{}: {}', msg.sender, content)
        # print(f'[+] {msg.sender}: {content}')
        print(f'[+] 星火: {answer}')
        wcf.send_text(answer, msg.sender)
