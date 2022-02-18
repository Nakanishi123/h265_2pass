import sys
import os
import subprocess
import re
import time

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
information = subprocess.Popen(
    ["ffprobe",  inputpath], stderr=subprocess.PIPE)
time.sleep(1)

for i in information.stderr:
    inf = re.search(r"Duration:\s+(.+),\s.+bitrate:\s+(\d+)", str(i))
    if inf != None:
        length = inf.groups()[0]
        bitrate = inf.groups()[1]
        filesize = os.path.getsize(inputpath)/(1024**3)
        filesize = round(filesize,1)
        break

# 10GBになるくらいのビットレートを計算
bitrate_osusume = int(int(bitrate) * 9.6 / filesize)
print(f"現在のビットレート : {bitrate} kb/s")
print(f"現在のファイルサイズ : {filesize}GB")
print(f"おすすめのビットレート : {bitrate_osusume}")
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

# コマンド実行
for i in range(1, 3):
    command = ["ffmpeg", "-i", inputpath, "-b:v",f"{bitrate}k","-c:v","libx265", "-c:a", "copy", "-x265-params", f"pass={i}", "-y", outputpath]
    popen=subprocess.Popen(command)
    popen.wait()
