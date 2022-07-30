#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
from urllib.request import urlopen as uReq
import requests
from bs4 import BeautifulSoup 
import json
from difflib import SequenceMatcher
from selenium import webdriver
import time
from datetime import date
#regex para pegar Ano do STRING do nome dos veiculos
import re
import openpyxl
from openpyxl.styles import Color, PatternFill, Font, Border

from selenium import webdriver

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import winsound


# In[24]:


listaJson = []
options = Options()
#options.headless = True
options.add_argument("--disable-notifications")
options.add_argument("--mute-audio")
driver = webdriver.Firefox(options=options, executable_path = 'C:\python-geckodriver\geckodriver.exe')


# In[21]:


def definirParams(auth: "", path: "", referer: ""):
    PARAMS = {
            "authority": auth,
            "method": "GET",
            "path":path,
            "scheme": "https",
            "referer": referer,
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
            }
    return PARAMS

def criarJson(dataPostagem, titulo, preco, url, regiao, regiaoCidade, resumo):
    print("titulo: " + str(titulo))
    print("Preco: " + str(preco))
    print(regiao)
    print(url)
    print(resumo)
    print("----")
        
    json = { 
    "preco": preco,
    "titulo": titulo,
    "regiao": regiao,
    "dataPostagem" : dataPostagem,
    "regiaoCidade": regiaoCidade, 
    "resumo" : resumo,
    "url": url,}
    
    #adiciona na lista GERAL de JSON
    listaJson.append(json)
    
def retornarSoupSimples(url):
    auth = url.split("/")[2]
    path = url.split("/")[3]
    referer = url
    PARAMS = definirParams(auth = auth,path = path, referer = url )
    page = requests.get(url = url, headers = PARAMS)
    soup = BeautifulSoup(page.content, 'lxml')
    return soup
def clicarBotao(xpath):
    entToClick = driver.find_element_by_xpath(xpath)
    driver.execute_script("arguments[0].click();", entToClick)
def retornarSoupSellenium(url, timeAwait):
    driver.get(url)
    time.sleep(timeAwait)
    result = driver.page_source
    soup = BeautifulSoup(result, 'lxml')
    return soup

def scrollDown(rangeD = 30,clickBton = False, xPathBtn = "", timeSleep = 1.5):
     for a in range(0, rangeD):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        if clickBton == True:
            clicarBotao(xPathBtn)
        time.sleep(timeSleep)
        print("carregando mais dados...")
        
def buscarDadosOLX(pages = 10):
        
    for x in range(0, pages):
        try:
            print(" LOOP NÚMERO: " + str(x))
            url = "https://sp.olx.com.br/grande-campinas/imoveis?o="+str(x)
            soup = retornarSoupSimples(url)
            results = soup.find_all("li", {"class":"sc-1fcmfeb-2"})
            itens = results
            print(len(itens))
                        
            for a in itens:
            
                try:
                    titulo = a.findAll("a")[0]["title"]
                    url = a.findAll("a")[0]["href"]
                    preco = a.findAll("", {"aria-label" : re.compile("Preço")})[0].text
                    preco = preco.split("R$")[1]
                    preco = float(preco.replace(".", ""))
                    resumo = a.findAll("", {"title" : re.compile(r".*")})[0].text
                    dataPostagem = a.findAll("", {"aria-label" : re.compile("Anúncio")})[0].text
                    regiao = a.findAll("", {"aria-label" : re.compile("Localização")})[0].text
                    regiao = regiao.strip()
                    try:
                        regiaoCidade = regiao.split(",")[0]
                    except:
                        regiaoCidade = regiao
                        
                    #da Print e adiciona na lista geral
                    criarJson(dataPostagem, titulo, preco, url, regiao, regiaoCidade, resumo)
                    
                    
                except Exception as e:
                    print(url)
                    print("Erro na OLX no FOR iTENS: ", e)
                    pass
                
        except Exception as e:
            print("erro na url da OLX:" + url)
            print(e)
            pass
    print(len(listaJson))

    #inviavel, ficou muito demorado...
