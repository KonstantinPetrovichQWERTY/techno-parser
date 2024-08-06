from bs4 import BeautifulSoup
import requests
import gspread
import pandas as pd
from datetime import datetime


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
            
            title_img = good.find('img', class_='img-responsive').get('alt')
            title_caption = good.find('div', class_='caption').find('a').text.strip(' ."\t\n')

            title = title_img if len(title_img) >= len(title_caption) else title_caption
            
            result.append({
                "title": title,
                "price": good.find('div', class_='caption').find('a').get('href'), 
                "href": good.find('p', class_='price').text.strip((' ."\t\n')),
            })
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


df = pd.DataFrame(result)

gc = gspread.service_account(filename="creds.json")
sh = gc.open("tehno37_parsing")
worksheet = sh.add_worksheet(title=f"update_{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", rows=df.shape[0]+100, cols=df.shape[1]+20)

worksheet.update([df.columns.values.tolist()] + df.values.tolist())

print("jopa")
