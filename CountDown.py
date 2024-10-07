from bs4 import BeautifulSoup  # 解析标签
import json
import time
import datetime
import os
from loguru import logger  # 日志输出
# from main import model

# TODO 根据接口增加功能
# TODO 根据消息类型增加功能
# TODO 将日志信息改成log日志 写入文件

# 联系人信息
contacts_dict = {}  # {'wxid': ['name', 'code']}
# 群聊信息
chatroom_dict = {}  # {'chatroom_id': ['name', 'code']}
# 倒数日信息字典
countdown_day = {}  # {'user1':{'count_down_days':{'title':'date'}, 'remind_time':'12:00', 'send_wxid':['wxid_xxx', 'xxx@chatroom']}}
# 微信消息类型
all_msg_type = {}
'''
{0: '朋友圈消息', 1: '文字', 3: '图片', 34: '语音', 37: '好友确认', 40: 'POSSIBL
EFRIEND_MSG', 42: '名片', 43: '视频', 47: '石头剪刀布 | 表情图片', 48: '位置', 4
9: '共享实时位置、文件、转账、链接', 50: 'VOIPMSG', 51: '微信初始化', 52: 'VOIPN
OTIFY', 53: 'VOIPINVITE', 62: '小视频', 66: '微信红包', 9999: 'SYSNOTICE', 10000
: '红包、系统消息', 10002: '撤回消息', 1048625: '搜狗表情', 16777265: '链接', 43
6207665: '微信红包', 536936497: '红包封面', 754974769: '视频号视频', 771751985:
'视频号名片', 822083633: '引用消息', 922746929: '拍一拍', 973078577: '视频号直播
', 974127153: '商品链接', 975175729: '视频号直播', 1040187441: '音乐链接', 10905
19089: '文件'}
'''


# 广播消息
def broadcast_msg(wcf, content):
    for user in countdown_day:
        if countdown_day[user]['count_down_days']:
            wcf.send_text(content, user)


# 保存联系人列表
def save_contacts(wcf):
    data = wcf.get_contacts()
    for i in data:
        wxid = i['wxid']
        code = i['code']
        name = i['name']
        if i['wxid'].startswith('wxid_'):
            contacts_dict[wxid] = [name, code]
        elif i['wxid'].endswith('@chatroom'):
            chatroom_dict[wxid] = [name, code]
    with open('contacts.csv', 'w', encoding='utf-8') as f:
        for i in contacts_dict:
            f.write(f'{i},{contacts_dict[i][0]},{contacts_dict[i][1]}\n')
    with open('chatroom.csv', 'w', encoding='utf-8') as f:
        for i in chatroom_dict:
            f.write(f'{i},{chatroom_dict[i][0]},{chatroom_dict[i][1]}\n')
    # print('[+] 保存联系人列表成功')
    logger.info('保存联系人列表成功')


