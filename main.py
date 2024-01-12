# Autism Helper (Related to AutismChina)
# NiceGUI Ver
# 2023 By rgzz666 & fakeai
# Requires Python version 3.10+

from nicegui import ui,app,run
#from niceguiToolkit.layout import inject_layout_tool

import effects

#import openai
import chatgpt
import OpenAIConfig

import time
import os
import sys
import json
import threading


#inject_layout_tool()

# 反复修改本行注释来使服务端重载更新内容

global_addr='fr_config' #Set it to 'fr_config' to read from ./config.json
global_ssl='fr_config' #Set it to 'fr_config' to read from ./config.json
global_port=10008 #Run with '--port <PORT>' to override this with the given port in params
global_apikey='fr_secrets' #Set it to 'fr_secrets' to read from ./secrets.json
global_maxcontext=3
global_rule='fr_file' #Set it to 'fr_file' to read from ./gpt_rule.txt
global_adminpwd='fr_secrets' #Set it to 'fr_secrets' to read from ./secrets.json


##### CODE BELOW #####
visits=0
promps=0


def split_string_by_length(string, length):
    return [string[i:i+length] for i in range(0, len(string), length)]

f=open("./secrets.json",'r',encoding='utf-8')
fcontent=f.read()
f.close()
secrets=json.loads(fcontent)

f=open("./config.json",'r',encoding='utf-8')
fcontent=f.read()
f.close()
config=json.loads(fcontent)

if global_addr=='fr_config':
    global_addr=config['addr']

if global_ssl=='fr_config':
    global_ssl=config['ssl']

if global_rule=='fr_file':
    f=open("./gpt_rule.txt",'r',encoding='utf-8')
    fcontent=f.read()
    f.close()
    global_rule=fcontent

if global_apikey=='fr_secrets':
    global_apikey=secrets['apikey']

if global_adminpwd=='fr_secrets':
    global_adminpwd=secrets['admin_pwd']

if '--port' in sys.argv:
    global_port=int(sys.argv[sys.argv.index('--port')+1])

global_gpt='--nogpt' in sys.argv

if '--autoclear' in sys.argv:
    if os.name=='nt':
        os.system("cls")
    else:
        os.system("clear")


### Classes & Functions ###
def call_func_list(func_list):
    for func in func_list:
        func()

def confirm(action,description='继续',detail=None):
    def confirm_yes(action,dlg):
        action()
        dlg.close()
    with ui.dialog() as confirm_dlg,ui.card():
        ui.label("您确定要 "+str(description)+" 吗？").style("font-weight:bolder;font-size:18px")
        if detail!=None or detail!='':
            ui.label(str(detail))
        with ui.row().style("width:95%;align-self:center"):
            ui.button('取消',on_click=confirm_dlg.close).style("width:45%")
            ui.button('继续',on_click=lambda:confirm_yes(action,confirm_dlg),color='red').style("width:45%")
    confirm_dlg.open()

def load_history(historypt):
    hlist=app.storage.user['history']
    #hlist=app.storage.user.get('history',0)
    for h in hlist:
        match h['role']:
            case "user":
                with historypt:
                    ui.chat_message(h["content"],name='You',sent=True,stamp=time.strftime("%Y/%m/%d %H:%M:%S",time.localtime(time.time()))).style("align-self:end")
            case "assistant":
                with historypt:
                    with ui.chat_message(name='ChatGPT',sent=False,avatar="http://116.198.35.73:10007/chatgpt.png",stamp=time.strftime("%Y/%m/%d %H:%M:%S",time.localtime(time.time()))):
                        ui.markdown(h["content"])
            case _:
                pass
    historypt.scroll_to(percent=1)

async def askgpt(historylist,msg_placeholder,history_pt):
    global global_maxcontext,global_rule
    #if len(historylist)>global_maxcontext:
    #    listorylist=[{"role":"system","content":str(global_rule)},historylist[len(historylist)-2],historylist[len(historylist)-1]]
    try:
        context_list=historylist[len(historylist)-(global_maxcontext-1):]
        context_list.insert(0,{"role":"system","content":str(global_rule)})
        api=chatgpt.ChatCompletionsApi(global_apikey)
        config = OpenAIConfig.OpenAIConfig(
            model="gpt-3.5-turbo",
            messages=context_list)
        #print(historylist[len(historylist)-(global_maxcontext-1):])
        response = await run.io_bound(lambda:api.create_chat_completions(config,msg_placeholder,msglist=history_pt))
        return response
    except Exception as e:
        #a=abc #取消注释此行，产生错误，使异常处理失效，在控制台查看完整报错
        return 'Error: \n\n```'+str(e)+'```'

