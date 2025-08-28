import subprocess
import time
import re
from datetime import datetime

# -------------------------------
# 配置
# -------------------------------
TMUX_SESSION = "qwen_session"
WORKING_DIR = "/Users/kingsonwu/programming/ts-src/ts-playground"
QWEN_COMMAND = "qwen --proxy http://localhost:7890 --yolo"
POLL_INTERVAL = 10  # 轮询间隔（秒）
INPUT_PROMPT_TIMEOUT = 3600  # 超过1小时没有输入提示，触发ESC逻辑

LOG_FILE = "gemini_cli.log"
LOG_TO_CONSOLE = True


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
# tmux 辅助函数
# -------------------------------
def tmux_session_exists(session: str) -> bool:
    result = subprocess.run(["tmux", "has-session", "-t", session],
                            capture_output=True, text=True)
    return result.returncode == 0


def tmux_create_session(session: str):
    if not tmux_session_exists(session):
        log(f"Creating tmux session {session}")
        subprocess.run([
            "tmux", "new-session", "-d", "-s", session, "-c", WORKING_DIR
        ])
        time.sleep(3)  # 给 tmux 启动时间
        tmux_send_keys(session, QWEN_COMMAND)
        time.sleep(5)  # 给 Qwen CLI 启动时间


def tmux_send_keys(session: str, keys: str):
    log(f"[tmux] send: {keys}")
    # 1️⃣ 发文字内容
    subprocess.Popen(["tmux", "send-keys", "-t", session, keys])
    time.sleep(5)
    # 2️⃣ 单独发回车
    # subprocess.Popen(["tmux", "send-keys", "-t", session, "Enter"])
    subprocess.run(["tmux", "send-keys", "-t", session, "C-m"])


def tmux_send_enter(session: str):
    log("[tmux] send: Enter")
    subprocess.Popen(["tmux", "send-keys", "-t", session, "C-m"])


def tmux_send_escape(session: str):
    log("[tmux] send: Escape")
    subprocess.Popen(["tmux", "send-keys", "-t", session, "Escape"])


def tmux_send_backspace(session: str, count: int = 10):
    print(f"[tmux] send: Backspace x{count}")
    for _ in range(count):
        subprocess.Popen(["tmux", "send-keys", "-t", session, "C-h"])


def tmux_capture_output(session: str) -> str:
    result = subprocess.run(
        ["tmux", "capture-pane", "-t", session, "-p"],
        capture_output=True, text=True
    )
    return result.stdout


# -------------------------------
# 检测输入提示
# -------------------------------
def is_input_prompt(output: str) -> bool:
    if not output:
        return False
    return bool(re.search(r">.*Type your message or @[\w/]+(?:\.\w+)?", output))


def is_input_prompt_with_text(output: str) -> bool:
    if not output:
        return False
    # 使用非贪婪匹配，中间允许任意字符（不跨行）
    return bool(re.search(r"│ > .*? │", output))


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
    tmux_create_session(TMUX_SESSION)
    last_output = ""
    last_input_prompt_time = time.time()

    while True:
        output = tmux_capture_output(TMUX_SESSION)

        if output != last_output:
            last_output = output

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
            tmux_send_keys(TMUX_SESSION, cmd)
            time.sleep(20)
        elif is_input_prompt_with_text(output):
            log(f"Sending Enter")
            tmux_send_enter(TMUX_SESSION)
            time.sleep(20)

        else:
            if time.time() - last_input_prompt_time > INPUT_PROMPT_TIMEOUT:
                log("Input prompt timeout exceeded 1 hour, sending ESC and continue")
                # 单独发送 ESC
                tmux_send_escape(TMUX_SESSION)
                time.sleep(5)

                increase_num = 10
                backspace_num = increase_num
                tmux_send_backspace(TMUX_SESSION, backspace_num)
                output = tmux_capture_output(TMUX_SESSION)
                while not is_input_prompt(output):
                    tmux_send_backspace(TMUX_SESSION, backspace_num)
                    backspace_num = backspace_num + increase_num
                    output = tmux_capture_output(TMUX_SESSION)
                    time.sleep(2)

                # 再发送 continue
                tmux_send_keys(TMUX_SESSION, "continue")
                last_input_prompt_time = time.time()
            else:
                log("Not in input prompt, waiting...")

            time.sleep(POLL_INTERVAL)

    log("Automation finished.")


# -------------------------------
# 启动
# -------------------------------
if __name__ == "__main__":
    main()