# 获取倒数日
def get_countdown():
    global countdown_day
    if not os.path.exists('count_down_days.json'):
        # 创建一个新的文件
        with open('count_down_days.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps({}))
    with open('count_down_days.json', 'r', encoding='utf-8') as f:
        countdown_day = json.loads(f.read())
    # print('[+] 获取倒数日成功')
    logger.info('获取倒数日成功')


# 保存倒数日
def save_countdown():
    with open('count_down_days.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(countdown_day))
    # print('[+] 保存倒数日成功')
    logger.info('保存倒数日成功')


# 处理倒数日
def process_countdown(wcf):
    while True:
        try:
            # 获取当前时间
            now_time = time.strftime('%H:%M', time.localtime())
            for user in countdown_day:
                # 如果倒数日为空 则跳过
                if not countdown_day[user]['count_down_days']:
                    continue
                # 如果当前时间等于提醒时间
                if now_time == countdown_day[user]['remind_time']:
                    content = f'今天是{time.strftime("%Y-%m-%d", time.localtime())}\n'
                    for title in list(countdown_day[user]['count_down_days']):
                        # 计算还剩多少天
                        days = (datetime.datetime.strptime(countdown_day[user]['count_down_days'][title], '%Y-%m-%d')
                                - datetime.datetime.strptime(time.strftime('%Y-%m-%d', time.localtime()),
                                                             '%Y-%m-%d')).days
                        # 如果是0天 则发送提醒
                        if days == 0:
                            content += f'[!] [{title}] 就在今天!\n'
                        # 如果是最后一天 则删除倒数日
                        if days < 0:
                            countdown_day[user]['count_down_days'].pop(title)
                    for title in countdown_day[user]['count_down_days']:
                        # 计算还剩多少天
                        days = (datetime.datetime.strptime(countdown_day[user]['count_down_days'][title], '%Y-%m-%d')
                                - datetime.datetime.strptime(time.strftime('%Y-%m-%d', time.localtime()),
                                                             '%Y-%m-%d')).days
                        content += f'\n[+] [{title}]\n'
                        content += f"[{countdown_day[user]['count_down_days'][title]}] [还剩{days}天]\n"
                    for j in countdown_day[user]['send_wxid']:
                        wcf.send_text(content, j)
                    # print('[+] 发送倒数日成功')
                    logger.info('发送倒数日成功')
            time.sleep(60)  # 每分钟检查一次
        except Exception as e:
            # print('[-] 处理倒数日错误:', e)
            logger.error('处理倒数日错误:{}', e)


# 添加倒数日
def add_countdown(wcf, msg):
    stop_date = msg.content.split(' ')[2]
    title = msg.content.split(' ')[1]
    user = msg.sender
    # 检查时间格式
    try:
        time.strptime(stop_date, '%Y-%m-%d')
        # 如果倒数日已存在
        if title in countdown_day[user]['count_down_days']:
            wcf.send_text(f'[-] 倒数日 {title} 已存在', user)
            return
        # 如果时间已过
        if (datetime.datetime.strptime(stop_date, '%Y-%m-%d') - datetime.datetime.strptime(
                time.strftime('%Y-%m-%d', time.localtime()), '%Y-%m-%d')).days < 0:
            wcf.send_text(f'[-] 倒数日 {title} 时间已过', user)
            return
    except Exception as e:
        # print('[-] 添加倒数日错误:', e)
        logger.warning('添加倒数日错误:{}', e)
        wcf.send_text('[-] 添加倒数日错误', user)
    else:
        countdown_day[user]['count_down_days'][title] = stop_date
        # print(f'[+] {user} 添加倒数日 {title} {stop_date}')
        logger.info('{} 添加倒数日 {} 截止日期 {}', user, title, stop_date)
        wcf.send_text(f'[+] 添加倒数日 {title} 截止日期 {stop_date}', user)


# 删除倒数日
def del_countdown(wcf, msg):
    title = msg.content.split(' ')[1]
    user = msg.sender
    try:
        countdown_day[user]['count_down_days'].pop(title)
    except Exception as e:
        # print('[-] 删除倒数日错误:', e)
        logger.warning('删除倒数日错误:{}', e)
        wcf.send_text('[-] 删除倒数日错误', user)
    else:
        # print(f'[+] {user} 删除倒数日 {title}')
        logger.info('{} 删除倒数日 {}', user, title)
        wcf.send_text(f'[+] 删除倒数日 {title}', user)


# 列出倒数日
def list_countdown(wcf, msg):
    content = f'今天是{time.strftime("%Y-%m-%d", time.localtime())}\n\n'
    user = msg.sender
    for i in countdown_day[user]['count_down_days']:
        # 计算还剩多少天
        days = (datetime.datetime.strptime(countdown_day[user]['count_down_days'][i],
                                           '%Y-%m-%d') - datetime.datetime.strptime(
            time.strftime('%Y-%m-%d', time.localtime()), '%Y-%m-%d')).days
        content += f'[+] [{i}]\n'
        content += f"[{countdown_day[user]['count_down_days'][i]}] [还剩{days}天]\n\n"
    content += f"\n提醒时间为每天的 {countdown_day[user]['remind_time']}\n"
    content += f'发送倒数日的对象为 {countdown_day[user]["send_wxid"]}'
    # print(f'[+] {user} 列出倒数日')
    logger.info('{} 列出倒数日', user)
    wcf.send_text(content, user)


# 设置提醒时间
def set_remind_time(wcf, msg):
    global remind_time
    user = msg.sender
    try:
        time_ = msg.content.split(' ')[1]
        # 检查时间格式
        _time = time.strptime(time_, '%H:%M')
    except Exception as e:
        # print('[-] 设置提醒时间错误:', e)
        logger.warning('设置提醒时间错误:{}', e)
        wcf.send_text('[-] 设置提醒时间错误', user)
    else:
        countdown_day[user]['remind_time'] = time.strftime('%H:%M', _time)
        # print(f"[+] {user} 设置提醒时间为每天的 {countdown_day[user]['remind_time']}")
        logger.info('{} 设置提醒时间为每天的 {}', user, countdown_day[user]['remind_time'])
        wcf.send_text(f"[+] 设置提醒时间为每天的 {countdown_day[user]['remind_time']}", user)


# 设置发送倒数日的对象
def update_send_wxid(wcf, msg):
    user = msg.sender
    try:
        if ',' in msg.content.split(' ')[1]:
            send_wxid_ = msg.content.split(' ')[1].split(',')
        else:
            send_wxid_ = [msg.content.split(' ')[1]]
    except Exception as e:
        # print('[-] 设置发送倒数日的对象错误:', e)
        logger.warning('设置发送倒数日的对象错误:{}', e)
        wcf.send_text('[-] 设置发送倒数日的对象错误', user)
    else:
        countdown_day[user]['send_wxid'] = send_wxid_
        # print(f'[+] {user} 设置发送倒数日的对象为 {send_wxid_}')
        logger.info('{} 设置发送倒数日的对象为 {}', user, send_wxid_)
        wcf.send_text(f'[+] 设置发送倒数日的对象为 {send_wxid_}', user)


# 初始化用户数据
def init_user_data(wcf, msg):
    user = msg.sender
    if user not in countdown_day:
        # model[user] = 'qwen'  # 默认使用通义千问大模型
        countdown_day[user] = {'count_down_days': {}, 'remind_time': '12:00', 'send_wxid': [user]}
        # print(f'[+] 初始化用户 {user} 数据')
        logger.info('初始化用户 {} 数据', user)
        # wcf.send_text('[+] 初始化用户数据', user)


# 自动通过好友申请
def auto_accept_friend(wcf, msg):
    try:
        # 解析msg.content
        soup = BeautifulSoup(msg.content, 'html.parser')
        # 获取微信号
        alias = soup.msg['alias']
        # 获取wxid
        wxid = soup.msg['fromusername']
        # 获取昵称
        nickname = soup.msg['fromnickname']
        # 获取v3
        v3 = soup.msg['encryptusername']
        # 获取v4
        v4 = soup.msg['ticket']
        # 添加方式
        scene = int(soup.msg['scene'])  # 3:通过微信号 30:通过二维码
        # 添加好友
        wcf.accept_new_friend(v3=v3, v4=v4, scene=scene)
    except Exception as e:
        # print('[-] 自动通过好友申请错误:', e)
        logger.error('自动通过好友申请错误:{}', e)
    else:
        # print(f'[+] 自动通过好友申请 {nickname} {wxid}')
        logger.info('自动通过好友申请 {} {}', nickname, wxid)
        time.sleep(3)  # 等待3秒
        rev = f'Halo~👋 {nickname}\n\n[+] 你的wxid为:\n[{wxid}]\n[+] 你的微信号为:\n[{alias}]\n\n你可以发送$help查看帮助信息'
        wcf.send_text(rev, wxid)
