"""
调用示例：
python llm_api_shutdown.py --serve all
可选"all","controller","model_worker","openai_api_server"， all表示停止所有服务
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import subprocess
import argparse
import psutil

parser = argparse.ArgumentParser()
parser.add_argument("--serve", choices=["all", "controller", "model_worker", "openai_api_server"], default="all")

args = parser.parse_args()

if args.serve == "all":
    search_pattern = "fastchat.serve"
else:
    search_pattern = f"fastchat.serve.{args.serve}"

killed_count = 0
for proc in psutil.process_iter(['pid', 'cmdline']):
    try:
        cmdline = proc.info['cmdline']
        if cmdline and any(search_pattern in arg for arg in cmdline):
            proc.kill()
            killed_count += 1
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass

print(f"llm api sever --{args.serve} has been shutdown!")
