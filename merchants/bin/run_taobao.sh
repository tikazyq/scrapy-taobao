#!/usr/bin/env bash

d=$(date +%Y%m%d%H)
cd /Users/yeqing/projects/taixiangny/merchants
/usr/local/bin/scrapy crawl taobao -a keywords="羊肚菌" -o /Users/yeqing/projects/taixiangny/merchants/merchants/data/taobao.morel.${d}.csv -t csv
/usr/local/bin/scrapy crawl taobao -a keywords="红薯" -o /Users/yeqing/projects/taixiangny/merchants/merchants/data/taobao.sweetpotato.${d}.csv -t csv
/usr/local/bin/scrapy crawl taobao -a keywords="柠檬" -o /Users/yeqing/projects/taixiangny/merchants/merchants/data/taobao.lemon.${d}.csv -t csv
