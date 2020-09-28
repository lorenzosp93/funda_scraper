# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class MyFundaScraperItem(Item):
    # define the fields for your item here like:
    url = Field()
    title = Field()
    location = Field()
    status = Field()
    price = Field()
    price_per_sqm = Field()
    expenses = Field()
    created_date = Field(serializer=str)
    year = Field()
    space = Field()
    living = Field()
    outdoor = Field()
    balcony = Field()
    other = Field()
    volume = Field()
    total_rooms = Field()
    bathrooms = Field()
    number_of_stories = Field()
    floor = Field()
    services = Field()
    energy_rating = Field()
    insulation = Field()
    heating = Field()
    sold_date = Field()
    lat = Field()
    lng = Field()
    neighbourhood = Field()
