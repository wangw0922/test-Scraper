import sys
sys.path.append('....')
import os
import datetime
import asyncio
import re
import ddddocr
import random
import aiohttp
import ssl
from lxml import etree
from xinwei.project.Collect.src.loggerDefine import logger_define
from xinwei.project.setting import proxy, username, password, cookies, get_token_url, tunnel_name

my_logger = logger_define(os.getcwd(), 'asyncio')


class Verify:
    def __init__(self):
        self.tunnel = proxy
        self.proxy_auth = aiohttp.BasicAuth(username, password)
        self.headers = {
            'authority': 'www.amazon.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'referer': 'https://www.amazon.com/errors/validateCaptcha',
            'sec-ch-ua': '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
        }
        self.cookies = cookies

    @staticmethod
    def get_ssl() -> ssl.SSLContext:
        """修改tls加密逻辑"""
        ORIGIN_CIPHERS = ('ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+HIGH:'
                          'DH+HIGH:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+HIGH:RSA+3DES')
        ciphers = ORIGIN_CIPHERS.split(':')
        random.shuffle(ciphers)
        ciphers = ":".join(ciphers)
        ciphers = ciphers + ":!aNULL:!eNULL:!MD5"
        context = ssl.create_default_context()
        context.options |= ssl.OP_NO_SSLv3
        context.options |= ssl.OP_NO_SSLv2
        context.options |= ssl.OP_NO_TLSv1_1
        context.options |= ssl.OP_NO_TLSv1_2
        context.options |= ssl.OP_NO_TLSv1_3
        context.set_ciphers(ciphers)
        return context

    @staticmethod
    async def get_field_keywords(image_name) -> ddddocr.DdddOcr.classification:
        """识别验证码"""
        ocr = ddddocr.DdddOcr()
        with open(f'project\\Collect\\verify_img\\{image_name}.jpg', 'rb') as f:
            img_bytes = f.read()
        field_keywords = ocr.classification(img_bytes)
        os.remove(f'project\\Collect\\verify_img\\{image_name}.jpg')
        return field_keywords

    @staticmethod
    async def save_imgs(img_url, image_name) -> None:
        """保存验证码图片"""
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=50)) as session:
            async with session.get(img_url) as r:
                content = await r.read()
            with open(f'project\\Collect\\verify_img\\{image_name}.jpg', 'wb') as f:
                f.write(content)

    async def get_verify_comtent(self) -> str:
        """请求验证码页面"""
        for i in range(3):
            sslgen = self.get_ssl()
            timeout = aiohttp.ClientTimeout(total=20)
            try:
                async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=50)) as session:
                    async with session.get(url='https://www.amazon.com/errors/validateCaptcha', cookies=self.cookies,
                                           ssl=sslgen,
                                           headers=self.headers, timeout=timeout) as resp:
                        content = await resp.text()
                        return content
            except Exception:
                continue
        return ""

    async def get_token(self, detaile_url) -> str:
        """请求商品页面"""
        for i in range(5):
            url = 'https://www.amazon.com/errors/validateCaptcha'
            content = await self.get_verify_comtent()
            if not content:
                continue
            try:
                data = etree.HTML(content)
                amzn = data.xpath('/html/body/div/div[1]/div[3]/div/div/form/input[1]/@value')[0]
                amzn_r = re.search('https://www.amazon.com(.*)', detaile_url).group(1)
                img_url = data.xpath('/html/body/div/div[1]/div[3]/div/div/form/div[1]/div/div/div[1]/img/@app')[0]
                import hashlib
                image_name = hashlib.md5(detaile_url.encode("utf8")).hexdigest()
                await self.save_imgs(img_url, image_name)
                field_keywords = await self.get_field_keywords(image_name)
            except Exception:
                continue
            params = {
                'amzn': amzn,
                'amzn-r': amzn_r,
                'field-keywords': field_keywords,
            }
            sslgen = self.get_ssl()
            while True:
                async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=50)) as session:
                    async with session.post(url=get_token_url, data={"tunnel_name": tunnel_name}) as token_res:
                        try:
                            token_dict = await token_res.json(content_type='text/html', encoding='utf-8')
                            token = token_dict.get("token")
                            result = token_dict.get("result")
                        except:
                            my_logger.info("Request token exception，retry")
                            await asyncio.sleep(5)
                            continue
                        if result:
                            my_logger.info(f'-------------current token: {token}----------------')
                            break
                        else:
                            my_logger.info('Request overclocking,please waiting！')
                            await asyncio.sleep(61 - datetime.datetime.now().second + random.randint(1, 60))
            try:
                timeout = aiohttp.ClientTimeout(total=20)
                async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=50)) as session:
                    # proxy="http://" + self.tunnel,  proxy_auth=self.proxy_auth,
                    async with session.get(url=url, cookies=self.cookies, ssl=sslgen,
                                           headers=self.headers, params=params, timeout=timeout) as resp:
                        content = await resp.text()
                    if resp.status == 200 and len(content) > 20000:
                        return content
                    else:
                        continue
            except Exception:
                continue
        return ""
