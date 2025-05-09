#!D:\soft\api api
# -*- coding: utf-8 -*-
# @Time    : 2022/12/2 10:15
# @Author  : 杨硕
# @File    : get_response.py
# @Software: win11 Software Parser api 3.8.6
import sys

sys.path.append('./')
from setting import username, proxy, password, manager_url
import requests


class GetResponse:
    def __init__(self):
        self.verify_headers = {
            'authority': 'tools.usps.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
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
        self.track_headers = {
            'authority': 'tools.usps.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'client-ip': '152.195.79.111',
            # Requests sorts cookies= alphabetically
            # 'cookie': 'o59a9A4Gx=AyhMJMKEAQAA5GnrNQdjneuDewyIVyBj3ukbH2eAQLZMHZwsf8CWOA14_omWAXd7rayucmW8wH8AAEB3AAAAAA|1|0|be036823825b6531fd8e2c4dca4a19a961f9ff6a; TLTSID=773d15478ae1162d800800e0ed96ae55; NSC_tibqf-ofx=ffffffff3b22251d45525d5f4f58455e445a4a42378b; _ga_3NXP3C8S9V=GS1.1.1669702542.6.1.1669704469.0.0.0',
            'istl-infinite-loop': '1',
            'ns-client-ip': '119.123.173.172',
            'ns-client-port': '50818',
            'pragma': 'no-cache',
            'referer': 'https://tools.usps.com/go/TrackConfirmAction?tRef=fullpage&tLc=16&text28777=&tLabels=9400111206213536799186&tABt=false',
            'sec-ch-ua': '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
            'x-ec-internal-traffic-type': 'ORIGIN_SHIELD',
            'x-ec-pop': 'lab',
            'x-ec-session-id': '13577007280069655059422109354817143382',
            'x-ec-uuid': '1099657394561333915313267469691275500824',
            'x-forwarded-for': '119.123.173.172, 152.195.131.223',
            'x-forwarded-proto': 'https',
            'x-gateway-list': 'lab1',
            'x-host': 'tools.usps.com',
            'x-jfuguzwb-a': 'u6dCnGSvyUVOhlBdGfBhgV_4oGcVlvb6iVE=LcAJZJswwsxJaxb8mchC33xrrkVEdLICGd83_UfNi6VavrHOTLV8tmXfZP7IDMCTTvpwQBlK2d-E8fxCYRvqgPlnIQJlIh=JMA4zxpB59CtP1ncNE71DOP2XRetPuQRHXairm43jYTCDhQ0h1Z2UfG7ZRYCMM0OJncE0ayBmtw9k0OQ1Ddn1Z4q_VwcLDtjJEwao7vn_zZf_xfzxte9EhMOzbiX8oYncu7a7mQ7R8y7dCwkEeZg0uChe09Sj-QwLM5Qqs9GhAf4I2T=HEYumf0cWMo1JcpeeOScIm3wSU5tt_IY5o2KhUfn-kwhw1mT11HAUBw09PVRlsbwxkb2TSZcSPPzxInszkSNcJ=22YY1f2WzjKnQ_u34fUkNPoiaP4maLgQ=w7DrjS1xOvj=u4Jseeu__T0y-vZ0=ce2X=dxGX3nwBfPmNrSn9ZVxH34Xk-eUbpCs7YOQDe_vVGUqZWhW6ibAWEPza=mY6ACXZOjxQZOY1m693QDYIa9O4w2Et1SQucw6=uIVoeAb_mAlY0Gy=vPGw_Syy=W0UKJC4b8PLE2QB6bpgxuIuQ-r2-cTn61pnkuhN0xTeSyAvkqXN6u2hNqb2SNG2RZeeJb0csPBHn5Czx6BfWs8WMehx6tWfAHrd_Ja-D_8H2Rn_ctXpW4xYk5MrRxguvgwa9WyBl-nJeG=1HtDxNZiA_s2WJL-kSk5HNraYTPoa5bwwXOKmRdRgVadZqUYajr1lVII_1d2XVe_X47mNYZ8d=EW8RlkS8Bf1H=OUHzwcOP8gNz6cX-EUWsvbpPR-=SZCwdb1V6HZtlbAbdlfKgM7BdiZUkphUXx7rEZceBcWme9gP=y88R_XKyDr2nbvkAdwLwOMIn90-u9k0nAvgT9kOTLiOuCKkiJbeRxD-VHfp0GdOfCHI=zRPG66lgGLZedd4sUAfG0_EjaUBeotK1OUrrkLW3UugTYmT191NIcbt1AvfRbYDNHltuwCPlUbLXLeSjQqWfJ0S5pJuy62K=DiovloVBivtKGgdpD_PQ7TBiL5unhnCBkJQ4OGW=svt2VQms7uKPUvrHwUPIkVD=xegNul4a2gVLAZZ6lWLxgU-tIUxjvvIfotiAe5C9Ykl3mv_VOiOU3Shq2gEARMse4yAKWIU5LUgOkMCc_SmoMoEq9OzliihWzdXUU6uBCeT5=AmDDk6kKvhzGLH7ZslnCNDfgZY_lJeB0laf2kijiZg532phuJZEo960My6hDOih9wnckSEuglcZaYbQ9iGzk_JWcD6jb5ViMbq=RvY_78pKgQk_11KAon=pLDchSBjclmfqE25NfWNoQ_b5AwwKTHgGw0tRczJYm4xb4c0cn0vjSMjYyyZnecNdWLYVRNhfwEgmXjCtIM_Jc1XpS8feQjSWrq78oL7eCEW8vyttYpj=3wJDQxQldPjjkZcNn0Hh79E-WQ=ouaqQr1qS7WAdsyIttKHauJYrAA5npatlie077ANBAkAeyIUhmZCkLcpQafRwTlEe0Ez9TqLP-1PrZC2EcbAgxikfoUKnKOqmGnsZyz3-H33fduemz4MgGtNdVztnIjmR3l7QA_bIB4ArU6H9Bk=OPdfva=qEQ-16eTAmV73vtDgRXz=gXm812Yo2tNRY5Hpj5eI4h7yMj63y-HnLPTMsUPepYA4iPioeOvmTLqmC8eMGjDgeacJAdSAmearujMYNGwDc8NczgB5M40dvGj5ByA1kMxBEPXnJH2KS9nOeOfRRezvlATQTvNTjONGueIk2==Q0=taOkBZtaXYPc8u28H=i5fK0gYetkn-AjbRgj94OmEkipXEUL_m0f-i6inWp6c7H8UxJ9VpEKU_8Y6NavYuNLgHpKUw_ngn_TSQ5nLvBj-eShzvjEfMom6XqrMWrRYQICJWS=Bng6PXRZT=Lpm6GLw-6VXOOWU_YSXgpuD8HoZizAyqXWMDc0vqGzn4xfrKAVA2g8jAbhp=vxeBlCAb8b3N8LlZZY4MA6991TisGSf-o_ebK9K_NpdhGJvJmlhVKBm9-atAtORtszpGBRJQZMkxzPxH-GgaOj=kWmbf_e05K1IAotTT96LYm6703UzTdVvQzVtXhvyc3fiScYy7Wo8PM0Wkcv4Q5680336562vCLHZWbazOqk4rp-rW6CmdzqhjH7M229fyB_BTIqbTtBOiselSQswnOU07=XcXYnh8X-EIIvuwYp0xv3IjYZdg9PYK=CEwBmB05LkBZk7=hTR2EVH=Ugp_CHzSgrMyPDxj7E9Nrk4-bS3_Sc2i3fQo-i32ImwZuBpXZ87iL8984ozy0ZbN1y4-IiP-otHvBvvjVvy_bg2H6Y9d_RWgRWLv6EefzB-aENdTvQ-vqS3RM364Ds1cMuMiWJzag7WlRwPwRjxOaekAy8sDiH1Q9lhrp=SsrupOk4L=vIa_QH8VTC_H09WtB1QffXhgy1_Y29qG6GYQ9k7bsw2AiPMi26jnGjfNkoYXK4y=343QnLGjPVbBL=rvOuOqJfbqnAakZsJi_up3X7NKLD5e6_QNJf8aagp7BDIUn8R6fRcxoDDHSsaOt=Exla84bcyfHj81fJ114Khu4BL2lB6D62nbhYG00c=xyQm1ClPhYjT8-3Dr6B9=eW3zg8ijRkIuIsgOYpOw89Uy8OPZ=Nyrs63dYVvuun5KE7EaWlvmLRtHnmBzNz80jhMSsA-744vkOHeEMHZ3sIuk-e9_feI3kEBm4_t0LhvYSmf=WmB_=mM1ZB2b9nDoB13uG2=NctYyMuR0r=8CDYjMu89fbVsXZ=IdfXzvsrmTvvDuiUBAh13uUydLyaUiw-=-BI7C7JNbuZCER0zYM8AprVC1bg6_GExpLlxGGhGUO5gZHgelN79-G=juxsNuUMR1oU4a',
            'x-jfuguzwb-b': 'muj09w',
            'x-jfuguzwb-c': 'AOC1IcKEAQAAgy-yLbJW9LcvIiCgrsgdv_nyAmmvhJKmqAvptfp1g4FjQsR7',
            'x-jfuguzwb-d': 'ABaChAiBBKCMgUGAQZAQgICAAKIAgACBAgD6dYOBY0LEe______g4dfAARSim1FEtSI5ebzFotOrwO8',
            'x-jfuguzwb-f': 'AyhMJMKEAQAASHTQgh-P-ktu-ZpDqUvig9M0hcM_rUiFj-1nF8CWOA14_omWAXd7rayucmW8wH8AAEB3AAAAAA==',
            'x-jfuguzwb-z': 'q',
        }
        self.cookies = {'TLTSID': '84bac1108ae1162d8e0600e0ed96ae55',
                        'o59a9A4Gx': 'A_dg0tCEAQAAMCEhPL1CIT3dEiG8dcZPItrKMCm6cbG3T5V4w2zVrLQ0-GZKAT2_VY2ucmW8wH8AAEB3AAAAAA|1|0|f9c4fbc8d98ba5824094307c2b4bb3f2be779e12',
                        'NSC_tibqf-ofx': 'ffffffff3b22251e45525d5f4f58455e445a4a42378b'}

    @staticmethod
    def get_proxies():
        r_proxy = f'http://{username}:{password}@{proxy}'
        proxies = {
            'http': r_proxy,
            'https': r_proxy
        }
        return proxies

    def get_verify(self):
        verify_params = {
            'tRef': 'fullpage',
            'tLc': '16',
            'text28777': '',
            'tLabels': '',
            'tABt': 'false',
        }
        # proxies = self.get_proxies()
        verify_response = requests.get('https://tools.usps.com/go/TrackConfirmAction', params=verify_params,
                                       # proxies=proxies,
                                       headers=self.verify_headers, timeout=20)
        cookies = dict(verify_response.cookies)

        return cookies

    def get_get_response(self, track_url):
        response = requests.get(url=track_url,
                                cookies=self.cookies,
                                headers=self.track_headers, timeout=20)
        content = response.content.decode('utf-8')
        if response.status_code == 200 and len(content) > 100000:
            return content
        else:
            self.get_token()
            proxies = self.get_proxies()
            response = requests.get(url=track_url,
                                    proxies=proxies,
                                    cookies=self.cookies,
                                    headers=self.track_headers, timeout=20)
            content = response.content.decode('utf-8')
            if response.status_code == 200 and len(content) > 100000:
                return content

    def get_post_response(self, track_url):
        response = requests.post(url=track_url,
                                 cookies=self.cookies,
                                 headers=self.track_headers, timeout=20)
        content = response.content.decode('utf-8')
        if response.status_code == 200 and len(content) > 100000:
            return content
        else:
            self.get_token()
            proxies = self.get_proxies()
            response = requests.post(url=track_url,
                                     proxies=proxies,
                                     cookies=self.cookies,
                                     headers=self.track_headers, timeout=20)
            content = response.content.decode('utf-8')
            if response.status_code == 200 and len(content) > 100000:
                return content

    @staticmethod
    def get_token():
        while True:
            try:
                r = requests.get(url=manager_url)
                token = r.json().get('token')
                if token:
                    return token
            except Exception:
                continue
