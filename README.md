# Funda.nl scraper for feeding to ML pipeline

## Description

This project employs a Scrapy pipeline to retrieve listings data from Funda.nl, and place calls to a geocoding API returning coordinates and information about the street and neighbourhood, which are then fed to a ML algorithm in order to make predictions regarding expected valuation of new listings vs. the current asking price.

Two scrapers exists:

* current (open) listings, employing the `listings` spider,
* historical (sold) listings, employing the `sold_listings` spider.

### Instructions

To start the scraper, `cd` to the base folder and run the following command:

```bash
scrapy crawl [scraper] -o [output name] -a [options]
```

The available options are:

* `city` to define the city to search in,
* `start_price` and `end_price` to specify the price range,
* `day` to specify the age of required listings, as follows:
  * `1` for 1 day,
  * `2` for 3 days,
  * `3` for 5 days,
  * `4` for 10 days.
