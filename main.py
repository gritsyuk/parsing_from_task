from asyncio import TaskGroup, run, sleep
from aiohttp import ClientSession
from bs4 import BeautifulSoup
import time
import json
import pandas as pd
from config import proxies, headers

async def get_all_id() -> list:
    result = []
    url = r"https://akv.task-tm.com:30201/tm/approval/all"
    async with ClientSession(headers=headers) as session:
        async with session.get(url, proxy=proxies.get("http")) as res:
            if res.status == 200:
                html = await res.text()
                soup = BeautifulSoup(html, "html.parser")
                all_approval = soup.find_all('tr', class_ = 'ac')
                for data in all_approval:
                    result.append(int(data['data']))
            else:
                print(f"ERROR in fn: get_all_id")
    return result

async def gather_data(list_id) -> dict:
    parser_res = {}
    async with ClientSession(headers=headers) as session:
        async with TaskGroup() as tg:
            for id in list_id:
                tg.create_task(get_data(session, id, parser_res))
    
    return parser_res

async def get_data(session, id: int, res_dict: dict):
    url = f'https://akv.task-tm.com:30201/tm/action/?vx=form/approving/approve/get'
    data = f'-----------------------------8677523423436311045504554915\r\nContent-Disposition: form-data; name=\"type\"\r\n\r\nform\r\n-----------------------------8677523423436311045504554915\r\nContent-Disposition: form-data; name=\"realm\"\r\n\r\napproving\r\n-----------------------------8677523423436311045504554915\r\nContent-Disposition: form-data; name=\"name\"\r\n\r\napprove\r\n-----------------------------8677523423436311045504554915\r\nContent-Disposition: form-data; name=\"action\"\r\n\r\nget\r\n-----------------------------8677523423436311045504554915\r\nContent-Disposition: form-data; name=\"object\"\r\n\r\n{{\"id\":{id}}}\r\n-----------------------------8677523423436311045504554915--\r\n'
    await sleep(0.5)
    async with session.post(url=url, data=data, proxy=r'http://192.168.141.2:26280') as card_approval:
        res = await card_approval.read()
        json_text = json.loads(res)
        res_dict[id] = json_text['approve']

def time_execution(func):
    async def wrapped():
        print("Старт ....")
        start = time.time()
        await func()
        task_time = round(time.time() - start, 2)
        print(f"Время исполнения: {task_time} сек")
        
    return wrapped    

@time_execution                      
async def main():
    all_id = await get_all_id()
    print("Количество задач в Task: {}".format(len(all_id)))
    parser_res = await gather_data(all_id)
    df = pd.DataFrame.from_dict(parser_res, orient='index')  
    df_new = df[['id','created', 'approvers', 'status_id', 'is_canceled', 'is_closed', 'subj',  'building_id', 'building']]
    df_new_explode = df_new.explode('approvers', ignore_index=True)
    pd.json_normalize(df_new_explode['approvers'])
    df_s = pd.concat([df_new_explode.drop('approvers', axis=1), pd.json_normalize(df_new_explode['approvers'])], axis=1)
    df_s.to_excel("task.xlsx")
    print("Создана Excel таблица с преобразоваными данными") 
    
if __name__ == "__main__":
    run(main())
