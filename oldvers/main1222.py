# Autism Helper (Related to AutismChina)
# NiceGUI Ver
# 2023 By rgzz666 & fakeai

from nicegui import ui,app
from niceguiToolkit.layout import inject_layout_tool

#import openai
import chatgpt
import OpenAIConfig

import time
import os
import sys
import json


inject_layout_tool()

global_port=10008 #Run with '--port <PORT>' to override this with the given port in params
global_apikey='fr_secrets' #Set it to 'fr_secrets' to read from ./secrets.json


f=open("./secrets.json",'r',encoding='utf-8')
fcontent=f.read()
f.close()
secrets=json.loads(fcontent)

if global_apikey=='fr_secrets':
    global_apikey=secrets['apikey']

if '--port' in sys.argv:
    global_port=int(sys.argv[sys.argv.index('--port')+1])

global_gpt='--nogpt' in sys.argv

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
    with history_pt:
        with ui.chat_message(name='ChatGPT',sent=False,avatar="http://116.198.35.73:10007/pub/chatgpt.png",\
             stamp=time.strftime("%Y/%m/%d %H:%M:%S",time.localtime(time.time()))):
            reply_text=ui.markdown()
    text = ""
    turns = []
    last_result = ""
    #问的问题
    question = prompt
    #回复的东西
    api=chatgpt.ChatCompletionsApi(global_apikey)
    response = api.create_chat_completions(config=OpenAIConfig.OpenAIConfig(
        model="gpt-3.5-turbo",
        messages=[{"role":"user","content":prompt}]),
        message_placeholder=reply_text)
    #result = response
    #last_result = result
    #turns += [question] + [result]
    #if len(turns) <= 10:
    #    text = "".join(turns)
    #else:
    #    text = "".join(turns[-10:])
    reply_text.set_content(str(response))


@ui.page("/chat")
def chat_page():
    global history_pt
    dark=ui.dark_mode()
    dark.enable()
    with ui.header(elevated=True).style('background-color: #303030').classes('items-center justify-between'):
        with ui.row():
            ui.button(on_click=lambda: left_drawer.toggle(), icon='menu').style("align-self:center").props('flat color=white')
            ui.label('AUTISM HELPER').style("align-self:center")
    with ui.column().style("width:100%"):
        with ui.card().style("width:720px;height:75%;background:#303030;align-self:center"):
            with ui.scroll_area().style("height:100%;width:100%") as history_pt:
                ui.label('消息历史')
        with ui.row().style("width:720px;height:20%;align-self:center") as msginput_pt:
            msg_input=ui.input(placeholder='Message Here').style("width:85%;align-self:center")
            ui.button(icon='send',on_click=lambda:send_msg(msg_input.value)).style("width:10%;align-self:center")


ui.run(title='Autism Helper',port=global_port,storage_secret='helper_storage')
