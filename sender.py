# -*- coding: utf-8 -*-
import serial
import time
import datetime
import pandas as pd

import logger

import sys

from pytz import timezone

argc = len(sys.argv)

if argc < 3:
	print('python sender xx(send_point) yy(SF)')
	sys.exit(1)
else:
	send_point = sys.argv[1]
	sf = sys.argv[2]


ser = serial.Serial("/dev/ttyUSB0", 19200)
MAX_LEN = 100


def init():
	ser.write(b"@GI11/W\r\n")
	ser.write(b"@EI02/W\r\n")
	ser.write(b"@DI00/W\r\n")
	ser.write(b"@SF" + sf.encode() + b"/W\r\n")
	ser.write(b"@CH1B/W\r\n")
	print('--- initialized ---')


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
	try_count = 1
	fileTxt = 'EI02SF'+ sf + send_point + str(time.strftime("%m%d%H%M"))
	print(try_count)
	sendData(fileTxt)
	columns = ["Time", 'SF']
	data = []

	while True:
		if ser.in_waiting:
			message = showreceived()
			dt_now = datetime.datetime.now(timezone('UTC'))
			if message.find("*IR=01") >= 0:
				print(message)
				sendData(fileTxt)

			elif message.find('*IR=03') >= 0:
				print('-- success_'+ str(try_count) + ':'+ fileTxt + '--')
				# データフレームのカラム
				now = dt_now.strftime("%Y-%m-%d %H:%M:%S")
				data.append(now)
				data.append(sf)
				# リストをDFに変換
				df = pd.DataFrame([data], columns=columns)
				# csvに書き出す関数の呼び出し
				logger.csv_out(send_point, '', df, 'send_log')

				data = []

				try_count += 1
				if try_count >= 30:
					break

				# sleep = (int(sf) + 1) * 3
				# print('sleep:' + str(sleep) + "\n")
				# time.sleep(sleep)


				sendData(fileTxt)


if __name__ == '__main__':
	main()
	ser.close()