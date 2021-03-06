# -*- coding: utf-8 -*-
import json
import logging
import re
from urllib import unquote

import requests
import scrapy
from bs4 import BeautifulSoup as bs

from merchants.items import TaobaoItem

cache = {}


class TaobaoSpider(scrapy.Spider):
    name = "taobao"
    base_urls = {
        'default': 'https://s.taobao.com/search?q=%s&s=%s',
        'renqi': 'https://s.taobao.com/search?q=%s&s=%s&sort=renqi-desc',
        'sale': 'https://s.taobao.com/search?q=%s&s=%s&sort=sale-desc',
        'credit': 'https://s.taobao.com/search?q=%s&s=%s&sort=credit-desc',
    }
    base_url_counter3 = 'https://count.taobao.com/counter3?callback=json86&sign=26024ae05065c1dad23b856300dd656ed20ac&keys=DFX_200_1_%s,ICVT_7_%s,ICCP_1_%s,SCCP_2_%s'
    base_url_shopcard = 'https://s.taobao.com/api?sid=%s&app=api&m=get_shop_card'
    base_url_item = 'https://item.taobao.com/item.htm?id=%s'
    base_url_item_detail = 'https://detailskip.taobao.com/service/getData/1/p1/item/detail/sib.htm?itemId=%s&modules=qrcode,viewer,price,contract,duty,xmpPromotion,dynStock,delivery,activity,fqg,zjys,coupon,soldQuantity'
    page_interval = 44
    page_num = 100
    allowed_domains = ["tmall.com", "taobao.com"]

    def __init__(self, keywords='', sort_type='default'):
        print keywords
        self.keywords = keywords.split(',')
        self.query_sort_type = sort_type if sort_type in self.base_urls.keys() else 'default'
        self.base_url = self.base_urls[self.query_sort_type]
        self.start_urls = [
            self.base_url % (kw, i * self.page_interval)
            for kw in self.keywords
            for i in range(self.page_num)
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

    def get_shop_web_id(self, response):
        return re.search('shopId=(\d+);', response.body).group(1)

    def wrap_url(self, id):
        return 'http://item.taobao.com/item.htm?id=%s' % id

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
                query_sort_type=self.query_sort_type,
                url=elem['detail_url'],
                # seller
                shop_id=elem['user_id'],
                shop_name=elem['nick'],
                shop_url=elem['shopLink'],
                is_tmall=elem['shopcard']['isTmall'],
                # seller rating
                sc_description_rating=elem['shopcard']['description'][0],
                sc_description_pct=int(elem['shopcard']['description'][1]) * int(elem['shopcard']['description'][2]),
                sc_service_rating=elem['shopcard']['service'][0],
                sc_service_pct=int(elem['shopcard']['service'][1]) * int(elem['shopcard']['service'][2]),
                sc_delivery_rating=elem['shopcard']['delivery'][0],
                sc_delivery_pct=int(elem['shopcard']['delivery'][1]) * int(elem['shopcard']['delivery'][2]),
                seller_credit=elem['shopcard'].get('sellerCredit'),
                total_rate=elem['shopcard'].get('totalRate'),
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

            s = requests.Session()
            s.headers['referer'] = response.url
            yield scrapy.Request(self.base_url_item % item['id'],
                                 callback=self.parse_item,
                                 meta={'item': item,
                                       'dont_merge_cookie': True})

    def parse_item(self, response):
        item = response.meta['item']
        item['shop_web_id'] = self.get_shop_web_id(response)
        yield scrapy.Request(self.base_url_item_detail % item['id'],
                             callback=self.parse_item_detail,
                             meta={'item': item,
                                   'dont_merge_cookie': True})

    def parse_item_detail(self, response):
        item = response.meta['item']
        data = json.loads(response.body.strip())['data']
        item['sold_total_count'] = data['soldQuantity']['soldTotalCount']
        item['confirmed_sales'] = data['soldQuantity']['confirmGoodsCount']
        item['stock_type'] = data['dynStock']['stockType']
        item['stock_qty'] = data['dynStock']['stock']
        item['stock_hold_qty'] = data['dynStock']['holdQuantity']
        item['stock_available_qty'] = data['dynStock']['sellableQuantity']
        yield scrapy.Request(self.base_url_counter3 % (item['id'], item['id'], item['id'], item['shop_web_id']),
                             callback=self.parse_item_counter,
                             meta={'item': item,
                                   'dont_merge_cookie': True})

    def parse_item_counter(self, response):
        item = response.meta['item']
        raw = json.loads(re.search('json86\((.*)\);', response.body.strip()).group(1))
        item['dfx_200_1'] = raw['DFX_200_1_%s' % item['id']]
        item['icvt_7'] = raw['ICVT_7_%s' % item['id']]
        item['iccp_1'] = raw['ICCP_1_%s' % item['id']]
        item['sccp_2'] = raw['SCCP_2_%s' % item['shop_web_id']]
        yield item
