import scrapy
import json
from scraper import settings
from scraper import db_manage

class CarPriceSpider(scrapy.Spider):
    name = "carprice"
    domain = "http://www.ooyyo.com"

    def __init__(self):
        self.HEADER = {
                          "Accept": "application/json, text/javascript, */*; q=0.01",
                          "Accept-Encoding":"gzip, deflate",
                          "Accept-Language":"en-US,en;q=0.8",
                          "Content-Type":"application/json",
                          "Cookie":"JSESSIONID=5fsOdVsRlZsuiIoIEQ6HOMBs.slave1:server-one;                                        JSESSIONID=wlkuxJtGDVQ3hjZWjbkSEiwb.slave2:server-one;                           _ga=GA1.2.1565066221.1481247240; user_setting_v4=idLanguage%3A47%2CidCountry%3A1%2CidCurrency%3A3",
                          "Host":"www.ooyyo.com",
                          "Origin": "http://www.ooyyo.com",
                          "Referer": "http://www.ooyyo.com",
                          "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)                           Chrome/55.0.2883.87 Safari/537.36",
                          "X-Requested-With": "XMLHttpRequest"}

        self.db = db_manage.getDB()
        self.available = db_manage.getGenre(self.db)
        db_manage.setUpdateFlag(self.db)

    def start_requests(self):
	urls = [
	    'http://www.ooyyo.com/ooyyo-services/resources/indexpage/countryweburls'
	]

        yield scrapy.Request('http://www.ooyyo.com/ooyyo-services/resources/indexpage/countryweburls', headers=self.HEADER, method="POST", body=json.dumps({"isNew": "0", "idPageType": "5", "idCountry": "1", "idLanguage": "47", "idDomain": "1", "idCurrency": "3"}), callback=self.getCountry)

    # get list country.
    def getCountry(self, response):
        temp = json.loads(response.body)
        for cn in temp:
            if temp[cn]["title"] in settings.AVAILABLE_COUNTRY:
                
                # make request for getting car list
                request = scrapy.Request('http://www.ooyyo.com/ooyyo-services/resources/quicksearch/qselements', headers=self.HEADER, method="POST", body=json.dumps({"qsType": "advanced", "isNew": "0", "idCountry": str(cn), "idLanguage": "47", "idCurrency": "17", "idDomain": "1"}), callback=self.getCars, dont_filter=True)
                request.meta["country"] = [cn, temp[cn]["title"]]
                yield request

    # get car list.
    def getCars(self, response):
        country = response.meta["country"]

        cars = json.loads(response.body)["makes"]['black']

        for car in cars:
            available_car = [item for item in self.available if item.lower()==car["name"].lower()]
            if len(available_car) > 0:

                # make request for getting model list
                request = scrapy.Request('http://www.ooyyo.com/ooyyo-services/resources/quicksearch/qselements', headers=self.HEADER, method="POST", body=json.dumps({"qsType": "advanced", "isNew": "0", "idCountry": country[0], "idLanguage": "47", "idCurrency": "17", "idDomain": "1", "idMake": str(car["idMake"])}), callback=self.getModels, dont_filter=True)

                request.meta["country"] = country
                request.meta["cars"] = [car["idMake"], available_car[0]]

                yield request

    # get model list.
    def getModels(self, response):
        country = response.meta["country"]
        cars = response.meta["cars"]

        models = json.loads(response.body)["models"]['black']

        for model in models:
            available_model = [item for item in self.available[cars[1]] if model["name"].lower() == item.lower()]
            if len(available_model) > 0:

                # make request for getting search url
                request = scrapy.Request('http://www.ooyyo.com/ooyyo-services/resources/quicksearch/qselements', headers=self.HEADER, method="POST", body=json.dumps({"qsType": "advanced", "isNew": "0", "idCountry": country[0], "idLanguage": "47", "idCurrency": "17", "idDomain": "1", "idMake": str(cars[0]), "idModel": str(model["idModel"])}), callback=self.getSearchUrl, dont_filter=True)

                request.meta["country"] = country
                request.meta["cars"] = cars
                request.meta["models"] = [model["idModel"], available_model[0], self.available[cars[1]][available_model[0]]]
                
                yield request

    # get search url.
    def getSearchUrl(self, response):
        country = response.meta["country"]
        cars = response.meta["cars"]
        models = response.meta["models"]

        search_url = json.loads(response.body)["url"]

        request = scrapy.Request(self.domain + search_url, callback=self.getInfomation, dont_filter=False)
        # make request for getting data
        request.meta["country"] = country
        request.meta["cars"] = cars
        request.meta["models"] = models

        print search_url
        yield request
        
    # get list of cars.
    def getInfomation(self, response):
        country = response.meta["country"]
        cars = response.meta["cars"]
        models = response.meta["models"]

        nodes = response.xpath("//div[@class='beta']")

        for node in nodes:
            try:
                year = int(node.xpath(".//span[@itemprop='releaseDate']/text()").extract()[0].strip())
                price = float(node.xpath(".//span[@itemprop='price']/@content").extract()[0].strip()) 
            except:
                continue;

            item = {"country": country[1], "name": cars[1], "model": models[2], "year": year, "price": price}
            db_manage.save(self.db, item)

        # make request for the next page
        pagination = response.xpath("//div[@class='pagination type2']//div[contains(@class, 'pagin')]")
        if len(pagination) < 2:
            return;

        href = pagination[1].xpath(".//a/@href").extract()[0].strip()

        if href == "javascript:void(0)":
            return;

        request = scrapy.Request(self.domain + href, callback=self.getInfomation, dont_filter=False)
        # make request for getting data
        request.meta["country"] = country
        request.meta["cars"] = cars
        request.meta["models"] = models
        yield request

