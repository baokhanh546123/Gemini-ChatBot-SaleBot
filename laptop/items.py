# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class LaptopItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = scrapy.Field()
    cpu = scrapy.Field()
    ram = scrapy.Field()
    rom = scrapy.Field()
    price = scrapy.Field()
