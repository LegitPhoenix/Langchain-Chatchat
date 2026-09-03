"""Usage
加载本地模型：
python webui_allinone.py

调用远程api服务：
python webui_allinone.py --use-remote-api

后台运行webui服务：
python webui_allinone.py --nohup

加载多个非默认模型：
python webui_allinone.py --model-path-address model1@host1@port1 model2@host2@port2 

多卡启动：
python webui_alline.py --model-path-address model@host@port --num-gpus 2 --gpus 0,1 --max-gpu-memory 10GiB

"""
import streamlit as st
from webui_pages.utils import *
from streamlit_option_menu import option_menu
from webui_pages import *
import os
from server.llm_api_stale import string_args,launch_all,controller_args,worker_args,server_args,LOG_PATH

from server.api_allinone_stale import parser, api_args
import subprocess
import re

parser.add_argument("--use-remote-api",action="store_true")
parser.add_argument("--nohup",action="store_true")
parser.add_argument("--server.port",type=int,default=8501)
parser.add_argument("--theme.base",type=str,default='"light"')
parser.add_argument("--theme.primaryColor",type=str,default='"#165dff"')
parser.add_argument("--theme.secondaryBackgroundColor",type=str,default='"#f5f5f5"')
parser.add_argument("--theme.textColor",type=str,default='"#000000"')
web_args = ["server.port","theme.base","theme.primaryColor","theme.secondaryBackgroundColor","theme.textColor"]


def validate_theme_base(value):
    return value in ['"light"', '"dark"', 'light', 'dark']

def validate_hex_color(value):
    pattern = r'^"#[0-9a-fA-F]{6}"$'
    return re.match(pattern, value) is not None

def validate_port(value):
    return isinstance(value, int) and 1 <= value <= 65535


def launch_api(args,args_list=api_args,log_name=None):
    print("Launching api ...")
    print("启动API服务...")
    if not log_name:
        log_name = f"{LOG_PATH}api_{args.api_host}_{args.api_port}"
    print(f"logs on api are written in {log_name}")
    print(f"API日志位于{log_name}下，如启动异常请查看日志")
    
    cmd_list = ['python', 'server/api.py']
    for arg_name in args_list:
        arg_value = getattr(args, arg_name.replace('-', '_'), None)
        if any(char in str(arg_value) for char in [';', '&', '|', '$', '`', '\n', '(', ')', '<', '>']):
            raise ValueError(f"Invalid characters in argument {arg_name}: {arg_value}")
        if arg_value is not None:
            cmd_list.append(f'--{arg_name}')
            cmd_list.append(str(arg_value))
    
    with open(f"{log_name}.log", 'w') as log_file:
        subprocess.Popen(cmd_list, stdout=log_file, stderr=subprocess.STDOUT)
    print("launch api done!")
    print("启动API服务完毕.")

def launch_webui(args,args_list=web_args,log_name=None):
    print("Launching webui...")
    print("启动webui服务...")
    if not log_name:
        log_name = f"{LOG_PATH}webui"

    cmd_list = ['streamlit', 'run', 'webui.py']
    for arg_name in args_list:
        arg_value = getattr(args, arg_name.replace('-', '_').replace('.', '_'), None)
        if arg_name == "theme.base" and not validate_theme_base(str(arg_value)):
            raise ValueError(f"Invalid theme.base value: {arg_value}")
        if arg_name in ["theme.primaryColor", "theme.secondaryBackgroundColor", "theme.textColor"] and not validate_hex_color(str(arg_value)):
            raise ValueError(f"Invalid color value for {arg_name}: {arg_value}")
        if arg_name == "server.port" and not validate_port(arg_value):
            raise ValueError(f"Invalid port value: {arg_value}")
        if arg_value is not None:
            cmd_list.append(f'--{arg_name}')
            cmd_list.append(str(arg_value))
    
    if args.nohup:
        print(f"logs on api are written in {log_name}")
        print(f"webui服务日志位于{log_name}下，如启动异常请查看日志")
        with open(f"{log_name}.log", 'w') as log_file:
            subprocess.Popen(cmd_list, stdout=log_file, stderr=subprocess.STDOUT)
    else:
        subprocess.run(cmd_list, check=True)
    print("launch webui done!")
    print("启动webui服务完毕.")


if __name__ == "__main__":
    print("Starting webui_allineone.py, it would take a while, please be patient....")
    print(f"开始启动webui_allinone,启动LLM服务需要约3-10分钟，请耐心等待，如长时间未启动，请到{LOG_PATH}下查看日志...")
    args = parser.parse_args()

    print("*"*80)
    if not args.use_remote_api:
        launch_all(args=args,controller_args=controller_args,worker_args=worker_args,server_args=server_args)
    launch_api(args=args,args_list=api_args)
    launch_webui(args=args,args_list=web_args)
    print("Start webui_allinone.py done!")
    print("感谢耐心等待，启动webui_allinone完毕。")