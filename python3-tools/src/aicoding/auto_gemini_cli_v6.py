#!/usr/bin/env python3

import iterm2
import asyncio
import time
import re
from datetime import datetime
import logging

# -------------------------------
# 配置
# -------------------------------
TARGET_WINDOW_NAME = "Qwen - ts-playground"
WORKING_DIR = "/Users/kingsonwu/programming/ts-src/ts-playground"
QWEN_COMMAND = "qwen --proxy http://localhost:7890 --yolo"
POLL_INTERVAL = 10  # 轮询间隔（秒）
INPUT_PROMPT_TIMEOUT = 3600  # 超过1小时没有输入提示，触发ESC逻辑

LOG_FILE = "gemini_cli.log"  # 日志文件路径
LOG_TO_CONSOLE = True  # 是否输出到控制台


# -------------------------------
# 日志配置
# -------------------------------
def setup_logging():
    logger = logging.getLogger('iterm2_automation')
    logger.setLevel(logging.DEBUG)  # 临时启用调试模式

    # 文件handler
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s',
                                       datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # 控制台handler
    if LOG_TO_CONSOLE:
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s',
                                              datefmt='%Y-%m-%d %H:%M:%S')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    return logger


logger = setup_logging()


# -------------------------------
# 检测输入提示
# -------------------------------
def is_input_prompt(output: str) -> bool:
    if not output:
        return False
    return bool(re.search(r">.*Type your message or @[\w/]+(?:\.\w+)?", output))


# -------------------------------
# 规则系统
# -------------------------------
RULES = [
    {"check": lambda out: True, "command": "Write a TypeScript function to reverse a string"},
    {"check": lambda out: "stringExamples.ts" in out, "command": "Generate a React component for a todo list"},
    {"check": lambda out: "no sandbox" in out, "command": "/help"},
    {"check": lambda out: "API Error" in out, "command": None},  # 停止
]


def next_command(output: str):
    for rule in RULES:
        try:
            if rule["check"](output):
                return rule["command"]
        except Exception as e:
            logger.error(f"Rule check error: {e}")
    return "continue"


