import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import subprocess
import sys
import os
import requests
import re
import json
import threading

# 日志记录函数
def log_message(message):
    log_text.config(state=tk.NORMAL)  # 解锁文本框以写入内容
    log_text.insert(tk.END, message + "\n")  # 在文本框中插入日志
    log_text.config(state=tk.DISABLED)  # 锁定文本框以防止用户编辑
    log_text.see(tk.END)  # 始终滚动到最后一行

# 自动安装所需库的函数
def install_required_packages():
    required_packages = ['requests']
    for package in required_packages:
        try:
            __import__(package)
            # 如果库已安装，提示用户是否要重新安装
            if messagebox.askyesno("安装库", f"库 {package} 已安装，是否重新安装？"):
                try:
                    log_message(f"正在重新安装 {package}...")
                    # 安装所需库
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', package])
                    log_message(f"{package} 重新安装完成！")
                except Exception as e:
                    messagebox.showerror("错误", f"重新安装 {package} 失败: {e}")
        except ImportError:
            if messagebox.askyesno("安装库", f"缺少库 {package}，是否安装？"):
                try:
                    log_message(f"正在安装 {package}...")
                    # 安装所需库
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                    log_message(f"{package} 安装完成！")
                except Exception as e:
                    messagebox.showerror("错误", f"安装 {package} 失败: {e}")

# 下载和合并处理
def download_and_merge(url, headers, save_path):
    title = download_video_and_audio(url, headers, save_path)
    if title:
        merge_video(title, save_path)

def download_video_and_audio(url, headers, save_path):
    try:
        response = requests.get(url=url, headers=headers)
        response.raise_for_status()
        html = response.text

        title = re.findall('title="(.*?)"', html)[0]
        log_message(f"视频标题: {title}")

        info = re.findall('window.__playinfo__=(.*?)</script>', html)[0]
        json_data = json.loads(info)

        video_url = json_data['data']['dash']['video'][0]['baseUrl']
        audio_url = json_data['data']['dash']['audio'][0]['baseUrl']
        
        video_content = requests.get(url=video_url, headers=headers).content
        audio_content = requests.get(url=audio_url, headers=headers).content
        
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        with open(os.path.join(save_path, f'{title}.mp4'), mode='wb') as v:
            v.write(video_content)
        with open(os.path.join(save_path, f'{title}.mp3'), mode='wb') as a:
            a.write(audio_content)

        log_message("视频和音频下载完成！")
        return title

    except Exception as e:
        messagebox.showerror("错误", f"发生错误: {e}")

# 合并视频的函数
def merge_video(title, save_path):
    log_message("开始合并视频...")
    if not os.path.exists('finally_video'):
        os.makedirs('finally_video')
    
    cmd = f'ffmpeg -hide_banner -i "{save_path}\\{title}.mp4" -i "{save_path}\\{title}.mp3" -c:v copy -c:a aac -strict experimental "{save_path}\\{title}output.mp4"'
    
    subprocess.run(cmd)
    log_message(f"{title} 合并完成！")

def start_download():
    url = url_entry.get()
    cookie = cookie_entry.get()
    save_path = path_entry.get()

    headers = {
        "Referer": url,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
        "Cookie": cookie
    }

    # 使用线程处理下载和合并
    threading.Thread(target=download_and_merge, args=(url, headers, save_path)).start()

def choose_directory():
    folder_selected = filedialog.askdirectory()
    path_entry.delete(0, tk.END)
    path_entry.insert(0, folder_selected)

# 创建主窗口
root = tk.Tk()
root.title("视频下载器")

# 输入视频链接
url_label = tk.Label(root, text="请输入视频链接:")
url_label.pack()

url_entry = tk.Entry(root, width=50)
url_entry.pack()

# 输入 cookie
cookie_label = tk.Label(root, text="请输入 Cookie:")
cookie_label.pack()

cookie_entry = tk.Entry(root, width=50)
cookie_entry.pack()

# 输入保存路径
path_label = tk.Label(root, text="请选择保存路径:")
path_label.pack()

path_entry = tk.Entry(root, width=50)
path_entry.pack()

# 选择保存路径按钮
choose_button = tk.Button(root, text="选择保存路径", command=choose_directory)
choose_button.pack()

# 开始下载按钮
start_button = tk.Button(root, text="开始下载", command=start_download)
start_button.pack()

# 创建日志文本框
log_frame = tk.Frame(root)
log_frame.pack(pady=10)

log_text = tk.Text(log_frame, height=10, width=60)
log_text.pack(side=tk.LEFT)

log_scrollbar = tk.Scrollbar(log_frame, command=log_text.yview)
log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

log_text.config(yscrollcommand=log_scrollbar.set)
log_text.config(state=tk.DISABLED)

# 签名标注
signature_label = tk.Label(root, text="© 2024 曙光工作室|幻影蓝狐", font=("Arial", 10))
signature_label.place(relx=1.0, rely=1.0, anchor='se')  # 右下角对齐

# 自动安装所需库
install_required_packages()

# 运行主窗口的事件循环
root.mainloop()
