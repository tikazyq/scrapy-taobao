# -*- coding: utf-8 -*-
import json
import re
from urllib import unquote

import requests
import scrapy
from bs4 import BeautifulSoup as bs

from merchants.items import TaobaoItem

cache = {}


class TaobaoSpider(scrapy.Spider):
    name = "taobao"
    base_url = 'https://s.taobao.com/search?q=%s&s=%s'
    base_url_shopcard = 'https://s.taobao.com/api?sid=%s&app=api&m=get_shop_card'
    page_interval = 44
    page_num = 100
    keywords = [
        u'羊肚菌',
        u'红薯',
    ]
    allowed_domains = ["taobao.com"]
    start_urls = [
        base_url % (kw, i * page_interval)
        for kw in keywords
        for i in range(page_num)
        ]

    def get_query(self, response):
        return unquote(re.search('q=([\w%]+)&?', response.url).group(1))

    def get_unit_price(self, elem):
        for icon in elem['icon']:
            m = re.search(u'<b>([\d+]+\.\d+)</b>\u5143/500g', icon['html'])
            if m is not None:
                return float(m.group(1))
        return None

    def get_rank(self, response, i):
        return int(re.search('s=(\d+)&?', response.url).group(1)) + i + 1

    def is_ad(self, elem):
        for icon in elem['icon']:
            if icon['icon_category'] == u'ad':
                return True
        return False

    def parse(self, response):
        query = self.get_query(response)
        sp = bs(response.body)
        raw = json.loads(re.search('g_page_config = (.*);\n', sp.select('script')[5].text).group(1))
        try:
            coll = raw['mods']['itemlist']['data']['auctions']
        except KeyError:
            return
        for i, elem in enumerate(coll):
            unit_price = self.get_unit_price(elem)
            rank = self.get_rank(response, i)
            is_ad = self.is_ad(elem)
            item = TaobaoItem(
                # basic
                id=elem['nid'],
                title=elem['title'],
                raw_title=elem['raw_title'],
                query=query,
                url=elem['detail_url'],
                # seller
                shop_id=elem['user_id'],
                shop_name=elem['nick'],
                shop_url=elem['shopLink'],
                is_tmall=elem['shopcard']['isTmall'],
                # seller rating
                sc_description_rating=elem['shopcard']['description'][0],
                sc_description_pct=elem['shopcard']['description'][2],
                sc_service_rating=elem['shopcard']['service'][0],
                sc_service_pct=elem['shopcard']['service'][2],
                sc_delivery_rating=elem['shopcard']['delivery'][0],
                sc_delivery_pct=elem['shopcard']['delivery'][2],
                # price
                view_price=elem['view_price'],
                reserve_price=elem['reserve_price'],
                view_fee=elem['view_fee'],
                unit_price=unit_price,
                weight=int(round(float(elem['view_price']) / unit_price * 500)) if unit_price is not None else None,
                # promotion
                rank=rank,
                is_ad=is_ad,
                # item info
                pic_url=elem['pic_url'],
                item_loc=elem['item_loc'],
                category=elem['category'],
                # stats
                view_sales=elem['view_sales'],
                comment_count=elem['comment_count'],
            )
            yield item