def buscarPropietarioDireto(pages = 10):
    #pages = 10
    for x in range(1, pages):
        url = "https://www.proprietariodireto.com.br/venda/imovel/direto-com-proprietario?page="+str(x)

        soup = retornarSoupSellenium(url, 10)

        print(len(soup.findAll("a", class_="style_card-property__3UzY-")))
        itens = soup.findAll("a", class_="style_card-property__3UzY-")
        for item in itens:
            print("Proprietario direto - page 1")
            print(item.findAll("a")[0])    
            
def buscarFacebook(rangeD = 15):
    
    url = "https://www.facebook.com/marketplace/112653438749352/propertyforsale/?latitude=-22.1324&longitude=-47.6714&radius=103"

    soup = retornarSoupSellenium(url, 5)
    
    #funcao de scrool down
    scrollDown(rangeD = rangeD, clickBton = False)
    
    #repicar as informações
    result = driver.page_source
    soup = BeautifulSoup(result, 'lxml')
    itens = soup.findAll("div", class_="kbiprv82")
    print(len(itens))
    for item in itens:
        try:
            url = url.split("marketplace")[0] + item.findAll("a")[0]["href"]
            url = url.replace("///////","/")
            print(item.findAll("", string= re.compile(r".*")))
            preco = item.findAll("", string= re.compile("R\$"))[0]
            preco = preco.split("R$")[1]
            preco = float(preco.replace(".", ""))
            titulo = item.findAll("", string= re.compile(r".*"))[1]
            regiao = item.findAll("", string= re.compile(r".*"))[2]
            regiaoCidade = regiao.split(",")[1]
        
            dataPostagem = "-"
            resumo = ' '.join(item.findAll("", string= re.compile(r".*")))
            print(resumo)
            criarJson(dataPostagem, titulo, preco, url, regiao, regiaoCidade, resumo)
        except Exception as e:
            print(url)
            print("Erro facebook")


def buscarLivima(rangeD = 30):
    url = "https://www.livima.com.br/buscar-imoveis?search_google=campinas&listing_search%5Bneighborhoods%5D%5B%5D=&listing_search%5Bstates%5D%5B%5D=&listing_search%5Bcities%5D%5B%5D=&price_range_min=&price_range_max=&area_range_min=&area_range_max=&listing_search%5Border%5D%5B%5D=Mais+recentes&type=sale&listing_search%5Brealty_types%5D%5B%5D="
    soup = retornarSoupSellenium(url, 1.5)
    print("buscando LIVIMA")
    #funcao de scrool down
    scrollDown(rangeD = rangeD, clickBton = True, xPathBtn="//*[@id='show-more']")
    
    #repicar as informações
    result = driver.page_source
    soup = BeautifulSoup(result, 'lxml')
    itens = soup.findAll("div", class_="listing-card")
    print(len(itens))
    for item in itens:
        try:
            url = url.split("buscar-imoveis")[0] + item.find("a")["href"]
            url = url.replace("/////////","/")
            #preco = item.findAll("", {"aria-label" : re.compile("Preço")})[0].text
            #print(item.findAll("", string= re.compile(r".*")))
            preco = item.findAll("", string= re.compile(r".*"))[2].strip()
            preco = preco.split(",")[0]
            preco = float(preco.replace(".", ""))
            regiao = item.findAll("", string= re.compile(r".*"))[3].strip()
            regiaoCidade = regiao.split(",")[2].strip()
            titulo = item.findAll("", string= re.compile(r".*"))[4] + " " + item.findAll("", string= re.compile(r".*"))[5] + " " + item.findAll("", string= re.compile(r".*"))[6] + " " + item.findAll("", string= re.compile(r".*"))[7]  + " " + item.findAll("", string= re.compile(r".*"))[8]
            dataPostagem= "-"
            resumo = item.findAll("", string= re.compile(r".*"))[0]
            criarJson(dataPostagem, titulo, preco, url, regiao, regiaoCidade, resumo)
        except Exception as e:
            print(e)

