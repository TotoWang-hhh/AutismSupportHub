# Autism Helper（自闭症关爱项目相关）
# NiceGUI重写

from nicegui import ui
from niceguiToolkit.layout import inject_layout_tool
import openai

import time
import os
import sys


#inject_layout_tool()

global_port=10008




if '--port' in sys.argv:
    global_port=int(sys.argv[sys.argv.index('--port')+1])

if '--autoclear' in sys.argv:
    if os.name=='nt':
        os.system("cls")
    else:
        os.system("clear")


def send_msg(prompt):
    global history_pt
    with history_pt:
        ui.chat_message(str(prompt),name='You',sent=True,
        stamp=time.strftime("%Y/%m/%d %H:%M:%S",time.localtime(time.time()))).style("align-self:end")
    return_msg='Return Message' #临时用一个固定的字符串代替ChatGPT返回内容
    with history_pt:
        ui.chat_message(str(return_msg),name='ChatGPT',sent=False,avatar="http://116.198.35.73:10007/pub/chatgpt.png",
        stamp=time.strftime("%Y/%m/%d %H:%M:%S",time.localtime(time.time())))

@ui.page("/chat")
def chat_page():
    global history_pt
    dark=ui.dark_mode()
    dark.enable()
    with ui.header(elevated=True).style('background-color: #303030').classes('items-center justify-between'):
        with ui.row():
            ui.button(on_click=lambda: left_drawer.toggle(), icon='menu').style("align-self:center").props('flat color=white')
            ui.label('AUTISM HELPER').style("align-self:center")
    with ui.card().style("height:540px;width:70%;background:#303030"):
        with ui.scroll_area().style("height:100%;width:100%") as history_pt:
            ui.label('消息历史')
    with ui.row().style("width:70%") as msginput_pt:
        msg_input=ui.input(placeholder='Message Here').style("width:85%;align-self:center")
        ui.button(icon='send',on_click=lambda:send_msg(msg_input.value)).style("width:10%;align-self:center")



ui.run(title='Autism Helper',port=global_port,storage_secret='helper_storage')
