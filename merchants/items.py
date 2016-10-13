# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TaobaoItem(scrapy.Item):
    # basic
    id = scrapy.Field()
    title = scrapy.Field()
    raw_title = scrapy.Field()
    query = scrapy.Field()
    url = scrapy.Field()

    # seller
    shop_id = scrapy.Field()
    shop_name = scrapy.Field()
    shop_url = scrapy.Field()
    is_tmall = scrapy.Field()

    # seller rating
    sc_description_rating = scrapy.Field()
    sc_description_pct = scrapy.Field()
    sc_service_rating = scrapy.Field()
    sc_service_pct = scrapy.Field()
    sc_delivery_rating = scrapy.Field()
    sc_delivery_pct = scrapy.Field()

    # price
    view_price = scrapy.Field()  # 展示价格
    reserve_price = scrapy.Field()  # 原始价格
    view_fee = scrapy.Field()  # 邮费
    unit_price = scrapy.Field()  # 单位价格(500g)
    weight = scrapy.Field()  # 净重(g)

    # promotion
    rank = scrapy.Field()  # 排名
    is_ad = scrapy.Field()  # 是否为广告

    # item info
    pic_url = scrapy.Field()
    item_loc = scrapy.Field()
    category = scrapy.Field()

    # stats
    view_sales = scrapy.Field()  # 近30天支付数量
    comment_count = scrapy.Field()  # 总评论数
