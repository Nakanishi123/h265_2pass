import sys
import os
import subprocess
import json

inputpath = sys.argv[1]
input_name = os.path.splitext(inputpath)[0]
input_ext = os.path.splitext(inputpath)[1]

output_name = input_name
output_ext = ".mkv"
outputpath = output_name+output_ext
if inputpath == outputpath:
    outputpath = output_name+"_new"+output_ext

isok = "n"
# ファイル名決める
while(1):
    print("input  : "+inputpath)
    print("output : "+outputpath)
    print("上でOK？ [y/n]")
    isok = input()
    if(isok == "y"):
        break
    else:
        outputpath = input("出力するファイル名をフルパスで入力 > ")

# ビットレートとファイルサイズを取得
x = os.path.exists(inputpath)
cmd = ["ffprobe", '-hide_banner', '-show_streams', '-of', 'json',  inputpath]
proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
info = json.loads(proc.stdout)
bitrate = int(info['streams'][0]['bit_rate'])/1000
bitrate_a = int(info['streams'][1]['bit_rate'])/1000
# ストリームの音声と動画が逆だった時に入れ替える
if info['streams'][0]['codec_type'] == "audio":
    bitrate, bitrate_a = bitrate_a, bitrate
filesize = round(os.path.getsize(inputpath)/(1024**3), 1)

# 10GBになるくらいのビットレートを計算
bitrate_osusume = int((bitrate+bitrate_a)*9.7/filesize - bitrate_a)
print(f"現在の動画のビットレート : {int(bitrate)} kb/s")
print(f"現在の音声のビットレート : {int(bitrate_a)} kb/s")
print(f"現在のファイルサイズ : {filesize} GB")
print(f"おすすめのビットレート : {bitrate_osusume} kb/s")
while(1):
    bitrate = input("ビットレート(k) >")
    if bitrate == "":
        bitrate = bitrate_osusume
    elif not bitrate.isdecimal():
        print("数字を入力してください")
        continue

    bitrate = int(bitrate)
    isok = "n"
    print(f"ビットレート :{bitrate}kb/sでよろしいですか")
    isok = input("[y/n] > ")
    if(isok == "y"):
        break

# 2pass目だけやるかどうか
start_pass = 1
print("2pass目だけやりますか [y/n]")
only2pass = input()
if(only2pass == "y"):
    print("2passだけやります")
    start_pass = 2
else:
    print("1passからやります")


# コマンド実行
for i in range(start_pass, 3):
    command = ["ffmpeg", "-i", inputpath, "-b:v", f"{bitrate}k", "-c:v", "libx265", "-c:a", "copy", "-x265-params", f"pass={i}", "-y", outputpath]
    popen = subprocess.Popen(command)
    popen.wait()
