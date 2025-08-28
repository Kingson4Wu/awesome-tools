import subprocess
import time
import re
from appscript import app, k
import os

# 配置
TARGET_WINDOW_NAME = "Qwen - ts-playground"
WORKING_DIR = "/Users/kingsonwu/programming/ts-src/ts-playground"
QWen_COMMAND = "qwen --proxy http://localhost:7890 --yolo"
POLL_INTERVAL = 2  # 轮询间隔（秒）
COMMAND_QUEUE = [
    "Write a TypeScript function to reverse a string",
    "Generate a React component for a todo list",
    "/help"
]  # 示例命令队列

# AppleScript 模板：查找或创建 iTerm2 窗口
CREATE_WINDOW_SCRIPT = f"""
tell application "iTerm2"
    set windowList to every window
    set targetWindow to null
    repeat with aWindow in windowList
        if name of aWindow contains "{TARGET_WINDOW_NAME}" then
            set targetWindow to aWindow
            exit repeat
        end if
    end repeat

    if targetWindow is null then
        create window with default profile
        tell current window
            set name to "{TARGET_WINDOW_NAME}"
            tell current session
                write text "cd {WORKING_DIR}"
                write text "{QWen_COMMAND}"
            end tell
        end tell
    end if
end tell
"""

# AppleScript 模板：读取终端输出
READ_OUTPUT_SCRIPT = """
tell application "iTerm2"
    tell current session of current window
        return contents
    end tell
end tell
"""

# AppleScript 模板：写入命令并显式发送回车
WRITE_COMMAND_SCRIPT = """
tell application "iTerm2"
    tell current session of current window
        write text "%s"
        tell application "System Events" to keystroke return
    end tell
end tell
"""

def run_applescript(script, command=None):
    """执行 AppleScript 并返回结果"""
    try:
        if command:
            script = script % command.replace('"', '\\"')  # 转义命令中的双引号
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"AppleScript error: {e.stderr}")
        return None

def is_input_prompt(output):
    """检测输出是否包含输入提示，某行包含 '>   Type your message or @path/to/file'"""
    if not output:
        return False
    # 检查某行是否包含“>   Type your message or @path/to/file”
    return bool(
        re.search(r">.*Type your message or @[\w/]+(?:\.\w+)?", output)
    )

def main():
    # 确保 iTerm2 窗口存在并运行 Qwen CLI
    run_applescript(CREATE_WINDOW_SCRIPT)
    time.sleep(5)  # 增加初始化等待时间，确保 Qwen CLI 启动

    # 初始化命令队列
    commands = COMMAND_QUEUE.copy()
    current_command_index = 0
    last_output = ""  # 跟踪上一次输出

    while current_command_index < len(commands):
        # 读取终端输出
        output = run_applescript(READ_OUTPUT_SCRIPT)
        if output is None:
            print("Failed to read terminal output")
            time.sleep(POLL_INTERVAL)
            continue

        # 检查输出是否变化且包含输入提示
        if output != last_output and is_input_prompt(output):
            # 发送当前命令
            command = commands[current_command_index]
            print(f"Sending command: {command}")
            run_applescript(WRITE_COMMAND_SCRIPT, command)
            last_output = output  # 更新最后输出
            current_command_index += 1
            time.sleep(30)  # 增加等待时间，确保命令执行完成
        else:
            print("Waiting for input prompt or output change...")
            time.sleep(POLL_INTERVAL)

    print("All commands executed.")

if __name__ == "__main__":
    # 确保 iTerm2 正在运行
    try:
        app("iTerm").activate()
    except Exception as e:
        print(f"Failed to activate iTerm2: {e}")
        exit(1)

    main()