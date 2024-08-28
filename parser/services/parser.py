from parser.services.google_sheets_api_client import upload_dataFrame_to_sheet

from bs4 import BeautifulSoup
import requests
import pandas as pd
import logging


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    'Referer': 'https://google.com',
}

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

    data = list()

    for page_href in links_list:
        response = requests.get(page_href, headers=HEADERS)
        soup = BeautifulSoup(response.text, 'lxml')

        if response.status_code != requests.codes.ok:
            logging.info(f'Problem with page {page_href}./nStatus_code: {response.status_code}')
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

def start_parsing_process() -> str:
    if __name__ == "__main__":
        logging.info('scheduled parsing')
    else:
        logging.info('pushed parsing')

    data = parse_catalog()
    worksheet = upload_dataFrame_to_sheet(dataFrame=data)
    logging.info(f'new information uploaded to {worksheet}')
    return 'Вы великомлепны. Данные успешно обновлены'

if __name__ == "__main__":
    res = start_parsing_process()
    print('jopa', res)
