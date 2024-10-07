from http import HTTPStatus
from dashscope import MultiModalConversation
from loguru import logger  # 日志输出

# ！ 添加千问API_KEY 到环境变量 以DASHSCOPE_API_KEY为变量名 API_KEY为变量值


# 存放历史对话内容
text = {}  # 区分不同用户的历史消息
# {user1:[text1, text2, ...], user2:[text1, text2, ...], ...}

# 存储图片文件夹
image_dir = 'C:\\Users\\Administrator\\Desktop\\WeChatFerry\\image'
# 存储图片路径
image_path = ''


def getText(role, content, user, img_path):
    jsoncon = {"role": role, "content": [{"image": img_path}, {"text": content}]}
    if user not in text:
        text[user] = []
        text[user].append(jsoncon)
    else:
        text[user].append(jsoncon)
    return text[user]


def getHistory(role, content, user):
    jsoncon = {"role": role, "content": [{"text": content}]}
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


def main(Input, user, img_path):
    messages = checklen(getText("user", Input, user, img_path))
    response = MultiModalConversation.call(
        model=MultiModalConversation.Models.qwen_vl_chat_v1,  # 模型选择
        messages=messages,
        result_format='message',  # 返回结果格式
    )
    if response.status_code == HTTPStatus.OK:
        role = response.output.choices[0]['message']['role']
        answer = response.output.choices[0]['message']['content']
        getHistory(role, answer, user)
        return answer
    else:
        return 0


# 清空历史消息
def clear_history(wcf, msg):
    user = msg.sender
    try:
        text[user].clear()
    except KeyError:
        pass
    logger.info('{}清空千问VL历史消息', user)
    wcf.send_text('[+] 清空千问VL历史消息', user)


# 接收图片并下载
def receive_image(wcf, msg):
    global image_path
    logger.info('{} 发送图片', msg.sender)
    try:
        # 下载图片
        image_path = wcf.download_image(id=msg.id, extra=msg.extra, dir=image_dir)
        if image_path == "":
            logger.error('下载图片失败')
            wcf.send_text('[-] 接收图片失败', msg.sender)
            return
    except Exception as e:
        logger.error('接收图片错误:{}', e)
    else:
        logger.info('接收图片 {}', msg.id)
        wcf.send_text('[+] 收到图片 请发送图片描述文字', msg.sender)


# 通义大模型聊天
def qwen_vl(wcf, msg):
    content = msg.content
    img_path = 'file://' + image_path.replace('\\', '/')
    if msg.is_at(wxid=wcf.self_wxid):  # 如果是群聊中@我
        self_name = wcf.get_user_info()['name']
        content = content.replace(f'@{self_name}', '')
        answer = main(content, msg.roomid, img_path)
        if answer == 0:
            logger.error('请求错误')
            answer = '[-] 请求错误'
        else:
            logger.info('{}: {}', msg.roomid, content)
            print(f'[+] 千问VL: {answer}')
        wcf.send_text(answer, msg.roomid)
    elif not msg.from_group():  # 如果是私聊
        answer = main(content, msg.sender, img_path)
        if answer == 0:
            logger.error('请求错误')
            answer = '[-] 请求错误'
        else:
            logger.info('{}: {}', msg.sender, content)
            print(f'[+] 千问VL: {answer}')
        wcf.send_text(answer, msg.sender)