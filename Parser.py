import json
import requests
from bs4 import BeautifulSoup as bs
import lxml
import os
import sys
from time import time, sleep
from fake_useragent import UserAgent
import re
import openpyxl
import time
i = 0
class Parser:

	def getItems(url,s,headers):
		global i
		#Переменные

		code = None
		name = None
		edIzm = None
		prices = []
		sizeOpt = None
		optDiscount = None
		distripDscount = None
		sklad = None
		timeSend = None
		Charectes = None
		Complects = None
		Logistick = None
		Marker = None
		Instruct = None
		description = None
		Declaracion = None
		Photos = None
		goodURL = url
		if url.find('https://') == 0:
			return(False)
		else:
			print(f'Открываю: https://www.ssd.ru{url}')
			goodURL = f'https://www.ssd.ru{url}'
		while True:
			try:
				page = s.get(goodURL,headers=headers)
				break
			except Exception as ex:
				print(f'Произошла ошибка: {ex}\n Жду 60 секунд и продолжаю')
				time.sleep(60)
		soup = bs(page.text, 'lxml')
		code = soup.find('span',{'class':'copy-to-buffer'})
		code = code.find('strong').text
		status = soup.find('div',{'class':'widget__title'}).text
		name = soup.find('h1',{'class':'page-title'}).get('content')
		#Работа с 1 блоком информации
		BlockInfo1 = soup.find('div',{'class':'wrapper-for-tips'})
		col_5_Block1 = BlockInfo1.findAll('div',{'class':'col_5'})
		if len(col_5_Block1) == 1:
			print('Товар под заказ')
			findBlock2 = False
			Block2 = soup.findAll('div',{'class':'widget widget_mod no-fix-height'})
			for block in Block2:
				if block.find('div',{'class':'widget__title'}) != None:
					if block.find('div',{'class':'widget__title'}).text == 'Параметры товара':
						Block2 = block
						findBlock2 = True
						break
			#Сбор возможных данных
			if findBlock2 == True:

				#AllParametrs = Block2.findAll('div',{'class':'accord__title js-accord-toggle'})
				AllParametrs = Block2.findAll('div',{'class':'accord accord_small js-accord is-open'})
				
				for blockMain in AllParametrs:
					param = blockMain.find('div',{'class':'accord__title js-accord-toggle'})
					if param.text =='Характеристики':
						Charectes = []
						block = Block2.findAll('div',{'class':'tab-characteristics'})[0]
						trs = block.findAll('tr')
						for tr in trs:
							tr = re.sub(" +", " ", tr.text).replace('\n','').replace('\r','')
							Charectes.append(tr)
					if param.text =='Комплектация':
						Complects = []
						block = Block2.findAll('div',{'class':'tab-complectation'})[0]
						trs = block.findAll('tr')
						for tr in trs:
							tr = re.sub(" +", " ", tr.text).replace('\n','').replace('\r','')
							Complects.append(tr)
					if param.text =='Логистические параметры':
						Logistick = []
						block = Block2.findAll('div',{'class':'tab-logistic'})[0]
						trs = block.findAll('tr')
						for tr in trs:
							tr = re.sub(" +", " ", tr.text).replace('\n','').replace('\r','')
							Logistick.append(tr)
					if param.text =='Маркировка':
						Marker = []
						block = blockMain.find('div',{'class':'accord__body js-accord-list'})
						trs = block.findAll('tr')
						for tr in trs:
							tr = re.sub(" +", " ", tr.text).replace('\n','').replace('\r','')
							Marker.append(tr)

				AllParametrs = Block2.findAll('div',{'class':'accord accord_small js-accord'})
				for blockMain in AllParametrs:
					param = blockMain.find('div',{'class':'accord__title js-accord-toggle'})
					if param.text =='Инструкции':
						Instruct = []
						block = blockMain.findAll('a',{'class':'file-item'})
						for href in block:
							href = href.get('href')
							Instruct.append(f'https://www.ssd.ru{href}')
					if param.text =='Декларации':
						Declaracion = []
						block = blockMain.findAll('a',{'class':'file-item'})
						for href in block:
							href = href.get('href')
							Declaracion.append(f'https://www.ssd.ru{href}')

				ArticleBlock = soup.findAll('div',{'class':'article'})[0]
				if soup.find('div',{'itemprop':'description'}) != None:
					ArticleBlock = soup.find('div',{'itemprop':'description'}).text
					Article = ArticleBlock.replace('Перейти к сопутствующим товарам', '')	
					Article = re.sub(" +", " ", Article).replace('\n','')
					description = Article 
				else:
					description = None

				
				MainBlockPhoto = soup.findAll('div',{'class':'swiper-container'})
				if len(MainBlockPhoto) > 0:
					PhotosBlock = MainBlockPhoto[1].findAll('img',{'class':'swiper-lazy'})
					if len(PhotosBlock) > 0:
						Photos = []
						for PhotosB in PhotosBlock:
							PhotosB = PhotosB.get('src')
							if PhotosB.find('https://') == -1:
								Photos.append(f'https://www.ssd.ru{PhotosB}')
		elif len(col_5_Block1) == 2:
			edIzm = soup.find('div',{'class':'unit-value'}).text
			edIzm = re.sub(" +", " ", edIzm).replace('\n','').replace('\r','')
			col_5_Block1 = col_5_Block1[1]

			#Получение цен
			price_cells = soup.findAll('td',{'class':'price-cell'})
			for price in price_cells:
				if price.find('span') == None:
					continue
				else:
					prices.append(price.find('span').text)
			if len(prices) == 0:
				prices = None

			#Получение кол-во опта / скидка опта
			widget_price_body = col_5_Block1.find('div',{'class':'widget_price_body'})
			table = widget_price_body.findAll('table',{'class':'price-table-content'})[1]

			allTr = table.findAll('tr')
			if len(allTr) > 1:
				tr1 = allTr[0]
				td1 = tr1.findAll('td')[0].text
				if td1.find('опт') != -1:
					td2 = tr1.findAll('td')[1].text
					td2 = re.sub(" +", " ", td2).replace('\n','')
					sizeOpt = td2

				tr2 = allTr[1]
				td1 = tr2.findAll('td')[0].text
				if td1.find('скидка') != -1:
					optDiscount = tr2.findAll('td')[1].find('span').text

			#Дистрибьюторская скидка
			table = widget_price_body.findAll('table',{'class':'price-table-content'})
			if len(table) > 3:
				table = widget_price_body.findAll('table',{'class':'price-table-content'})[3]
				if table.find('span') != None:
					distripDscount = table.find('span').text
			#-----------------------------------------------
			
			AllParametrs = col_5_Block1.findAll('div',{'class':'accord__title js-accord-toggle'})
			#Сбор возможных данных
			for param in AllParametrs:
				if param.text =='Наличие':
					sklad = []
					table = col_5_Block1.findAll('table',{'class':'price-table-content full-info__trigger'})
					for tab in table:
						trs = tab.findAll('tr')
						for tr in trs:
							sklads = re.sub(" +", " ", tr.text).replace('\n','').replace('\r','')
							sklad.append(sklads)
				if param.text == 'Прогнозируемый срок поставки':
					timeSend = None
					table = col_5_Block1.findAll('div',{'class':'tabs-cont js-tabs-cont tab-params tab-characteristics'})
					for tab in table:
						if tab.find('div',{'class':'avr-post-block'}) != None:
							timeSend = tab.find('div',{'class':'avr-post-block'}).text
							timeSend = re.sub(" +", " ", timeSend).replace('\n','').replace('\r','')[1:]
			#-----------------------------------------------

			#Работа со 2 блоком информации
			findBlock2 = False
			Block2 = soup.findAll('div',{'class':'widget widget_mod no-fix-height'})
			for block in Block2:
				if block.find('div',{'class':'widget__title'}) != None:
					if block.find('div',{'class':'widget__title'}).text == 'Параметры товара':
						Block2 = block
						findBlock2 = True
						break
			#Сбор возможных данных
			if findBlock2 == True:

				#AllParametrs = Block2.findAll('div',{'class':'accord__title js-accord-toggle'})
				AllParametrs = Block2.findAll('div',{'class':'accord accord_small js-accord is-open'})
				
				for blockMain in AllParametrs:
					param = blockMain.find('div',{'class':'accord__title js-accord-toggle'})
					if param.text =='Характеристики':
						Charectes = []
						block = Block2.findAll('div',{'class':'tab-characteristics'})[0]
						trs = block.findAll('tr')
						for tr in trs:
							tr = re.sub(" +", " ", tr.text).replace('\n','').replace('\r','')
							Charectes.append(tr)
					if param.text =='Комплектация':
						Complects = []
						block = Block2.findAll('div',{'class':'tab-complectation'})[0]
						trs = block.findAll('tr')
						for tr in trs:
							tr = re.sub(" +", " ", tr.text).replace('\n','').replace('\r','')
							Complects.append(tr)
					if param.text =='Логистические параметры':
						Logistick = []
						block = Block2.findAll('div',{'class':'tab-logistic'})[0]
						trs = block.findAll('tr')
						for tr in trs:
							tr = re.sub(" +", " ", tr.text).replace('\n','').replace('\r','')
							Logistick.append(tr)
					if param.text =='Маркировка':
						Marker = []
						block = blockMain.find('div',{'class':'accord__body js-accord-list'})
						trs = block.findAll('tr')
						for tr in trs:
							tr = re.sub(" +", " ", tr.text).replace('\n','').replace('\r','')
							Marker.append(tr)

				AllParametrs = Block2.findAll('div',{'class':'accord accord_small js-accord'})
				for blockMain in AllParametrs:
					param = blockMain.find('div',{'class':'accord__title js-accord-toggle'})
					if param.text =='Инструкции':
						Instruct = []
						block = blockMain.findAll('a',{'class':'file-item'})
						for href in block:
							href = href.get('href')
							Instruct.append(f'https://www.ssd.ru{href}')
					if param.text =='Декларации':
						Declaracion = []
						block = blockMain.findAll('a',{'class':'file-item'})
						for href in block:
							href = href.get('href')
							Declaracion.append(f'https://www.ssd.ru{href}')

				ArticleBlock = soup.findAll('div',{'class':'article'})[0]
				if soup.find('div',{'itemprop':'description'}) != None:
					ArticleBlock = soup.find('div',{'itemprop':'description'}).text
					Article = ArticleBlock.replace('Перейти к сопутствующим товарам', '')	
					Article = re.sub(" +", " ", Article).replace('\n','')
					description = Article 
				else:
					description = None

				
				MainBlockPhoto = soup.findAll('div',{'class':'swiper-container'})
				if len(MainBlockPhoto) > 0:
					PhotosBlock = MainBlockPhoto[1].findAll('img',{'class':'swiper-lazy'})
					if len(PhotosBlock) > 0:
						Photos = []
						for PhotosB in PhotosBlock:
							PhotosB = PhotosB.get('src')
							if PhotosB.find('https://') == -1:
								Photos.append(f'https://www.ssd.ru{PhotosB}')


		#print(f'Price: {prices}\ncountOpt: {sizeOpt}\nDiscountOpt: {optDiscount}\nDiscountDis: {distripDscount}\nSklad: {sklad}\ntimeSend: {timeSend}\nCharectes: {Charectes}\nComplects: {Complects}\nLogistick: {Logistick}\nMarker: {Marker}\nInstruct: {Instruct}\ndescription: {description}\nDeclaracion: {Declaracion}\nPhotos: {Photos}')
		# i += 1
		# if i == 5:
		# 	sys.exit()
		else:
			print(f'col_5 Больше 2 страница: https://www.ssd.ru{url}')
		item = [code,name,edIzm,prices,sizeOpt,optDiscount,distripDscount,sklad,timeSend,Charectes,Complects,Logistick,Marker,Instruct,description,Declaracion,Photos]
		return(item)
		

