import sys
import os
import subprocess
import json
import tkinter as tk
from tkinter import ttk

inputpath = sys.argv[1]
outputpath = os.path.splitext(inputpath)[0]+".mkv"
if inputpath == outputpath:
    outputpath = os.path.splitext(inputpath)[0]+"_NEW"+".mkv"


def get_movie_info(path: str) -> dict:
    if os.path.exists(path):
        cmd = ["ffprobe", '-hide_banner', '-show_streams', '-of', 'json',  inputpath]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        return json.loads(proc.stdout)
    else:
        raise "ファイルが存在していません"


def get_bitrate(path: str) -> tuple[int, int, float]:
    info = get_movie_info(path)

    try:
        video_bitrate = float(info['streams'][0]['bit_rate'])/1000
    except:
        raise Exception("動画のビットレートがわからなかった 前々からあるけどよくわからん")

    try:
        audio_bitrate = float(info['streams'][1]['bit_rate'])/1000
    except:
        raise Exception("音声のビットレートがわからなかった 前々からあるけどよくわからん")

    if info['streams'][0]['codec_type'] == "audio":
        video_bitrate, audio_bitrate = audio_bitrate, video_bitrate

    total = video_bitrate+audio_bitrate
    return int(video_bitrate), int(audio_bitrate), total


# ビットレートとファイルサイズを取得
bitrate, bitrate_a, bitrate_total = get_bitrate(inputpath)
filesize = round(os.path.getsize(inputpath)/(1024**3), 1)

# 10GBになるくらいのビットレートを計算
bitrate_osusume = int((bitrate+bitrate_a)*9.9/filesize - bitrate_a)
bitrate_a = int(bitrate_a)


# GUI
root = tk.Tk()
root.geometry()
root.title('2passエンコ')

# 変数
bitrate_var = tk.IntVar()
bitrate_a_var = tk.IntVar()
presize = tk.StringVar()
presize.set("予想サイズ : "+str(round((bitrate_a+bitrate_osusume)*filesize/bitrate_total, 4))+" GB")


input_f = tk.Frame()
inputlabel = ttk.Label(input_f, text=f"入力元：{inputpath}")
inputlabel.pack(side=tk.LEFT)
input_f.pack(fill=tk.X, padx=(10, 50), pady=5)

output_f = tk.Frame()
outputlabel = ttk.Label(output_f, text=f"出力先：")
output_path = ttk.Entry(output_f)
output_path.insert(0, f"{outputpath}")
outputlabel.pack(side=tk.LEFT)
output_path.pack(fill=tk.X)
output_f.pack(fill=tk.X, padx=10, pady=5)

ba_f = tk.Frame()
ba_label = ttk.Label(ba_f, text=f"音声のビットレート(k)")
ba = ttk.Spinbox(ba_f, from_=0, to=100000, increment=1, textvariable=bitrate_a_var)
ba.delete(0, 1)
ba.set(bitrate_a)
ba_label.pack(side=tk.LEFT)
ba.pack(side=tk.LEFT)
# 音声コーデック選択肢
bc_label = ttk.Label(ba_f, text=f"音声のコーデック")
bc_combobox = ttk.Combobox(ba_f, values=["copy", "libopus", "aac", "libmp3lame"])
bc_combobox.set("copy")
bc_label.pack(side=tk.LEFT)
bc_combobox.pack(side=tk.LEFT)
# 元のサイズ
ba_motomoto = ttk.Label(ba_f, text=f"元々 : {bitrate_a}k")
ba_motomoto.pack()
ba_f.pack(fill=tk.X, padx=10, pady=5)

# 映像の設定
bv_f = tk.Frame()
bv_label = ttk.Label(bv_f, text=f"映像のビットレート(k)")
bv = ttk.Spinbox(bv_f, from_=0, to=10000000, increment=1, textvariable=bitrate_var)
bv.delete(0, 1)
bv.insert(0, bitrate_osusume)
bv_label.pack(side=tk.LEFT)
bv.pack(side=tk.LEFT)
bv_f.pack(fill=tk.X, padx=10, pady=5)


def defdo_2pass() -> None:
    if do_2pass_only.get:
        do_2pass_only.set(False)


def defdo_2pass_only() -> None:
    if do_2pass.get:
        do_2pass.set(False)


do_2pass_only = tk.BooleanVar()
do_2pass_only.set(False)
do_2pass_only_f = ttk.Frame()
do_2pass_only_chk = ttk.Checkbutton(do_2pass_only_f, command=defdo_2pass_only, variable=do_2pass_only, text="2passの2回目のみやる(1回目のログが残っている)")
do_2pass_only_chk.pack(side=tk.LEFT)
do_2pass_only_f.pack(fill=tk.X, padx=10, pady=5)

do_2pass = tk.BooleanVar()
do_2pass.set(False)
do_2pass_f = ttk.Frame()
do_2pass_chk = ttk.Checkbutton(do_2pass_f, command=defdo_2pass, variable=do_2pass, text="2passをしない(1回だけで終わる)")
do_2pass_chk.pack(side=tk.LEFT)
do_2pass_f.pack(fill=tk.X, padx=10, pady=5)

another_command = tk.BooleanVar()
another_command.set(False)
another_command_f = tk.Frame()
another_command_chk = ttk.Checkbutton(another_command_f,  variable=another_command, text="他のコマンドを使う")
another_command_cmd = ttk.Entry(another_command_f)
another_command_cmd.insert(0, "")
another_command_chk.pack(side=tk.LEFT)
another_command_cmd.pack(fill=tk.X)
another_command_f.pack(fill=tk.X, padx=10, pady=5)

# 予想サイズ


def update_presize(*args):
    presize.set("予想サイズ : "+str(round((float(ba.get())+float(bv.get()))*filesize/bitrate_total, 4))+" GB")


size_info = ttk.Label(root,  textvariable=presize, font=("メイリオ", "15", "normal"))
size_info.pack()
bitrate_a_var.trace('w', update_presize)
bitrate_var.trace('w', update_presize)


def do_ffmpeg():
    cmd = ["ffmpeg", "-i", inputpath, "-c:v", "libx265"]

    # 他のコマンドを使うとき
    if another_command.get():
        cmd += another_command_cmd.get().split()

    # 映像の設定
    cmd += ["-b:v", f"{int(bv.get())}k"]

    # オーディオの設定
    if bitrate_a == int(ba.get()):
        cmd += ["-c:a", "copy"]
    else:
        cmd += ["-c:a", f"{bc_combobox.get()}", "-b:a", f"{int(ba.get())}k"]

    if not do_2pass.get():  # 2passをやる場合
        start_pass = 1
        # 2passの2回目だけをやる場合
        if do_2pass_only.get():
            start_pass = 2

        for i in range(start_pass, 3):
            popen = subprocess.Popen(cmd+["-x265-params", f"pass={i}", "-y", output_path.get()])
            popen.wait()
    else:  # 2passsをしない場合
        popen = subprocess.Popen(cmd+["-y", output_path.get()])
        popen.wait()


button = ttk.Button(root, text="スタート", command=do_ffmpeg)
button.pack()

root.mainloop()