def buscarQuintoAndar(rangeD = 15):
    
    url = "https://www.quintoandar.com.br/comprar/imovel/campinas-sp-brasil"
    soup = retornarSoupSellenium(url, 1.5)
    scrollDown(rangeD = rangeD, clickBton = False, xPathBtn="")
    #repicar as informações
    result = driver.page_source
    soup = BeautifulSoup(result, 'lxml')
    itens = soup.findAll("div", class_="sc-1txbuf3-0 dWxyEy")
    print(len(itens))
    for item in itens:
        try:

            #preco = item.findAll("", {"aria-label" : re.compile("Preço")})[0].text
            #print(item.findAll("", string= re.compile(r".*")))

            url = item.findAll("a")[0]["href"]
            preco = item.findAll("", string= re.compile(r".*"))[5].strip()
            preco = preco.split("R$")[1]
            preco = float(preco.replace(".", ""))
            titulo = item.findAll("", string= re.compile(r".*"))[0].strip()
            regiao = item.findAll("", string= re.compile(r".*"))[2].strip()
            regiaoCidade = regiao.split(",")[1].strip()
            dataPostagem= "-"
            resumo = ' '.join(item.findAll("", string= re.compile(r".*")))
            criarJson(dataPostagem, titulo, preco, url, regiao, regiaoCidade, resumo)
        except Exception as e:
            print("erro no quinto andar", url)
            print(e)
            pass
def buscarImovelp(pages = 15):
    try:
        for x in range(1, pages):
            print("pagina Imovelp", x)
            url= "https://www.imovelp.com.br/busca-de-imoveis/todos/todos/sp/campinas/todos/de-0-a-0/0/0/0/1/0/5?pg="+str(x)+"#dv"
            soup = retornarSoupSellenium(url, 1.3)
            itens = soup.findAll("div", { "id": "centralizar-div-busca"})
            print(len(itens))
            for item in itens:
                #print(item.findAll("", string= re.compile(r".*")))

                preco = item.findAll("", string= re.compile("R\$"))[0].strip()
                preco = preco.split("R$")[1].strip().split(",")[0]
                preco = float(preco.replace(".", ""))
                titulo = item.findAll("", string= re.compile(r".*"))[14].strip()
                regiao = item.findAll("", string= re.compile(r".*"))[10].strip()
                regiaoCidade = regiao.split(" - ")[0].strip()
                dataPostagem= "-"
                resumo = ' '.join(item.findAll("", string= re.compile(r".*"))).strip()
                titulo = resumo
                try:
                    url = "https://www.imovelp.com.br" + item.findAll("a")[0]["href"]
                except:
                    url = url
                    pass
                criarJson(dataPostagem, titulo, preco, url, regiao, regiaoCidade, resumo)
                #print("\n")
                #alinharCampos(item,tituloIgualResumo = True, urlPrefix="https://www.imovelp.com.br",urlPosition = 0, 
                 #             precoPosition = 8, tituloPosition = 14, regiaoPosition = 10, regiaoCidadeSeparator = "-", 
                #regiaoCidadePosition = 0)
    
    except Exception as e:
            print("erro no imovelp", url)
            print(e)
            pass
    
def buscarZapImoveis(pages = 5):
    
    
    for x in range(1, pages):
        #try:
        print("Zap Imoveis - pagina", x)

        url = "https://www.zapimoveis.com.br/venda/imoveis/sp+campinas/?pagina="+str(x)+"&onde=,S%C3%A3o%20Paulo,Campinas,,,,,city,BR%3ESao%20Paulo%3ENULL%3ECampinas,,,&transacao=Venda&tipo=Im%C3%B3vel%20usado"
        soup = retornarSoupSellenium(url, 1.3)
        itens = soup.findAll("div", { "class": "card-container js-listing-card"})
        print(len(itens))
        for item in itens:
            #print(item.findAll("", string= re.compile(r".*")))
            url = url
            preco = item.findAll("", string= re.compile("R\$"))[0].strip()
            
            preco = preco.split("R$")[1]
            preco = float(preco.replace(".", ""))
            print(preco)
            allStrs =item.findAll("", string= re.compile(r".*"))
            
            #lógica pra deixar título com frase com maior contagem de caracteres
            lenStr = 0
            for string in allStrs:
                if len(string) > lenStr:
                    lenStr = len(string)
                    titulo = string.strip()
            
            print(titulo)
            try:
                regiao = item.findAll("", string= re.compile(r".*"))[19].strip()
                regiaoCidade = regiao.split(",")[1].strip()
            except Exception as e:
                print (e)
                pass
                
            dataPostagem= "-"
            resumo = ' '.join(item.findAll("", string= re.compile(r".*"))).strip()
            resumo = resumo.strip()
            criarJson(dataPostagem, titulo, preco, url, regiao, regiaoCidade, resumo)
           
        '''
        except Exception as e:
            print("erro no Zap Imoveis", url)
            print(e)
            pass
        '''
