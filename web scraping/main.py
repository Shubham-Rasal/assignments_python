import requests
# original_encoding = 'utf-8'
print('hello')
from bs4 import BeautifulSoup

url="https://en.wikipedia.org/wiki/Cat"
r=requests.get(url)
htmlContent=r.content
# print(htmlContent)
soup=BeautifulSoup(htmlContent,'html.parser')
# print(soup.prettify('utf-8'))

# para=soup.find('p')
# print(para)
print(soup.p.contents)
# print(soup.find('div'))
# title=soup.title.contents
# print(title)
# text=soup.find('p').children
# print(text)
# data=soup.find_all('a')
# print(data)
# print(soup.get_text())
# scripts=soup.find('script')
# print(scripts)P