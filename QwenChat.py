from http import HTTPStatus
from dashscope import Generation
from loguru import logger  # 日志输出

# ！ 添加千问API_KEY 到环境变量 以DASHSCOPE_API_KEY为变量名 API_KEY为变量值


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
    messages = checklen(getText("user", Input, user))
    response = Generation.call(
        Generation.Models.qwen_max,  # 模型选择
        messages=messages,
        result_format='message',  # 返回结果格式
    )
    if response.status_code == HTTPStatus.OK:
        role = response.output.choices[0]['message']['role']
        answer = response.output.choices[0]['message']['content']
        getText(role, answer, user)
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
    logger.info('{}清空千问历史消息', user)
    wcf.send_text('[+] 清空千问历史消息', user)


# 通义大模型聊天
def qwen_chat(wcf, msg):
    content = msg.content
    if msg.is_at(wxid=wcf.self_wxid):  # 如果是群聊中@我
        self_name = wcf.get_user_info()['name']
        content = content.replace(f'@{self_name}', '')
        answer = main(content, msg.roomid)
        if answer == 0:
            logger.error('请求错误')
            answer = '[-] 请求错误'
        else:
            logger.info('{}: {}', msg.roomid, content)
            print(f'[+] 千问: {answer}')
        wcf.send_text(answer, msg.roomid)
    elif not msg.from_group():  # 如果是私聊
        answer = main(content, msg.sender)
        if answer == 0:
            logger.error('请求错误')
            answer = '[-] 请求错误'
        else:
            logger.info('{}: {}', msg.sender, content)
            print(f'[+] 千问: {answer}')
        wcf.send_text(answer, msg.sender)
