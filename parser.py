from bs4 import BeautifulSoup
import requests
import csv
import datetime
import os


with open('links_DO_NOT_CHANGE_FILE_TITLE.txt', 'r') as f:
    links_list = [line.strip() for line in f.readlines()]


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    'Referer': 'https://google.com',
}


result = list()


for page in links_list:
    response = requests.get(page, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')

    if response.status_code != requests.codes.ok:
        print(f'Проблема со страницой {page}./nКод ошибки: {response.status_code}')
        continue

    # Ищем блок с товарами
    if soup.find('div', class_='product-thumb'):
        for good in soup.find_all('div', class_='product-thumb'):
            title_img = title_caption = ''
            if good.find('img', class_='img-responsive'):
                title_img = good.find('img', class_='img-responsive').get('alt')
            if good.find('div', class_='caption'):
                elem = good.find('div', class_='caption')
                title_caption = elem.find('a').text.strip()
                href = elem.find('a').get('href')
            if good.find('p', class_='price'):
                price = good.find('p', class_='price').text.strip()
            title = title_img if len(title_img) > len(title_caption) else title_caption
            result.append([title, price, href])
    else:
        print(f'Страница без товаров: {page}')

    # Ищем другие категории
    if soup.find('a', class_='catpr2'):
        for tag in soup.find_all('a', class_='catpr2'):
            link = tag.get('href')
            if link not in links_list:
                links_list.append(link)

    # Ищем блок со следующими страницами этой же категории
    if soup.find('ul', class_='pagination'):
        pagination = soup.find('ul', class_='pagination').find('li', class_='active')
        if pagination.next_sibling:
            link = pagination.next_sibling.find('a').get('href')
            if link not in links_list:
                links_list.append(link)

print("jopa")
print(result)

# field names 
fields = ('Titile', 'Price', 'Link')

# data rows of csv file 
rows = result

with open(f'parse.csv', 'w', encoding='utf-8', newline='') as f:
	
	# using csv.writer method from CSV package
	write = csv.writer(f)
	write.writerow(fields)
	write.writerows(result)



# структура 
# |- .exe
# |- ссылки_НЕ_МЕНЯТЬ_НАЗВАНИЕ.txt
# |- парсы
#    |- парс_1
#    |- парс_2
# TODO: сделать так чтобы окно exe не закрывалось после выполнения
