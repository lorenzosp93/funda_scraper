"""This module defines the basic spiders that 
will be used to scrape information from Funda"""

from scrapy import Spider, Request
from ..items import MyFundaScraperItem

class ListingSpider(Spider):
    name = "listings"
    city = "amsterdam"
    start_price = 0
    end_price = 10000000
    day_selector = {
            "1": "1-dag/",
            "2": "3-dagen/",
            "3": "5-dagen/",
            "4": "10-dagen/"
        }
    day = ""


    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        if self.day:
            self.day = self.day_selector[self.day]
        self.get_start_urls(**kwargs)

    def get_start_urls(self, **kwargs):
        self.start_urls = [f"""https://www.funda.nl/en/koop/{self.city}/\
                {self.start_price}-{self.end_price}/{self.day}\
            """]
    
    def get_day_selection(self, day):
        return self.day_selector[day]

    # def start_requests(self, **kwargs):
    #     return super.start_requests()

    def parse(self, response, **kwargs):
        """
        Parse the list view page for links based on css tag
        
        Contracts
        ---------
        @url https://www.funda.nl/en/koop/amsterdam/
        @returns requests 1 16
        @scrapes title price
        """
        self.logger.info(f"Parse List function called on {response.url}")

        yield from response.follow_all(
            set(response.css(".search-result__header-title-col a::attr(href)").getall()),
            callback=self.parse_listing,
        )
        next_page = response.css(".pagination a[rel='next']::attr(href)").get()
        if next_page:
            yield response.follow(
                next_page,
                callback=self.parse,
            )
        

    @staticmethod
    def extract_with_css(response, query):
        return response.css(query).get(default='')
    @staticmethod
    def extract_from_table_text_with_xpath(response, text):
        return response.xpath(
                f"//*[contains(text(),'{text}')]/following-sibling::dd/text()"
            ).get(default='')

    def parse_listing(self, response, **kwargs):
        """
        Parse the listing page, based both on css tags and name of previous table element
        
        Contracts
        ---------
        @url https://www.funda.nl/koop/verkocht/amsterdam/huis-87275014-paul-scholtenstraat-4/
        @returns item 1
        @scrapes title location
        """
        self.logger.info(f"Parse Listing function called on {response.url}")        
        
        yield self.funda_extract_listing(response)

    def funda_extract_listing(self, response):      
        item = MyFundaScraperItem()
        extract_with_css = lambda query: self.extract_with_css(response, query)
        extract_from_table_text_with_xpath = (
                lambda text: self.extract_from_table_text_with_xpath(response, text)
            )

        item.update({
            "url": response.url,
            "title": extract_with_css(".object-header__title::text"),
            "location": extract_with_css(".object-header__subtitle::text"),
            "status": extract_with_css(".label-transactie-voorbehoud::text"),
            "price": extract_with_css(".object-header__price::text"),
            "price_per_sqm": extract_with_css("dt.object-kenmerken-list__asking-price + dd::text"),
            "expenses": extract_from_table_text_with_xpath("VVE (Owners Association) contribution"),
            "created_date": extract_from_table_text_with_xpath("Listed since"),
            "year": extract_from_table_text_with_xpath("Year of construction"),
            "space": extract_from_table_text_with_xpath("Area"),
            "living": extract_from_table_text_with_xpath("Living area"),
            "balcony": extract_from_table_text_with_xpath("Exterior space attached to the building"),
            "outdoor": extract_from_table_text_with_xpath("External storage space"),
            "other": extract_from_table_text_with_xpath("Other space inside the building"),
            "volume": extract_from_table_text_with_xpath("Volume in cubic meters"),
            "total_rooms": extract_from_table_text_with_xpath("Number of rooms"),
            "bathrooms": extract_from_table_text_with_xpath("Number of bath rooms"),
            "number_of_stories": extract_from_table_text_with_xpath("Number of stories"),
            "floor": extract_from_table_text_with_xpath("Located at"),
            "services": extract_from_table_text_with_xpath("Facilities"),
            "energy_rating": extract_with_css(".energielabel::text"),
            "insulation": extract_from_table_text_with_xpath("Insulation"),
            "heating": extract_from_table_text_with_xpath("Heating"),
        })
        return item

class SoldListingSpider(ListingSpider):
    name = "sold_listings"
    def get_start_urls(self, **kwargs):
        self.start_urls = [f"""https://www.funda.nl/en/koop/{self.city}/\
                {self.start_price}-{self.end_price}/verkocht/\
            """]

    def parse_listing(self, response, **kwargs):
        item = self.funda_extract_listing(response)
        item.update({
            "sold_date": self.extract_from_table_text_with_xpath(
                    response,
                    "Date of sale"
                ),
            "price": self.extract_with_css(
                    response,
                    ".object-header__price--historic::text"
                ),
        })
        yield item