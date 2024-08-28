import time
import logging

import gspread
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="parser_logs.log",
    encoding='utf-8',
)

def upload_dataFrame_to_sheet(dataFrame: pd.DataFrame) -> None:
    gc = gspread.service_account(filename="creds.json")
    sheet = gc.open("tehno37_parsing")

    all_worksheets = sheet.worksheets()
    if len(all_worksheets) >= 185:
        worksheet_to_delete = sheet.get_worksheet(index=1)
        sheet.del_worksheet(worksheet=worksheet_to_delete)
        
        logging.info(f'worksheet {worksheet_to_delete} is deleted')

    new_worksheet = sheet.add_worksheet(title=f"{time.asctime()}", 
                                        rows=dataFrame.shape[0]+100, 
                                        cols=26)
    
    new_worksheet.update([dataFrame.columns.values.tolist()] + dataFrame.values.tolist())
    return new_worksheet
