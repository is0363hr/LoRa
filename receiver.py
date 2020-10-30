# -*- coding: utf-8 -*-
import serial
import time
import logger
import datetime
from pytz import timezone

import pandas as pd

import sys

argc = len(sys.argv)

if argc < 3:
	print('python receiver xx(recv_point) yy(sf)')
	sys.exit(1)
else:
	# 送信拠点に対応
	recv_point = sys.argv[1]
	sf = sys.argv[2]


# データフレームのカラム
columns = ["Time","SF",'RS','RA']

ser = serial.Serial("/dev/ttyUSB0", 19200)


def init():
	ser.write(b"@GI11/W\r\n")
	ser.write(b"@DI00/W\r\n")
	ser.write(b"@EI02/W\r\n")
	ser.write(b"@SF" + sf.encode() + "/W\r\n")
	ser.write(b"@CH1B/W\r\n")
	print('--- initialized ---')


def showreceived():
	data = ser.readline()
	str = data.decode('utf-8')
	return(str)


def main():
	data = []
	init()
	count = 0
	while True:
		if ser.in_waiting:
			dt_now = datetime.datetime.now(timezone('UTC'))
			message = showreceived()
			if message.find("*DR") >= 0: # 送信機からデータを受信した時
				count += 1
				print("-------------- received data "+ str(count) +" --------------\n")
				print(message)

				# 送信元IDに対応
				id = message[8:10]
				sf = message[12:14]
				send_point = message[14:15]
				print("ID=" +str(id) + ", SF=" +str(sf) + ", point=" + str(send_point) +"\n")
				now = dt_now.strftime("%Y-%m-%d %H:%M:%S")

				#　messageからデータを抽出する
				data.append(now)
				data.append(sf)
				ser.write(b"@RS\r\n")
			if message.find("*RS") >= 0: # 送信機からデータを受信した時
				data.append(message[4:])
				ser.write(b"@RA\r\n")
			if message.find("*RA") >= 0: # 送信機からデータを受信した時
				data.append(message[4:])
				# リストをDFに変換
				df = pd.DataFrame([data], columns=columns)
				# csvに書き出す関数の呼び出し
				logger.csv_out(send_point, recv_point, df, 'recv_log')
				data = []
				print("\nwaiting....")


main()
ser.close()
# file.close()