# -------------------------------
# iTerm2 会话管理类
# -------------------------------
class QwenAutomation:
    def __init__(self):
        self.session = None
        self.window = None
        self.last_output = ""
        self.last_input_prompt_time = time.time()

    async def find_or_create_session(self, connection):
        """查找或创建目标窗口和会话"""
        app = await iterm2.async_get_app(connection)

        # 首先通过窗口标题查找现有窗口
        target_window = None
        logger.info(f"Looking for existing window with title: {TARGET_WINDOW_NAME}")

        for window in app.windows:
            try:
                # 获取窗口标题
                window_title = await window.async_get_variable("title") or ""
                logger.debug(f"Checking window title: '{window_title}'")

                if TARGET_WINDOW_NAME in window_title:
                    logger.info(f"Found existing window: '{window_title}'")
                    target_window = window
                    # 使用当前标签页的当前会话
                    current_tab = target_window.current_tab
                    self.session = current_tab.current_session
                    break

            except Exception as e:
                logger.debug(f"Error checking window title: {e}")
                continue

        # 如果通过标题没找到，再通过屏幕内容查找
        if not target_window:
            logger.info("No window found by title, checking screen contents...")
            for window in app.windows:
                try:
                    # 检查窗口的标签页是否包含我们要找的会话
                    for tab in window.tabs:
                        for session in tab.sessions:
                            try:
                                screen_contents = await session.async_get_screen_contents()
                                # 获取前几行内容检查
                                content_lines = []
                                max_lines = min(5, screen_contents.number_of_lines)
                                for i in range(max_lines):
                                    try:
                                        line_content = screen_contents.line(i).string
                                        content_lines.append(line_content)
                                    except:
                                        continue
                                content = "\n".join(content_lines)

                                if "qwen" in content.lower():
                                    logger.info(f"Found existing Qwen session in window")
                                    target_window = window
                                    self.session = session
                                    break
                            except Exception as e:
                                logger.debug(f"Error checking session content: {e}")
                                continue
                        if target_window:
                            break
                    if target_window:
                        break
                except Exception as e:
                    logger.debug(f"Error checking window: {e}")
                    continue

        # 如果还是没找到，创建新窗口
        if not target_window:
            logger.info(f"No existing window found, creating new window: {TARGET_WINDOW_NAME}")
            target_window = await iterm2.Window.async_create(connection)
            current_tab = target_window.current_tab
            self.session = current_tab.current_session

            # 设置窗口标题
            try:
                await target_window.async_set_title(TARGET_WINDOW_NAME)
                logger.info(f"Set new window title to: {TARGET_WINDOW_NAME}")
            except Exception as e:
                logger.warning(f"Could not set window title: {e}")

            # 初始化环境
            await self.setup_environment()
        else:
            logger.info("Using existing window/session")

        self.window = target_window

    async def setup_environment(self):
        """设置工作环境"""
        logger.info("Setting up environment...")

        # 检查是否已经在正确的环境中
        current_output = await self.get_session_output()
        if "qwen" in current_output.lower() and "type your message" in current_output.lower():
            logger.info("Qwen already running, skipping setup")
            return

        # 切换到工作目录
        logger.info(f"Changing to directory: {WORKING_DIR}")
        await self.session.async_send_text(f"cd {WORKING_DIR}")
        await asyncio.sleep(0.1)
        await self.session.async_send_text("\n")
        await asyncio.sleep(2)

        # 启动Qwen
        logger.info(f"Starting Qwen with command: {QWEN_COMMAND}")
        await self.session.async_send_text(QWEN_COMMAND)
        await asyncio.sleep(0.1)
        await self.session.async_send_text("\n")
        await asyncio.sleep(8)  # 给更多时间让Qwen启动

        logger.info("Environment setup completed")

    async def get_session_output(self):
        """获取会话输出"""
        try:
            # 获取屏幕内容
            screen_contents = await self.session.async_get_screen_contents()

            # 获取屏幕尺寸
            height = screen_contents.number_of_lines
            logger.debug(f"Screen has {height} lines")

            # 获取最后10行或全部内容
            lines_to_check = min(10, height)
            start_line = max(0, height - lines_to_check)

            output_lines = []
            for line in range(start_line, height):
                try:
                    line_content = screen_contents.line(line).string
                    if line_content.strip():  # 只保留非空行
                        output_lines.append(line_content.strip())
                except Exception as e:
                    logger.debug(f"Error reading line {line}: {e}")
                    continue

            result = "\n".join(output_lines)
            logger.debug(f"Got output: {result[:200]}...")  # 只显示前200个字符
            return result

        except Exception as e:
            logger.error(f"Failed to get session output: {e}")
            return ""

    async def send_command(self, command: str):
        """发送命令"""
        logger.info(f"Sending command: {command}")
        await self.session.async_send_text(command)
        await asyncio.sleep(0.1)  # 短暂等待
        await self.session.async_send_text("\n")  # 明确发送回车
        logger.debug("Command sent with newline")

    async def send_escape(self):
        """发送ESC键"""
        logger.info("Sending ESC key...")
        await self.session.async_send_text("\x1b")  # ESC character

    async def monitor_and_respond(self):
        """主监控循环"""
        logger.info("Starting monitoring loop...")

        while True:
            try:
                # 获取当前输出
                output = await self.get_session_output()

                if output != self.last_output:
                    self.last_output = output
                    logger.debug("Output changed")

                # 检测输入提示
                if is_input_prompt(output):
                    self.last_input_prompt_time = time.time()
                    logger.info("Input prompt detected")

                    # 应用规则获取下一个命令
                    cmd = next_command(output)

                    if cmd == "continue":
                        logger.info("No matching rule, continue waiting...")
                        await asyncio.sleep(POLL_INTERVAL)
                        continue

                    if cmd is None:
                        logger.info("No more commands to execute. Stopping.")
                        break

                    # 发送命令
                    await self.send_command(cmd)
                    await asyncio.sleep(20)  # 等待命令执行

                else:
                    # 检查超时
                    if time.time() - self.last_input_prompt_time > INPUT_PROMPT_TIMEOUT:
                        logger.warning("Input prompt timeout exceeded 1 hour, sending ESC...")
                        await self.send_escape()
                        await asyncio.sleep(2)
                        await self.send_command("continue")
                        self.last_input_prompt_time = time.time()
                    else:
                        logger.debug("Not in input prompt, waiting...")

                    await asyncio.sleep(POLL_INTERVAL)

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(POLL_INTERVAL)

        logger.info("Automation finished.")


# -------------------------------
# 主函数
# -------------------------------
async def main(connection):
    """主异步函数"""
    automation = QwenAutomation()

    try:
        # 查找或创建会话
        await automation.find_or_create_session(connection)

        # 开始监控和响应
        await automation.monitor_and_respond()

    except Exception as e:
        logger.error(f"Main execution error: {e}")
        raise


# -------------------------------
# 启动脚本
# -------------------------------
def run_automation():
    """运行自动化脚本"""
    try:
        # 启动iTerm2 Python API
        iterm2.run_until_complete(main)
    except Exception as e:
        logger.error(f"Failed to run automation: {e}")
        raise


if __name__ == "__main__":
    logger.info("Starting Qwen iTerm2 automation...")
    run_automation()