async def send_msg(prompt,history_pt):
    global promps
    promps+=1
    #historylist=[] #暂时充当聊天记录列表
    #global history_pt
    history_pt.scroll_to(percent=1)
    with history_pt:
        ui.chat_message(str(prompt),name='您',sent=True,stamp=time.strftime("%Y/%m/%d %H:%M:%S",time.localtime(time.time()))).style("align-self:end")
        #historylist.append({"role":"user","content":prompt})
        #存储用户问题
        app.storage.user['history'].append({"role":"user","content":prompt})
    with history_pt:
        with ui.chat_message(name='ChatGPT',sent=False,avatar="http://116.198.35.73:10007/chatgpt.png",stamp=time.strftime("%Y/%m/%d %H:%M:%S",time.localtime(time.time()))):
            reply_text=ui.markdown()
            #reply_text.on('change',history_pt.scroll_to(percent=1))
    history_pt.scroll_to(percent=1)
    #text = ""
    #turns = []
    last_result = ""
    #问的问题
    question = prompt
    #回复的东西
    response=await askgpt(app.storage.user.get('history',0),reply_text,history_pt)
    #result = response
    #last_result = result
    #turns += [question] + [result]
    #if len(turns) <= 10:
    #    text = "".join(turns)
    #else:
    #    text = "".join(turns[-10:])
    with history_pt:
        #historylist.append({"role":"assistant","content":response})
        app.storage.user['history'].append({"role":"assistant","content":response})
    reply_text.set_content(str(response))
    history_pt.scroll_to(percent=1)

async def copy_text(text,notify='已复制文本'):
    global global_ssl
    if global_ssl:
        ui.run_javascript(f"navigator.clipboard.writeText('"+str(text)+"')")
        ui.notify(str(notify))
    else:
        ui.notify('站点未使用HTTPS，无法复制，请手动选中复制')


### COMPONENTS ###
def home_douknow(left_txt:str,right_txt:str,height:int=124):
    with ui.row().style("width:80%;align-self:center;height:"+str(height)+"px"):
        with ui.card().style("width:45%;align-self:center;height:100%"):
            ui.label(left_txt)
        with ui.card().style("width:45%;align-self:center;height:100%"):
            placeholder1=ui.label('')
            showans_btn=''
            showans_btn=ui.button("点我！",on_click=lambda:run.io_bound(lambda:call_func_list([showans_btn.delete,lambda:effects.typewriter(
                [right_txt],text_placeholder=placeholder1,repeat=False)]))).style("color:#0078dc;width:70%;align-self:center")


### PAGES ###
@ui.page("/chat")
def chat_page():
    global visits
    visits+=1
    with ui.left_drawer(bottom_corner=True).style('background-color: #f0f0f0') as left_drawer:
        with ui.card().style("width:100%"):
            ui.label('免责声明').style("font-weight:bolder")
            ui.label("此处替换为新免责声明").style("width:100%")
        ui.label('操作')
    with ui.header(elevated=True).style('background-color: #303030').classes('items-center justify-between'):
        with ui.row():
            ui.button(on_click=lambda: left_drawer.toggle(), icon='menu').style("align-self:center").props('flat color=white')
            ui.label('AUTISM SUPPORT').style("align-self:center")
        #ui.label('所有答复仅供参考，切勿直接按其行事，出现任何问题本项目概不负责')
    with ui.column().style("width:100%;height:85vh"):
        with ui.card().style("width:100%;max-width:720px;height:75%;background:#f0f0f0;align-self:center"):
            with ui.scroll_area().style("height:100%;width:100%") as history_pt:
                ui.label('消息历史')
        with ui.row().style("width:100%;max-width:720px;height:20%;align-self:center") as msginput_pt:
            msg_input=ui.textarea(placeholder='输入问题…').style("width:85%;align-self:center").props('outlined dense')
            ui.button(icon='send',on_click=lambda:send_msg(msg_input.value,history_pt)).style("width:10%;align-self:center")
    #print(app.storage.user.get('history',0),'  |  ',app.storage.user['history'])
    if app.storage.user.get('history',0)==0:
        app.storage.user['history']=[]
        ui.notify('已初始化用户数据')
    load_history(history_pt)
    ui.notify("已加载记录")
    #app.on_connect(lambda:init_page(history_pt))
    #history_pt.scroll_to(percent=1)
    #print("hi?")

@ui.page("/admin")
def admin():
    global visits,promps
    with ui.header(elevated=True).style('background-color: #303030').classes('items-center justify-between'):
        with ui.row():
            ui.label('AUTISM SUPPORT | Admin').style("align-self:center")
    with ui.row().style("width:95%"):
        ui.label('操作').style("font-weight:bolder;font-size:24px")
        with ui.card().style("width:35%"):
            ui.label('快速操作')
            ui.button('关闭网页',on_click=lambda:confirm(app.shutdown,'关闭网页',detail='若未启用自动重载，继续会导致网页服务停止，仅可在服务器再次启动。'))
            ui.button('退出服务端',on_click=lambda:confirm(lambda:os._exit(1),'退出服务端',detail='若未启用自动重载则会推出服务端。退出后网页服务将停止，仅可在服务器再次启动。'))
        with ui.card().style("width:55%"):
            ui.label('发送系统命令')
            with ui.row().style("width:95%"):
                cmd_input=ui.input(placeholder='输入命令').style("width:65%")
                apply_btn=ui.button('执行',on_click=lambda:call_func_list([lambda:os.system(cmd_input.value),lambda:ui.notify("已执行")])).style("width:30%")
                apply_btn.disable()
            ui.label('点击启用该功能').style("color:#0078dc").on('click',lambda:confirm(lambda:call_func_list([apply_btn.enable,lambda:ui.notify('已启用远程命令执行功能')]),
                                                                                 '启用远程命令执行','直接执行命令可能会导致未知问题'))
    with ui.row().style("width:95%"):
        ui.label('统计').style("font-weight:bolder;font-size:24px")
        with ui.card().style("width:90%"):
            with ui.row().style("width:100%"):
                ui.label("注：访问统计数据从服务端启动/重启截至本次进入后台时").style("font-weight:bolder;color:#007000")
                ui.label("访问次数："+str(visits))
                ui.label("询问次数："+str(promps))
    # 管理密码输入框
    with ui.dialog().props('persistent') as pwd_dlg,ui.card():
        pwd_input=ui.input(placeholder='输入管理密码',password=True,password_toggle_button=True).style("width:100%")
        ui.button('进入后台',on_click=lambda:pwd_dlg.close() if pwd_input.value==global_adminpwd else ui.notify('密码错误')).style("width:100%")
        ui.label("管理密码明文存储于服务端目录下的secrets.json")
        pwd_dlg.open()

