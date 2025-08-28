import subprocess
import time
import re
from appscript import app
from datetime import datetime

# -------------------------------
# 配置
# -------------------------------
TARGET_WINDOW_NAME = "Qwen - ts-playground"
WORKING_DIR = "/Users/kingsonwu/programming/ts-src/ts-playground"
QWen_COMMAND = "qwen --proxy http://localhost:7890 --yolo"
POLL_INTERVAL = 10             # 轮询间隔（秒）
INPUT_PROMPT_TIMEOUT = 3600    # 超过1小时没有输入提示，触发ESC逻辑

LOG_FILE = "gemini_cli.log"    # 日志文件路径
LOG_TO_CONSOLE = True          # 是否输出到控制台

# -------------------------------
# 日志函数
# -------------------------------
def log(message: str, to_console: bool = LOG_TO_CONSOLE):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] {message}"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(formatted + "\n")
    if to_console:
        print(formatted)

# -------------------------------
# AppleScript 模板（统一操作指定 window/session）
# -------------------------------
CREATE_WINDOW_SCRIPT = f"""
tell application "iTerm2"
    set targetWindow to missing value
    repeat with w in windows
        if name of w contains "{TARGET_WINDOW_NAME}" then
            set targetWindow to w
            exit repeat
        end if
    end repeat

    if targetWindow is missing value then
        set targetWindow to (create window with default profile)
        set name of targetWindow to "{TARGET_WINDOW_NAME}"
        tell current session of targetWindow
            write text "cd {WORKING_DIR}"
            write text "{QWen_COMMAND}"
        end tell
    end if
end tell
"""

READ_OUTPUT_SCRIPT = f"""
tell application "iTerm2"
    set targetWindow to missing value
    repeat with w in windows
        if name of w contains "{TARGET_WINDOW_NAME}" then
            set targetWindow to w
            exit repeat
        end if
    end repeat
    if targetWindow is not missing value then
        tell current session of targetWindow
            return contents
        end tell
    else
        return ""
    end if
end tell
"""

# 通用写命令模板（含回车）
WRITE_COMMAND_SCRIPT = """
tell application "iTerm2"
    set targetWindow to missing value
    repeat with w in windows
        if name of w contains "%s" then
            set targetWindow to w
            exit repeat
        end if
    end repeat
    if targetWindow is not missing value then
        tell current session of targetWindow
            write text "%s"
            write text ""
        end tell
    end if
end tell
"""

# 方案2 ESC模板
SEND_ESC_SCRIPT = """
tell application "iTerm2"
    set targetWindow to missing value
    repeat with w in windows
        if name of w contains "%s" then
            set targetWindow to w
            exit repeat
        end if
    end repeat
    if targetWindow is not missing value then
        tell current session of targetWindow
            write text "\\033"
        end tell
    end if
end tell
"""

# -------------------------------
# AppleScript 执行函数
# -------------------------------
def run_applescript(script, window_name=None, command=None):
    try:
        if command:
            script = script % (window_name, command) if window_name else script % command
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        log(f"AppleScript error: {e.stderr}")
        return None

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
            log(f"Rule check error: {e}")
    return "continue"

# -------------------------------
# 主循环
# -------------------------------
def main():
    # 确保 iTerm2 窗口存在并运行 CLI
    run_applescript(CREATE_WINDOW_SCRIPT)
    time.sleep(5)

    last_output = ""
    last_input_prompt_time = time.time()

    while True:
        output = run_applescript(READ_OUTPUT_SCRIPT)
        if output is None:
            log("Failed to read terminal output")
            time.sleep(POLL_INTERVAL)
            continue

        # 输出变化检测
        if output != last_output:
            last_output = output

        # -------------------------------
        # 检测输入提示
        # -------------------------------
        if is_input_prompt(output):
            last_input_prompt_time = time.time()
            cmd = next_command(output)

            if cmd == "continue":
                log("No matching rule, continue waiting...")
                time.sleep(POLL_INTERVAL)
                continue

            if cmd is None:
                log("No more commands to execute. Stopping.")
                break

            log(f"Sending command: {cmd}")
            run_applescript(WRITE_COMMAND_SCRIPT, TARGET_WINDOW_NAME, cmd)
            time.sleep(20)

        # -------------------------------
        # 超时处理
        # -------------------------------
        else:
            if time.time() - last_input_prompt_time > INPUT_PROMPT_TIMEOUT:
                log("Input prompt timeout exceeded 1 hour, sending ESC via write text...")
                run_applescript(SEND_ESC_SCRIPT, TARGET_WINDOW_NAME)
                log("Sent 'continue' command after ESC")
                last_input_prompt_time = time.time()
            else:
                log("Not in input prompt, waiting...")

            time.sleep(POLL_INTERVAL)

    log("Automation finished.")

# -------------------------------
# 启动
# -------------------------------
if __name__ == "__main__":
    try:
        app("iTerm").activate()
    except Exception as e:
        log(f"Failed to activate iTerm2: {e}")
        exit(1)

    main()
