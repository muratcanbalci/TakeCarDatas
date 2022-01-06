# -*- coding: utf-8 -*-
"""
Created on Sat Mar 20 02:16:56 2021

@author: Murat Can BALCI
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

global sayi
global aracLinkleri
global carDatas
global fiyatDatas

def kayitCek():
    r = requests.get("https://www.arabam.com/ikinci-el/otomobil/audi")
    r.status_code
    soup = BeautifulSoup(r.content,"lxml")
    kayitlar = soup.find_all("div",attrs={"class":"selected-filters-wrapper"})
    
    for kayit in kayitlar:
        sayi = kayit.find("span",attrs={"class":"color-red4 bold pl4 fz13"}).text.strip()   
    return sayi

def verileriCek():
    try:
        s1 = kayitCek()
        s1=s1.replace('.','')
        s1 = int(s1[1:len(s1)-6])
        if(s1 > 30 or s1 == 30):        
            sayfasayisi = round(s1 / 20)
        elif(s1 > 20 and s1 < 30):
            sayfasayisi = 2
        elif(s1 < 0 or s1 == 0):
            sayfasayisi = 0
        else:
            sayfasayisi = 1
        
        aracLinkleri = list()
        carDatas = list()
        fiyatDatas = list()
        baslikListesi = list()
        degerListesi = list()
        yenidegerListesi=list()
        fiyatListesi = list()
        while(sayfasayisi > 0):
            r2 = requests.get("https://www.arabam.com/ikinci-el/otomobil/audi?page={}".format(sayfasayisi))
            r2.status_code
            soup = BeautifulSoup(r2.content,"lxml")
            arabakayit = soup.find_all("td",attrs={"class":"listing-modelname pr"})
            for link in arabakayit:
                for a in link.find_all('a',href=True,text=True):
                    aracLinkleri.append(a['href'])
            sayfasayisi = sayfasayisi - 1
        #Arabaların tek tek linklerini alıyoruz bir listeye atıyoruz. Daha sonra her bir linke girip
        #Oradaki verileri alıp bir dataframe'e atacağız.
                   
        if(len(aracLinkleri) > 50):
            aracLinkSayisi = 50
        else:
            aracLinkSayisi = len(aracLinkleri)

        for j in range(aracLinkSayisi):
            url = "https://www.arabam.com{}".format(aracLinkleri[j])
            rInfo = requests.get(url)
            rInfo.status_code
            infoSoup = BeautifulSoup(rInfo.content,"lxml")
            
            veriler = infoSoup.find_all("div",attrs={"class":"banner-column-detail bcd-mid-extended p10 bg-white"})
            for veri in veriler:
                yeniveriler = veri.find_all("li",attrs={"class":"bcd-list-item"})
                fiyatverileri = veri.find_all("div",attrs={"class":"mb8"})
                if(len(yeniveriler) == 16):
                    for element in yeniveriler:
                        for deger in element.find_all("span"):
                            if(deger.text.strip() != "Boya-değişen:" and deger.text.strip() != "Belirtilmemiş"):           
                                carDatas.append(deger.text.strip())
                    for fiyatelement in fiyatverileri:
                        for fiyatlar in fiyatelement.find_all("span"):
                            fiyatDatas.append(fiyatlar.text.strip())
  
        for baslik in carDatas:
            baslikListesi.append(carDatas[::2])
            degerListesi.append(carDatas[1::2])
        del carDatas
        for index,fsay in enumerate(fiyatDatas,start=0):
            fiyatListesi.append(fiyatDatas[index][:-3].replace('.',""))
        del fiyatDatas
        fiyatDf = pd.DataFrame(fiyatListesi,columns=["Fiyat"])
        
        del yeniveriler,veriler,s1,rInfo,r2,j,aracLinkleri,arabakayit,sayfasayisi,aracLinkSayisi,baslik,index,fsay    
        baslikListesi = np.array(baslikListesi)
        degerListesi = np.array(degerListesi[0])
        uzunluk = round(int(len(degerListesi) / 15))
        degerListesi = degerListesi.reshape(uzunluk,15)
        
        for degerler in degerListesi:
            yenidegerListesi.append(degerler[0:15])
        bilgilerDF = pd.DataFrame(yenidegerListesi,columns=baslikListesi[0][0:15])
        allDataFrame=pd.DataFrame()
        allDataFrame=pd.concat([bilgilerDF,fiyatDf],axis=1)
        allDataFrame.to_excel("audi.xlsx")
        del yenidegerListesi,baslikListesi,degerListesi,degerler,url,uzunluk,bilgilerDF,allDataFrame,fiyatDf,fiyatListesi,fiyatverileri

    except:
        print("Veri Çekilemedi")
