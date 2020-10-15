# -*- coding: utf-8 -*-
import serial
import time
import logger
import datetime
import pandas as pd

import sys

argc = len(sys.argv)

if argc < 2:
	print('python ste_receiver xx(sf)')
	sys.exit(1)
else:
	# 送信拠点に対応
	sf = sys.argv[1]


# データフレームのカラム
columns = ["Time","SF",'RS','RA']

ser = serial.Serial("/dev/ttyUSB0", 19200)
# file = open("LoRa_output.txt", 'w')


def init():
	ser.write(b"@GI11/W\r\n")
	ser.write(b"@DI00/W\r\n")
	ser.write(b"@EI02/W\r\n")
	ser.write(b"@SF" + sf.encode() + "/W\r\n")
	ser.write(b"@CH1B/W\r\n")


def data_time(message):
	dt_now = datetime.datetime.now()  # 受信した時刻
	print(dt_now)
	print("")
	# data.append(str(dt_now))
	# print(data)
	return str(dt_now)

def showreceived():
	data = ser.readline()
	str = data.decode('utf-8')
	return(str)

def writeToFile(message):
	file.write(str(message))
	file.write("\n")


def main():
	data = []
	init()
	count = 0
	while True:
		if ser.in_waiting:
			message = showreceived()
			print(message)
			# writeToFile(message)
			if message.find("*DR") >= 0: # 送信機からデータを受信した時
				count += 1
				print("-------------- received data "+ str(count) +" --------------\n")


				# 送信元IDに対応
				id = message[8:10]
				sf = message[12:14]
				point = message[14:15]
				print("ID=" +str(id) + ", SF=" +str(sf) + ", point=" + str(point) +"\n")
				dt_now = datetime.datetime.now()
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
				logger.csv_out(point, id, df, 'receive_')
				data = []
				print("\nwaiting....")


main()
ser.close()
# file.close()