@ui.page("/")
async def home():
    #ui.label('test')
    with ui.column().style("width:100%"):
        with ui.card().style("align-self:center;width:100%;background:#303030").props('flat'):
            with ui.column().style("align-self:center;background:#303030"):
                ui.label("[BLANK]").style("font-size:48px;font-weight:bolder;color:#303030")
                ui.label("The").style("font-size:72px;font-weight:bolder;color:#ffffff")
                projname_txt=ui.label("Autism Support").\
                              style("font-size:120px;font-weight:bolder;background-image:linear-gradient(135deg, #DA5050 25%,#FFCE73 75%);background-clip:text;color: transparent")
                ui.label("Project").style("font-size:72px;font-weight:bolder;color:#ffffff")
                ui.label("WE NEED PEOPLE !").style("font-size:48px;font-weight:bolder;color:#303030")
        with ui.card().style("width:100%").props("flat"):
            with ui.row().style("align-self:center"):
                with ui.dialog() as copyurl_dlg,ui.card():
                    ui.label('复制本站链接，并发给身边有需要的人').style("align-self:center")
                    url_txt=ui.label('http://'+str(global_addr)+':'+str(global_port)+'/').style("width:100%;max-width:480px;background:#eeeeff;font-size:18px;align-self:center")
                    #copy_cmd='navigator.clipboard.writeText("'+'http://'+str(global_addr)+':'+str(global_port)+'/'+'")'
                    ui.button("复制到剪贴板",on_click=lambda:copy_text('http://'+str(global_addr)+':'+str(global_port)+'/')).style("width:100%")
                    #url_txt.value='http://'+str(global_addr)+':'+str(global_port)+'/'
                ui.button("开始提问",on_click=lambda:ui.open("/chat")).props("flat color=black")
                with ui.button("帮助我们").props("flat color=black"):
                    with ui.menu() as helpus_options:
                        ui.menu_item('传播本站',copyurl_dlg.open)
                        ui.menu_item('加入我们',lambda:ui.notify('感谢，但是我们目前不需要过多的人哦！'))
                ui.button("关于自闭症").props("flat color=black")
        with ui.row().style("width:80%;align-self:center"):
            autism_count=500000000 #数据蒙眼乱编，仅供效果参考
            people_count=1400000000
            ui.echart({"type":"pie","data":[{"name":"Autism","value":autism_count},{"name":"Normal","value":people_count-autism_count}]})
        with ui.column().style("width:100%;max-width:720px;align-self:center;background:#f0f0f0"):
            ui.label('【很闲吗？】').style("font-size:28px;font-weight:bolder;align-self:center;color:#f0f0f0")
            ui.label('您知道吗？').style("font-size:28px;font-weight:bolder;align-self:center")
            home_douknow("您知道吗？这个网站虽然看起来啥也不是，","它的确也啥也不是……")
            ui.label('你居然看到底了欸！但是……【很闲吗？】').style("font-size:28px;font-weight:bolder;align-self:center;color:#f0f0f0")
            


### Print Config ###
if not '--noclear' in sys.argv:
    if os.name=='nt':
        os.system("cls")
    else:
        os.system("clear")
    print("["+time.strftime("%Y/%m/%d %H:%M:%S",time.localtime(time.time()))+"] 程序启动，已清屏\n（若要禁用启动时清屏，请在启动时传入“--noclear”参数）\n\n")

console_w=os.get_terminal_size().columns

print("=====本次启动/重启的配置内容=====")
print("--API Key："+global_apikey[0:len(global_apikey)-20-1]+"********************")
print("--端口："+str(global_port))
print("--上下文限制："+str(global_maxcontext)+"(-1)")
print("--问答规则：")
for l in global_rule.split('\n'):
    for t in split_string_by_length(l,console_w):
        print("| "+t)
#print(global_rule)
print("")


### Run UI ###
ui.run(title='Autism Support',port=global_port,storage_secret='autism_storage')
