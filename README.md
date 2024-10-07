# WeChatFerry Countdown Bot

[English](README.md) | [简体中文](README_CN.md)

A WeChat bot based on WeChatFerry that provides countdown functionality and integrates with various AI models for chat interactions.

For a detailed project introduction, please visit my blog post: [Pi3'Notes](https://blog.pi3.fun/post/2023/12/%E5%BE%AE%E4%BF%A1%E5%AE%9A%E6%97%B6%E5%8F%91%E9%80%81%E5%80%92%E6%95%B0%E6%97%A5/)

## Features

- Countdown management (add, delete, list, set reminder time)
- Integration with multiple AI models:
  - Qwen (通义千问)
  - Qwen VL (通义千问 VL, supports image input)
  - Spark (讯飞星火)
- Automatic friend request acceptance
- Multi-user support
- Logging system

## Requirements

- Python 3.7+
- WeChatFerry
- Other dependencies listed in `requirements.txt`

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/Pi3-l22/WeChat_CountDownDay_Bot.git
   cd WeChat_CountDownDay_Bot
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up API keys:
   - Add Qwen API key to environment variables with the name `DASHSCOPE_API_KEY`
   - Update Spark API credentials in `SparkChat.py`

## Usage

Log in to the bot's WeChat account on your computer's WeChat program.

Run the main script:
```
python main.py
```

The bot will start and listen for WeChat messages.

### Commands

Enter the following commands directly in the chat window with the bot in WeChat:

- `$help`: View help information
- `$version`: View version information
- `$add [title] [date]`: Add a countdown
- `$del [title]`: Delete a countdown
- `$list`: List all countdowns
- `$set [time]`: Set daily reminder time
- `$send [wxid]`: Set countdown recipient(s)
- `$qwen`: Switch to Qwen model
- `$qwenvl`: Switch to Qwen VL model
- `$spark`: Switch to Spark model
- `$clear`: Clear model history messages

## Project Structure

- `main.py`: Main entry point and message processing
- `CountDown.py`: Countdown functionality
- `QwenChat.py`: Qwen model integration
- `QwenVL.py`: Qwen VL model integration
- `SparkApi.py`: Spark API implementation
- `SparkChat.py`: Spark model integration

## Configuration

- Countdown data is stored in `count_down_days.json`
- Contact and chatroom information is saved in `contacts.csv` and `chatroom.csv`
- Logs are saved in `run.log`

## License

This project is licensed under the MIT License - see the [MIT LICENSE](LICENSE) file for details.

## Acknowledgments

- [WeChatFerry](https://github.com/lich0821/WeChatFerry) for providing the WeChat bot framework
- [Qwen](https://github.com/QwenLM/Qwen) for the AI model
- [Spark](https://www.xfyun.cn/doc/spark/Web.html) for the AI model
