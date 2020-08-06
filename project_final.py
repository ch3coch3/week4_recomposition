#-*-coding:utf-8 -*-

#############################################
#			  將所需函式庫加入			 #
#############################################
import requests
from bs4 import BeautifulSoup
import os
import time
from matplotlib import pyplot as plt
from matplotlib import pyplot as hold
from matplotlib.font_manager import FontProperties
from matplotlib import cm
import numpy as np

#############################################
#				讀取PTT網頁				 #
#############################################
def get_web_page(url):
	time.sleep(0.1)  
	resp = requests.get(
		url=url,
		cookies={'over18': '1'}
	)
	if resp.status_code != 200:
		print('Invalid url:', resp.url)
		return None
	else:
		return resp.text

#############################################
#		  對PTT網頁進行資料擷取			  #
#############################################
def get_data(dom):
	soup = BeautifulSoup(dom , 'html.parser')
	article = soup.find(id='main-content')
	push_tag = soup.find_all('span', 'push-tag')
	return article, push_tag

#############################################
#		  		讀取文章網址				 #
##################a##########################
def get_article_url(text):
	url = []
	month = []
	soup = BeautifulSoup(text, 'html.parser')
	divs = soup.find_all("div", "r-ent")
	for div in divs:
		try:
			href = div.find('a')['href']
			date = div.find_all('div','date')[0].get_text()
			url.append('https://www.ptt.cc' + href)
			[m,d] = date.split("/")
			month.append(eval(m))
		except:
			pass
	return [url, month]

#############################################
#		讀取看板頁面(沒有加搜尋字眼時使用)	 #
##################a##########################
def getNext(url):
	print(url)
	urls = get_web_page(url)
	soup = BeautifulSoup(urls, 'html.parser')
	div = soup.find_all('a','btn wide')
	for i in div:
		if i.getText() == '‹ 上頁':
			nextPage = 'https://www.ptt.cc' + i.get('href')
	return nextPage
############新增函式#################
#								   #
####################################
def New_function(index):
	if index == 12:
		index = 0 
		return index   		#####將判別12月以及11月的過程濃縮一個函式
	elif index == 11:
		return index
	else:
		return index

#############################################
#					畫圖					#
#############################################
def drawPicture(month,mask_month,alcohol_month,paper_month,people):
	fig = plt.figure()													#繪圖
	plt1 = fig.add_subplot()

	plt.title('防疫用品討論度與確診人數關係圖',FontProperties = myfont)
	plt.xlabel("時間(月)",FontProperties=myfont)
	plt.ylabel("次數",FontProperties=myfont)

	plt1.plot(month,mask_month,'b-o',label ="口罩")						#畫出三個防疫用品折線圖
	plt1.plot(month,alcohol_month,'g-o',label = "酒精")
	plt1.plot(month,toiletpaper_month,'k-o',label = '衛生紙')
	plt.legend(prop=myfont)

	plt2=plt1.twinx()													#畫右標

	plt2.plot(month,people,'r-o',label = '確診人數')					#畫確診人數折線圖
	plt2.set_ylabel("人數",FontProperties=myfont)						
	plt2.legend(prop=myfont,loc="upper right")							#放置圖例
	plt1.legend(prop=myfont,loc="upper left")
	plt.show()


#############################################
#		   主程式:進行資料分析			  #
#############################################
if __name__ == '__main__':
	timeStart = time.time()	# begin timecall
	Board = 'Lifeismoney'												#選取PTT看板	!!!!!!(凡是設有內容分級規定處理，即不能直接進入看板者，EX.八卦版...等會沒辦法爬)!!!!!
	URL = 'https://www.ptt.cc/bbs/' + Board + '/index.html'				#PPT網址
	datasize = 3														#輸入爬的關鍵字數目
	urls = []															#存放網址
	keyword_list = ["口罩","酒精","衛生紙"]			#存放輸入的關鍵字
	articles = []						#articles: ptt文章所有內容 
	judgeMonth = False					# judge the month
	page = 0							#從第0頁開始跑
	while True:														#取得PTT頁面資訊
		print(page)
		if page != 0:
			URL = getNext(URL)
		[urls, months] = get_article_url(get_web_page(URL))
		print(months)
        # the stop month
		if 8 in months and page != 0:								#到11月就停止
			judgeMonth = True
			print("exit loop")
	############################################################
		for i in range(len(urls)):									#將網址印出
			print(urls[i])
			text = get_web_page(urls[i])
			article, push_tag = get_data(text)
			articles.append([article,months[i]])
		page += 1													#爬下一頁
		if judgeMonth == True:										#爬到11月即跳出迴圈
			break
############################################################
	#計算關鍵字出現次數
	sum_keyword_list = []					#該關鍵字出現總數
	mask_month = [0,0,0,0,0,0,0,0,0]		# store the number of keyword refereced per month
	alcohol_month = [0,0,0,0,0,0,0,0,0]  	#刪掉四個0
	toiletpaper_month = [0,0,0,0,0,0,0,0,0]
	for i in range(datasize):														
		keyword_count = 0					#計算關鍵字出現次數
		count = 0
		for index in articles:
			keyword_count = str(index[0]).count(keyword_list[i])
			if i == 0:						#計算口罩次數
				index[1]=New_function(index[1])   	 		#####將判別12月以及11月的過程濃縮一個函式
				mask_month[index[1]] += keyword_count
			if i == 1:						#計算酒精出現次數
				index[1]=New_function(index[1])
				alcohol_month[index[1]] += keyword_count
			if i == 2:						#計算衛生紙出現次數
				index[1]=New_function(index[1])
				toiletpaper_month[index[1]] += keyword_count
			count += 1
	myfont= FontProperties(fname=r'./GenYoGothicTW-Regular.ttf')							#字型檔，r'裡面放你的字型檔案路徑'
month = ['12','1','2','3','4','5','6','7','8']				#月份LIST
people=[0,10,29,283,107,13,5,8,2]							#確診數list

# 將結果繪圖
drawPicture(month,mask_month,alcohol_month,toiletpaper_month,people)
