#!/usr/bin/env bash

d=$(date +%Y%m%d%H)
cd /Users/yeqing/projects/taixiangny/merchants
/usr/local/bin/scrapy crawl taobao -o /Users/yeqing/projects/taixiangny/merchants/merchants/data/taobao.${d}.csv -t csv