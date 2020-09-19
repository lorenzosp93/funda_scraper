# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter, is_item
from scrapy.exceptions import DropItem
import codecs
import json
import requests

# Open config
openfile = open("config.json")
config = json.load(openfile)


def get_response_for_location(address:str, **kwargs) -> requests.Response:
    "Call Geocoding API to retrieve coordinates given an address"
    payload = {
        "location": address,
        "key": config.get("MAPQUEST_API_KEY"),
    }
    payload.update(kwargs)
    return requests.get(config.get("GEOCODE_API_URL"), params=payload)

def get_info_for_location(address:str, **kwargs) -> dict:
    "Retrieve the coordinates from API response"
    r = get_response_for_location(address, **kwargs)
    if r.ok:
        if (resp:=r.json())["info"]["statuscode"] == 0:
            return resp["results"][0]["locations"][0]
    return {}

class LocationPipeline:
    def process_item(self, item, spider):
        #put item inside an adapter
        adapter = ItemAdapter(item)
        #call API to retrieve information
        adapter.update(self.get_address_info(adapter, maxResults=1))

        return item

    def parse_info_for_location(self, address:str, **kwargs) -> dict:
        "Parse the information for each API call into fields expected by item"
        resp = get_info_for_location(address, **kwargs)
        if resp:
            return {
                "lat": resp["latLng"]["lat"],
                "lng": resp["latLng"]["lng"],
                "neighbourhood": resp["adminArea6"],
                "side_of_street": resp["sideOfStreet"]
            }
        return {"lat": "", "lng": "", "neighbourhood": "", "side_of_street": ""}


    def get_address_info(self, adapter:ItemAdapter, **kwargs) -> dict:
        "Return the address information based on the item's location"
        address = adapter.get("title")+", "+adapter.get("location")
        return self.parse_info_for_location(address, **kwargs)
    
class PricingPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        #validate price (if none, drop)
        self.validate_price(adapter)
        return item

    @staticmethod
    def validate_price(adapter:ItemAdapter) -> dict:
        "Ensure the item contains a price"
        if not adapter['price']:
            raise DropItem("Missing price in %s" % adapter)

class StripPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        #strip bad encoding
        self.strip_encoding(adapter)
        return item

    @staticmethod
    def strip_encoding(adapter:ItemAdapter) -> dict:
        for key, value in adapter.items():
            if isinstance(value, str):
                adapter[key] = value.strip().replace("\n", "").replace("\r", "")
        return adapter