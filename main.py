from wcferry import Wcf  # 微信机器人
from queue import Empty  # 队列
from threading import Thread  # 多线程
from loguru import logger  # 日志输出
import sys
import CountDown as Cd  # 倒数日功能模块
import SparkChat as Sc  # 讯飞星火功能模块
import QwenChat as Qc  # 通义千问功能模块
import QwenVL as Qvl  # 通义千问VL功能模块

# 聊天模型选择
model = {}  # qwen:千问模型 spark:星火模型 qwenvl:千问VL模型

# 日志输出到文件
logger.add('run.log', format='{time} {level} {message}', retention="10 days")

# 版本信息
def version_info(wcf, msg):
    content = '''[+] 版本信息
[+] 版本号: 4.0.1

1. 倒数日功能
2. 讯飞星火大模型
3. 通义千问大模型
4. 通义千问VL模型(支持图片)

[+] 作者: Pi3
'''
    # print(f'[+] {msg.sender} 查看版本信息')
    logger.info('{} 查看版本信息', msg.sender)
    wcf.send_text(content, msg.sender)

# 帮助信息
def help_info(wcf, msg):
    content = '''[+] 帮助信息 

$help 查看帮助信息
$version 查看版本信息
$add [title] [date] 添加倒数日 
$del [title] 删除倒数日
$list 列出倒数日
$set [time] 设置每天提醒时间 
$send [wxid] 发送倒数日的对象
$qwen 指定千问模型
$qwenvl 指定千问VL模型
$spark 指定星火模型
$clear 清空模型历史消息

[+] 格式示例

$add 生日 2024-10-01
$del 生日
$set 12:00
$send xxx@chatroom,wxid_xxx
'''
    # print(f'[+] {msg.sender} 查看帮助信息')
    logger.info('{} 查看帮助信息', msg.sender)
    wcf.send_text(content, msg.sender)


# 处理消息
def process_msg(wcf):
    global model, msg
    while wcf.is_receiving_msg():
        try:
            msg = wcf.get_msg()
            msg_type = msg.type  # 消息类型
            # msg_id = msg.id  # 消息id
            if Cd.all_msg_type[msg_type] == '文字':  # 如果是文字消息 1
                # 如果用户不在倒数日数据中 则初始化用户数据
                if msg.sender not in Cd.countdown_day:
                    Cd.init_user_data(wcf, msg)  # 初始化用户数据
                if msg.sender.startswith('wxid_'):
                    content = msg.content
                    if content.startswith('$add'):  # 添加倒数日
                        Cd.add_countdown(wcf, msg)
                    elif content.startswith('$del'):  # 删除倒数日
                        Cd.del_countdown(wcf, msg)
                    elif content == '$list':  # 列出倒数日
                        Cd.list_countdown(wcf, msg)
                    elif content == '$help':  # 帮助信息
                        help_info(wcf, msg)
                    elif content.startswith('$set'):  # 设置提醒时间
                        Cd.set_remind_time(wcf, msg)
                    elif content.startswith('$send'):  # 设置发送倒数日的对象
                        Cd.update_send_wxid(wcf, msg)
                    elif content == '$version':  # 版本信息
                        version_info(wcf, msg)
                    elif content == '$clear':  # 清空历史消息
                        Sc.clear_history(wcf, msg)
                        Qc.clear_history(wcf, msg)
                    elif content == '$qwen':  # 指定千问模型
                        model[msg.sender] = 'qwen'
                        wcf.send_text('[+] 选择通义千问大模型', msg.sender)
                    elif content == '$spark':  # 指定星火模型
                        model[msg.sender] = 'spark'
                        wcf.send_text('[+] 选择讯飞星火大模型', msg.sender)
                    elif not msg.from_self():  # 大模型聊天
                        try:
                            if model[msg.sender] == 'qwen':
                                Qc.qwen_chat(wcf, msg)
                            elif model[msg.sender] == 'spark':
                                Sc.spark_chat(wcf, msg)
                            elif model[msg.sender] == 'qwenvl':
                                Qvl.qwen_vl(wcf, msg)
                            else:
                                logger.warning('未知聊天模型')
                                wcf.send_text('[-] 未知聊天模型', msg.sender)
                        except KeyError:
                            logger.warning('未指定聊天模型')
                            wcf.send_text('[-] 未指定聊天模型', msg.sender)
            elif Cd.all_msg_type[msg_type] == '图片':  # 如果是图片消息 3
                if msg.sender.startswith('wxid_'):  # 如果是私聊
                    if not msg.from_self():  # 如果不是自己发的
                        model[msg.sender] = 'qwenvl'  # 使用通义千问VL大模型
                        Qvl.receive_image(wcf, msg)  # 接收图片并下载
            elif Cd.all_msg_type[msg_type] == '好友确认':  # 如果是好友确认消息 37
                Cd.auto_accept_friend(wcf, msg)  # 自动通过好友申请
        except Empty:
            continue
        except Exception as e:
            wcf.send_text(f'[-] 操作错误', msg.sender)
            logger.error('处理消息错误:{}', e)
            # print('[-] 处理消息错误:', e)


def main():
    wcf = Wcf()
    # 获取所有消息类型
    Cd.all_msg_type = wcf.get_msg_types()
    # 保存联系人列表
    Cd.save_contacts(wcf)
    # 获取倒数日
    Cd.get_countdown()
    # 广播上线消息
    Cd.broadcast_msg(wcf, '[+] 服务已恢复 正常运行中')
    logger.info('发送上线广播消息')
    # print('[+] 发送上线广播消息')
    # 处理倒数日
    Thread(target=Cd.process_countdown, args=(wcf,), daemon=True).start()
    # 处理消息
    wcf.enable_receiving_msg()
    Thread(target=process_msg, args=(wcf,), daemon=True).start()
    logger.info('服务启动成功')
    # print('[+] 服务启动成功')
    return wcf


if __name__ == '__main__':
    wcf = None
    try:
        wcf = main()
        wcf.keep_running()
    except KeyboardInterrupt:
        # 广播停止消息
        Cd.broadcast_msg(wcf, '[-] 服务已停止 正在维护中')
        logger.info('发送下线广播消息')
        # print('[+] 发送下线广播消息')
        Cd.save_countdown()
        logger.info('保存倒数日数据')
        # print('[*] 清理并回收资源')
        wcf.cleanup()
        logger.info('清理并回收资源')
        logger.critical('服务已停止')
        # print('[-] 服务已停止')
        sys.exit(0)
