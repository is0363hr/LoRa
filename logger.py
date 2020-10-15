# -*- coding: utf-8 -*-
# import sys
import os


import datetime
import pandas as pd


def csv_out(point, id, df, dir):   # point:拠点, id:機器ID, df:データ
    
    time = pd.to_datetime(df['time'][0])

    dir_name = '/home/pi/lora/' + dir + 'log/'
    folder_name = point

    # フォルダの存在確認
    if not os.path.exists(dir_name + folder_name):
        os.mkdir(dir_name + folder_name)

    # ファイル名を作成(機器IDと時間の組み合わせ)
    file_name = "EI" + str(id) + "_" + time.strftime("%Y-%m-%d_%H") + '.csv'
    
    #ファイルのパスを作成
    file_path = dir_name + folder_name + '/' + file_name
    
    # csvファイルがあったら追記/それ以外は新規作成
    if os.path.exists(file_path):
        df.to_csv(file_path, mode='a', header=False, index=False)
    else:
        df.to_csv(file_path, index=False)

    return

