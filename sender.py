# -*- coding: utf-8 -*-
import serial
import time
import datetime
import pandas as pd

import logger

import sys

argc = len(sys.argv)

if argc < 3:
	print('python sender xx(point) yy(SF)')
	sys.exit(1)
else:
	# 送信拠点に対応
	point = sys.argv[1]
	id = '02' # 機器ごとに変更必要
	sf = sys.argv[2]


ser = serial.Serial("/dev/ttyUSB0", 19200)
MAX_LEN = 100


def init():
	ser.write(b"@GI11/W\r\n")
	ser.write(b"@EI02/W\r\n")
	ser.write(b"@DI00/W\r\n")
	ser.write(b"@SF" + sf.encode() + b"/W\r\n")
	ser.write(b"@CH1B/W\r\n")


# def sf_set(sf):
# 	ser.write(b"@SF" + sf.encode() + b"/W\r\n")


def showreceived():
	data = ser.readline()
	str = data.decode('utf-8')
	return(str)


def sendData(fileTxt):
	length = len(fileTxt)
	if length >= MAX_LEN:
		print("Too much")
		return True
	hex_len = hex(length)[2:]
	tmp = "@DT" + str(hex_len) + fileTxt + "\r\n"
	ser.write(tmp.encode())
	return False



def main():
	init()
	try_count = 0
	# sf = ['00', '01', '02', '03', '04', '05']
	# fileTxt = 'EI02SF'+ sf + str(time.strftime("%m%d%H%M"))
	# sendData(fileTxt)

	data = []

	while True:
		if ser.in_waiting:
			message = showreceived()
			print(message)
			if message.find("*IR") >= 0:
				time.sleep(5)
				fileTxt = 'EI02SF'+ sf + point + str(time.strftime("%m%d%H%M"))
				print('-- SF変更 --')
				print(fileTxt)
				print('-- SF変更 --')
				sendData(fileTxt)

				if message.find('03') >= 0:
					print('-- success --')
					# データフレームのカラム
					dt_now = str(datetime.datetime.now())
					columns = ["Time"]
					data.append(dt_now)
					# リストをDFに変換
					df = pd.DataFrame([data], columns=columns)
					# csvに書き出す関数の呼び出し
					logger.csv_out(point, id, df, 'send_')

					data = []
					try_count += 1

					sleep = (int(sf) + 1) * 5
					print('sleep:' + str(sleep))


			if try_count >= 3:
				break


if __name__ == '__main__':
	main()
	ser.close()