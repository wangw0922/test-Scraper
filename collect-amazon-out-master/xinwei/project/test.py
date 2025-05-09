import asyncio
import datetime
import random
import time
import multiprocessing
import requests
import aiohttp

from xinwei.project.setting import get_token_url, tunnel_name


async def test():
    while True:
        url = "http://127.0.0.1:5001/get_token"
        data = {"tunnel_name": "tunnel2"}
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, data=data) as res:
                result = await res.json(content_type='text/html', encoding='utf-8')
        await asyncio.sleep(5)


async def test1():
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url=get_token_url, data={"tunnel_name": tunnel_name}) as token_res:
                    token_dict = await token_res.json(content_type='text/html', encoding='utf-8')
                    result = token_dict.get("result")
                    token = token_dict.get("token")
        except:
            print("Request token exception，retry")
            time.sleep(5)
            continue
        if result:
            print(f'-------------current token: {token}----------------')
            break
        else:
            print('Request overclocking,please waiting！')
            await asyncio.sleep(61 - datetime.datetime.now().second + random.randint(1, 60))

if __name__ == '__main__':
    # loop = asyncio.get_event_loop()
    # tasks = [asyncio.ensure_future(test1()) for _ in range(50)]
    # loop.run_until_complete(asyncio.wait(tasks))
    import requests

    r = requests.Session()
    pdata = {
        "group": "test",
        "action": "b",
        "word": "ok"
    }
    reult = r.get("http://192.168.159.132:5620/business-demo/invoke", params=pdata, verify=False).text
    print(reult)








