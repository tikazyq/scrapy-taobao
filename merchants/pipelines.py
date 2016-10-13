# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import re


def get_sales(item):
    return int(re.search('(\d+)', item['view_sales']).group(1))


class MerchantsPipeline(object):
    def process_item(self, item, spider):
        item['reserve_price'] = float(item['reserve_price'])
        item['view_price'] = float(item['view_price'])
        item['view_fee'] = float(item['view_fee'])
        item['view_sales'] = get_sales(item)
        return item
