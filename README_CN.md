# WeChatFerry 倒数日机器人

[English](README.md) | [简体中文](README_CN.md)

基于WeChatFerry的微信机器人，提供倒数日功能并集成了多种AI模型用于聊天交互。

项目详细介绍见我的博客文章：[Pi3's Notes](https://blog.pi3.fun/post/2023/12/%E5%BE%AE%E4%BF%A1%E5%AE%9A%E6%97%B6%E5%8F%91%E9%80%81%E5%80%92%E6%95%B0%E6%97%A5/)

## 功能特性

- 倒数日管理（添加、删除、列表、设置提醒时间）
- 集成多种AI模型：
  - 通义千问
  - 通义千问 VL（支持图片输入）
  - 讯飞星火
- 自动通过好友请求
- 多用户支持
- 日志系统

## 系统要求

- Python 3.7+
- WeChatFerry
- 其他依赖项列在 `requirements.txt` 中

## 安装

1. 克隆仓库：
   ```
   git clone https://github.com/Pi3-l22/WeChat_CountDownDay_Bot.git
   cd WeChat_CountDownDay_Bot
   ```

2. 安装所需包：
   ```
   pip install -r requirements.txt
   ```

3. 设置API密钥：
   - 将通义千问API密钥添加到环境变量，变量名为 `DASHSCOPE_API_KEY`
   - 在 `SparkChat.py` 中更新讯飞星火API凭证

## 使用方法

在电脑的微信程序中登录机器人的微信账号

运行主脚本：
```
python main.py
```

机器人将启动并监听微信消息。

### 命令

直接在微信中对机器人的聊天框中输入以下命令：

- `$help`：查看帮助信息
- `$version`：查看版本信息
- `$add [标题] [日期]`：添加倒数日
- `$del [标题]`：删除倒数日
- `$list`：列出所有倒数日
- `$set [时间]`：设置每日提醒时间
- `$send [wxid]`：设置倒数日接收者
- `$qwen`：切换到通义千问模型
- `$qwenvl`：切换到通义千问VL模型
- `$spark`：切换到讯飞星火模型
- `$clear`：清空模型历史消息

## 项目结构

- `main.py`：主入口点和消息处理
- `CountDown.py`：倒数日功能
- `QwenChat.py`：通义千问模型集成
- `QwenVL.py`：通义千问VL模型集成
- `SparkApi.py`：讯飞星火API实现
- `SparkChat.py`：讯飞星火模型集成

## 配置

- 倒数日数据存储在 `count_down_days.json`
- 联系人和群聊信息保存在 `contacts.csv` 和 `chatroom.csv`
- 日志保存在 `run.log`

## 许可证

本项目采用MIT许可证 - 详情请见 [MIT LICENSE](LICENSE) 文件。

## 致谢

- [WeChatFerry](https://github.com/lich0821/WeChatFerry) 提供微信机器人框架
- [通义千问](https://github.com/QwenLM/Qwen) 提供AI模型
- [讯飞星火](https://www.xfyun.cn/doc/spark/Web.html) 提供AI模型

