import tkinter
from tkinter import ttk
import requests
import re
import urllib.request,urllib.error
import bs4
import os
import urllib.parse
from fake_useragent import UserAgent
import time
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import tkinter as tk
#设置cookie
cookie = {
    '_uid': '1097055',
    '__client_id': '6d44000048a6adae6f6f7b4405948d69419b9c06',
}
data=[]
ProblemUrl = "https://www.luogu.com.cn/problem/"
ListUrl = "https://www.luogu.com.cn/problem/list?"
UrlSolution = "https://www.luogu.com.cn/problem/solution/"
savePath = r"C:\Users\12979\Desktop\luogu_crawler\project\\"

# 反爬设置，使用fake_useragent库随机生成一个User-Agent
ua = UserAgent()
random_user_agent = ua.chrome

#获取题目内容：背景，描述。。。
def get_question(html):
    bs = bs4.BeautifulSoup(html,"html.parser")
    core = bs.select("article")[0]
    md = str(core)
    ques=""
    content_pid = re.compile(r'<h1>.*?</h1>')
    matches = re.findall(content_pid, md)
    ques=matches[0]
    ques = re.sub("<h1>", "",ques)
    ques = re.sub("</h1>", "", ques)
    md = re.sub("<h1>","# ",md)
    md = re.sub("<h2>","## ",md)
    md = re.sub("<h3>","#### ",md)
    md = re.sub("</?[a-zA-Z]+[^<>]*>","",md)
    return md,ques
#获取题解
def get_answer(html):
    soup = bs4.BeautifulSoup(html, "html.parser")
    lock_F = soup.find('script')
    lock_S = lock_F.text
    begin = lock_S.find('"')
    endword = lock_S.find('"', begin + 1)
    lock_S = lock_S[begin + 1:endword]
    #解码
    #1.对字符串进行URL解码，将特殊字符转义为原始字符。然后，
    #2.将字符串中的\ / 替换为 /，以还原正常的URL格式。接着，将字符串编码为UTF - 8格式，
    #3.使用unicode_escape进行Unicode转义字符的解码。
    decode = urllib.parse.unquote(lock_S)
    decode = decode.replace('\/', '/')
    decode = decode.encode('utf-8').decode('unicode_escape')
    #截取题解
    begin = decode.find('"content":"')
    endword = decode.find('","type":"题解"')
    decode = decode[begin + 11:endword]
    return decode
#文件保存
def save_file(data,filename):
  file = open(filename,"w",encoding="utf-8")
  for d in data:
    file.writelines(d)
  file.close()
