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
#############################################
#		   主程式:進行資料分析			  #
#############################################
if __name__ == '__main__':
	tStart = time.time()	# begin timecal

	KEY = 1																#有沒有加入搜尋字眼 1:有 0:沒有
	Board = 'Lifeismoney'												#選取PTT看板	!!!!!!(凡是設有內容分級規定處理，即不能直接進入看板者，EX.八卦版...等會沒辦法爬)!!!!!
	URL = 'https://www.ptt.cc/bbs/' + Board + '/index.html'

	datazise = 3
	urls = []
	semantic_list = ["口罩","酒精","衛生紙"]			#存放輸入的關鍵字
	articles = []						#articles: ptt文章所有內容 
	judgeMonth = False					# judge the month
	page = 0
	while True:														#取得PTT頁面資訊
		print(page)
		if page != 0:
			URL = getNext(URL)
		[urls, months] = get_article_url(get_web_page(URL))
		print(months)
        # the stop month
		if 11 in months and page != 0:
			judgeMonth = True
			print("exit loop")
	############################################################
		for i in range(len(urls)):
			print(urls[i])
			text = get_web_page(urls[i])
			article, push_tag = get_data(text)
			articles.append([article,months[i]])
		page += 1
		if judgeMonth == True:
			break
	############################################################
	#計算關鍵字出現次數
	sum_sem_list = []			#該關鍵字出現總數
	mask_month = [0,0,0,0,0,0,0,0]		# store the number of keyword refereced per month
	alcohol_month = [0,0,0,0,0,0,0,0]  #####刪掉四個0
	paper_month = [0,0,0,0,0,0,0,0]
	for i in range(datazise):														
		sem_count = 0
		count = 0
		for index in articles:
			sem_count = str(index[0]).count(semantic_list[i])
			if i == 0:
				if index[1] == 12:
					index[1] = 0
				elif index[1] == 11:
					continue
				mask_month[index[1]] += sem_count
			if i == 1:
				if index[1] == 12:
					index[1] = 0
				elif index[1] == 11:
					continue
				alcohol_month[index[1]] += sem_count
			if i == 2:
				if index[1] == 12:
					index[1] = 0
				elif index[1] == 11:
					continue
				paper_month[index[1]] += sem_count
			count += 1
		# print(mask_month)
		# print(alcohol_month)
		# print(paper_month)

	#######################################
	#				將結果繪圖			  #
	#######################################
	myfont= FontProperties(fname=r'./GenYoGothicTW-Regular.ttf')							#字型檔，r'裡面放你的字型檔案路徑'
	
month = ['12','1','2','3','4','5','6','7']
people=[0,10,29,283,107,13,5,8]

fig = plt.figure()

plt1 = fig.add_subplot()

plt.title('防疫用品討論度與確診人數關係圖',FontProperties = myfont)
plt.xlabel("時間(月)",FontProperties=myfont)
plt.ylabel("次數",FontProperties=myfont)

plt1.plot(month,mask_month,'b-o',label ="口罩")
plt1.plot(month,alcohol_month,'g-o',label = "酒精")
plt1.plot(month,paper_month,'k-o',label = '衛生紙')
plt.legend(prop=myfont)

plt2=plt1.twinx()

plt2.plot(month,people,'r-o',label = '確診人數')
plt2.set_ylabel("人數",FontProperties=myfont)

plt2.legend(prop=myfont,loc="upper right")
plt1.legend(prop=myfont,loc="upper left")
plt.show()
