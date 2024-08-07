import os
import logging
import time

from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests
import gspread
import pandas as pd

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="parser_logs.log",
    encoding='utf-8',
)

def parse_catalog() -> pd.DataFrame:
    with open('upgrade33_links.txt', 'r') as f:
        links_list = [line.strip() for line in f.readlines()]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
        'Referer': 'https://google.com',
    }

    data = list()

    for page_href in links_list:
        response = requests.get(page_href, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')

        if response.status_code != requests.codes.ok:
            logging.info(f'Проблема со страницой {page_href}./nКод ошибки: {response.status_code}')
            continue

        # Ищем блок с товарами
        if soup.find('div', class_='product-thumb'):
            for good in soup.find_all('div', class_='product-thumb'):
                title_img = title_caption = ''
                
                title_img = good.find('img', class_='img-responsive').get('alt')
                title_caption = good.find('div', class_='caption').find('a').text.strip(' ."\t\n')

                title = title_img if len(title_img) >= len(title_caption) else title_caption
                
                data.append({
                    "title": title,
                    "price": good.find('div', class_='caption').find('a').get('href'), 
                    "href": good.find('p', class_='price').text.strip((' ."\t\n')),
                })
        else:
            logging.info(f'Страница без товаров: {page_href}')

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

    return pd.DataFrame(data)

def upload_dataFrame_to_sheet(dataFrame: pd.DataFrame) -> None:
    gc = gspread.service_account(filename="creds.json")
    sheet = gc.open("tehno37_parsing")

    all_worksheets = sheet.worksheets()
    if len(all_worksheets) >= 185:
        worksheet_to_delete = sheet.get_worksheet(index=1)
        sheet.del_worksheet(worksheet=worksheet_to_delete)
        
        logging.info(f'worksheet {worksheet_to_delete} is deleted')

    new_worksheet = sheet.add_worksheet(title=f"{time.asctime()}", rows=dataFrame.shape[0]+100, cols=26)
    new_worksheet.update([dataFrame.columns.values.tolist()] + dataFrame.values.tolist())
    return new_worksheet


if __name__ == "__main__":
    logging.info(f'run from terminal')
    data = parse_catalog()
    worksheet = upload_dataFrame_to_sheet(dataFrame=data)
    logging.info(f'new information uploaded to {worksheet}')
    print("jopa", os.getenv('TELEGRAM_BOT_TOKEN'))


# Функционал бота:
#   - запустить парсинг внепланово и получить ответ
#   - добавить новые ссылки для товаров из новых категорий