class GUI(ttk.Frame):
    #初始化页面
    def __init__(self, parent):
        super().__init__(parent, padding=15)
        self.columnconfigure(0, weight=1)
        self.GUI_elements()
    #GUI页面绘制
    def GUI_elements(self):
        #关键词输入框
        self.keyword_label = ttk.Label(self, text="请输入关键词：",font=('Arial', 20,'bold'))
        self.keyword_label.grid(row=0, column=0, padx=5,pady=10, sticky="w")
        self.keyword_entry = tk.Entry(self,width=50,font=('Arial', 20))
        self.keyword_entry.grid(row=1, column=0, padx=5, pady=10, sticky="ew")
        #难度选择框
        self.diff_label = ttk.Label(self, text="请选择难度：", font=('Arial', 20, 'bold'))
        self.diff_label.grid(row=2, column=0, padx=5, pady=10, sticky="w")
        diff_list = ["题目难度","全部","暂未评定", "入门", "普及-", "普及&提高-", "普及+&提高", "提高+&省选-", "省选&NOI-", "NOI&NOI+&CTSC"]
        self.combobox1 = ttk.Combobox(self,values=diff_list,font=("Arial", 20))
        self.combobox1.current(0)
        self.combobox1.grid(row=3, column=0, padx=5, pady=10, sticky="ew")
        self.combobox1.configure(font=("Arial", 20))
        #开始按钮
        style = ttk.Style()
        style.configure("Custom.TButton", font=("Arial", 20))
        self.button = ttk.Button(self, text="开始爬取", width=15,style="Custom.TButton")
        self.button.grid(row=6, column=0, padx=5, pady=10, sticky="ew")
        # 爬取情况文本框
        self.process_text = tkinter.StringVar()
        self.process_label = ttk.Label(self, textvariable=self.process_text)
        self.process_label.grid(row=7, column=0, padx=5, pady=(10, 0), sticky="w")
        self.time_text = tkinter.StringVar()
        self.time_label = ttk.Label(self, textvariable=self.time_text)
        self.time_label.grid(row=8, column=0, padx=5, pady=(10, 0), sticky="w")
        self.total_text = tkinter.StringVar()
        self.total_label = ttk.Label(self, textvariable=self.total_text)
        self.total_label.configure(font=('Arial', 20))
        self.total_label.grid(row=10, column=0, padx=5, pady=(10, 0), sticky="w")
        #实时更新绘制折线
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=11, column=0, pady=10)
        #开始爬取函数
        def click():
            self.total_text.set("总用时：秒")
            def update_graph(count_list, time_list):
                self.ax.clear()
                self.ax.plot(count_list, time_list)
                self.ax.set_xlabel("answer count")
                self.ax.set_ylabel("time (s)")
                self.ax.set_title("answer count vs time")
                self.canvas.draw()
            global keyword, difficulty
            keyword = self.keyword_entry.get()
            diff_select = self.combobox1.get()
            savePath = r"C:\Users\12979\Desktop\luogu_crawler\project\\"
            savePath = savePath + str(diff_select) + '-' + keyword
            print(savePath)
            #创建文件夹
            if not os.path.exists(savePath):
                os.mkdir(savePath)
            #获取难度
            for i in range(len(diff_list)):
                if diff_list[i] == diff_select:
                    difficulty = i - 2
                    #print(type(difficulty))
                    if difficulty <0:
                        difficulty = ''
            Url_final = ListUrl + "&difficulty=" + str(difficulty) + "&keyword=" + str(keyword) + "&type=B%7CP"
            headers = {
                "User-Agent": random_user_agent
            }
            resp = requests.get(Url_final, headers=headers)
            pattern = re.compile(r'(<a\shref=".*?">)*?') #匹配 HTML 锚标签 <a href="..."> 的起始部分
            pid = re.findall(pattern, resp.text)
            #获取题目名称与编号
            pid_list = []
            for x in pid:
                if (x != ""):
                    pid_list.append(x[9:14])#9到14位刚好就是题目id
            count = 0
            #存放时间
            time_list = []
            count_list = []
            time_per = []
            start_time = time.time()
            for i in range(len(pid_list) - 2):
                start_time_per = time.time()
                print(len(pid_list) - 2)
                #爬取15道题目
                if (count == len(pid_list) - 2 or count >= 15):
                    break
                count += 1
                #计算总时间
                end_time = time.time()
                duration = end_time - start_time
                print(duration)
                time_list.append(duration)
                count_list.append(i + 1)
                #实时更新图表
                update_graph(count_list, time_list)
                #实时更新文本
                title = "正在爬取第{}题,题目编号为".format(i + 1)+pid_list[i]
                self.process_text.set(title)
                self.process_label.configure(font=('Arial', 20))
                self.process_label.update()
                #根据pid分别获取题目内容和题解
                Problemurl = ProblemUrl + pid_list[i]
                resp = requests.get(Problemurl, headers=headers, cookies=cookie)
                ques_html = resp.text
                Solutionurl = UrlSolution + pid_list[i]
                resp = requests.get(Solutionurl, headers=headers, cookies=cookie)
                ans_html = resp.text
                #判断是否爬取成功
                if ques_html == "error":
                    print("爬取失败")
                else:
                    print("正在爬取第{}题,题目编号为".format(i + 1) + pid_list[i])
                    questionMD, ques = get_question(ques_html)
                    solutionMD = get_answer(ans_html)
                    print("爬取成功！正在保存\n", end="")
                    print(f"（用时：{duration:.2f}秒）")
                    #根据系统修改文件名中的非法字符
                    cleaned_pid = re.sub(r'[\\/:*?"<>|\[\]【】]', '-', pid_list[i])
                    cleaned_ques = re.sub(r'[\\/:*?"<>|\[\]【】]', '-', ques)
                    #题目与题解分开保存
                    folder_path = os.path.join(savePath, f"{cleaned_pid}-{cleaned_ques}")
                    if not os.path.exists(folder_path):
                        os.mkdir(folder_path)
                    problem_file_path = os.path.join(folder_path, f"{cleaned_pid}-{cleaned_ques}.md")
                    solution_file_path = os.path.join(folder_path, f"{cleaned_pid}-{cleaned_ques}-题解.md")
                    save_file(questionMD, problem_file_path)
                    save_file(solutionMD, solution_file_path)
                    print("保存成功!\n")
                    #计算每道题目的时间
                    end_time_per = time.time()
                    duration_per = end_time_per - start_time_per
                    time_per.append(duration_per)
                    title2 = "第{}题爬取成功题目编号为".format(i + 1) + pid_list[i]+ "（用时：{:.2f}秒）".format(duration_per)
                    self.time_text.set(title2)
                    self.time_label.configure(font=('Arial', 20))
                    self.time_label.update()
            self.process_text.set("爬取完毕!结果请前往" + savePath + "查看")
            self.total_text.set("总用时：{:.2f}秒".format(duration))
        self.button.config(command=click)
class Crawler(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=15)
        GUI(self).grid(row=0, column=1, rowspan=2, padx=10, pady=(10, 0), sticky="nsew")
def main():
    root = tkinter.Tk()
    root.title("洛谷爬虫")
    Crawler(root).pack(expand=True)
    root.mainloop()
if __name__ == "__main__":
    main()