def buscarMercadoLivre(pages = 10):
    
    url = "https://imoveis.mercadolivre.com.br/sao-paulo/campinas/imoveis-venda_NoIndex_True#applied_filter_id%3Dcity%26applied_filter_name%3DCidades%26applied_filter_order%3D5%26applied_value_id%3DTUxCQ1NQLTc2MDI%26applied_value_name%3DCampinas%26applied_value_order%3D15%26applied_value_results%3D8884%26is_custom%3Dfalse%26view_more_flag%3Dtrue"
    for x in range(1, pages):
        try:
            print("MERCADO LIVRE, página", x)
            soup = retornarSoupSellenium(url, 1.3)
            itens = soup.findAll("li", { "class": "ui-search-layout__item"})
            print(len(itens))
            for item in itens:
                print(item.findAll("", string= re.compile(r".*")))
                print("\n")
                alinharCampos(item,tituloIgualResumo = False, urlPrefix="",urlPosition = 0, precoPosition = 2, tituloPosition = 6,
                              regiaoPosition = 6, regiaoCidadeSeparator = ",", regiaoCidadePosition = 3)
            if x == 1:
                clicarBotao("//*[@id='root-app']/div/div[2]/section/div[8]/ul/li[3]/a/span[1]")
            else:
                clicarBotao("//*[@id='root-app']/div/div[2]/section/div[8]/ul/li[4]/a/span[1]")
        except Exception as e:
            print("Erro na página MERCADLO LIVRE,", x)
            print(e)
            pass

def alinharCampos(item, tituloIgualResumo = False, urlPrefix = "", urlPosition = 0, precoPosition = 5, tituloPosition = 0, regiaoPosition = 2, regiaoCidadeSeparator = ",", regiaoCidadePosition = 1):
    url = item.findAll("a")[urlPosition]["href"]
    if urlPrefix != "":
        url = urlPrefix + url
    preco = item.findAll("", string= re.compile(r".*"))[precoPosition].strip()
    try:
        preco = preco.split("R$")[1]
    except Exception as e:
        print(e)
        pass
        
    try:
        preco = preco.split(",")[0]
    except Exception as e:
        print(e)
        pass
    try:
        preco = float(preco.replace(".", ""))
    except Exception as e:
        print(e)
        pass
    titulo = item.findAll("", string= re.compile(r".*"))[tituloPosition].strip()
    regiao = item.findAll("", string= re.compile(r".*"))[regiaoPosition].strip()
    regiaoCidade = regiao.split(regiaoCidadeSeparator)[regiaoCidadePosition].strip()
    dataPostagem= "-"
    resumo = ' '.join(item.findAll("", string= re.compile(r".*"))).strip()
    if tituloIgualResumo == True:
        titulo = resumo.strip()
    criarJson(dataPostagem, titulo, preco, url, regiao, regiaoCidade, resumo)
    
def soundFinal():
    duration = 2000  # milliseconds
    freq = 800  # Hz
    winsound.Beep(freq, duration)


# In[25]:


buscarDadosOLX(pages = 1)
buscarFacebook(rangeD = 1)
buscarLivima(rangeD = 1)
   #este site não dá scrollDown e demora mto pra carregar
   #buscarQuintoAndar(rangeD = 2)
buscarImovelp(pages = 2)
buscarZapImoveis(pages = 2)
buscarMercadoLivre(pages= 2)

soundFinal()


# In[26]:


#listaJson = []
df = pd.DataFrame(listaJson)
df.tail()


# In[27]:


df = pd.DataFrame(listaJson)
#df.tail(500)

with pd.ExcelWriter("dados2207.xlsx", options={'strings_to_urls': False}) as writer:
    df.to_excel(writer,"Teste")


# In[94]:




