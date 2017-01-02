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

        self.available = db_manage.getGenre()
        # self.log(str(self.available)+'@@@@@@@')
        db_manage.setUpdateFlag() ##@@##

    def start_requests(self):
        yield scrapy.Request('http://www.ooyyo.com/ooyyo-services/resources/indexpage/countryweburls', headers=self.HEADER, method="POST", body=json.dumps({"isNew": "0", "idPageType": "5", "idCountry": "1", "idLanguage": "47", "idDomain": "1", "idCurrency": "17"}), callback=self.getCountry)

    # get list country.
    def getCountry(self, response):
        temp = json.loads(response.body)
        for cn in temp:
            if temp[cn]["title"] in settings.AVAILABLE_COUNTRY:
                # self.log(temp[cn]["title"]+'@@@@@@@')                         
                # make request for getting car list
                request = scrapy.Request('http://www.ooyyo.com/ooyyo-services/resources/quicksearch/qselements', headers=self.HEADER, method="POST", body=json.dumps({"qsType": "advanced", "isNew": "0", "idCountry": str(cn), "idLanguage": "47", "idCurrency": "17", "idDomain": "1"}), callback=self.getCars, dont_filter=True)
                request.meta["country"] = [cn, temp[cn]["title"]]
                yield request


    # get car list.
    def getCars(self, response):
        country = response.meta["country"]
        cars = json.loads(response.body)["makes"]['black']

        for car in cars:
            car_name = car['name'].lower().strip()
            if car_name in self.available:
                # self.log(car['name']+'@@@@@@@@@@@@@@@@@')                         

                # make request for getting model list
                request = scrapy.Request('http://www.ooyyo.com/ooyyo-services/resources/quicksearch/qselements', headers=self.HEADER, method="POST", body=json.dumps({"qsType": "advanced", "isNew": "0", "idCountry": country[0], "idLanguage": "47", "idCurrency": "17", "idDomain": "1", "idMake": str(car["idMake"])}), callback=self.getModels, dont_filter=True)

                request.meta["country"] = country
                request.meta["cars"] = {'idMake':car["idMake"], 'make_name':car_name}
                yield request


    # get model list.
    def getModels(self, response):
        country = response.meta["country"]
        cars = response.meta["cars"]

        models = json.loads(response.body)["models"]['black']

        for model in models:
            model_name = model['name'].lower().strip()
            if model_name in self.available[cars['make_name']]:
                # self.log(model['name']+'@@@@@@@')                         

                # make request for getting search url
                request = scrapy.Request('http://www.ooyyo.com/ooyyo-services/resources/quicksearch/qselements', headers=self.HEADER, method="POST", body=json.dumps({"qsType": "advanced", "isNew": "0", "idCountry": country[0], "idLanguage": "47", "idCurrency": "17", "idDomain": "1", "idMake": str(cars['idMake']), "idModel": str(model["idModel"])}), callback=self.getSearchUrl, dont_filter=True)

                request.meta["country"] = country
                cars_ = cars.copy()
                cars_['model_name'] = model_name
                request.meta["cars"] = cars_
                
                yield request

    # get search url.
    def getSearchUrl(self, response):
        country = response.meta["country"]
        cars = response.meta["cars"]

        search_url = json.loads(response.body)["url"]

        request = scrapy.Request(self.domain + search_url, callback=self.getInfomation, dont_filter=False)
        # make request for getting data
        request.meta["country"] = country
        request.meta["cars"] = cars

        yield request
        
    # get list of cars.
    def getInfomation(self, response):
        country = response.meta["country"]
        cars = response.meta["cars"]
        nodes = response.xpath('//a[@class="car type8 _dcdtrgt"]')

        for node in nodes:
            try:
                car_id = node.xpath(".//img[@itemprop='image']/@data-record").extract()[0].strip() 
                year = int(node.xpath(".//span[@itemprop='releaseDate']/text()").extract()[0].strip())
                price_unit = node.xpath(".//span[@itemprop='priceCurrency']/@content").extract()[0].strip()
                price = float(node.xpath(".//span[@itemprop='price']/@content").extract()[0].strip()) 
                price = int(price * settings.CURRENCY_RATE[price_unit])
            except:
                raise
                continue

            # check constraints
            if price < 1000:
                continue

            year_filter = self.available[cars['make_name']][cars['model_name']]['year_filter']
            flag = False
            for f_item in year_filter:
                if f_item['from'] <= year and year <= f_item['to']:
                    flag = True
                    break
            if flag:                    
                item = {"country": country[1], "name": self.available[cars['make_name']]['alias'], 
                        "brand": self.available[cars['make_name']][cars['model_name']]['alias'], 
                        "year": year, "price": price, "car_id": car_id, "prev_price": price}
                self.log(str(item)+'#############')
                db_manage.save(item)

        # make request for the next page
        pagination = response.xpath("//div[@class='pagination type2']//div[contains(@class, 'pagin')]")
        if len(pagination) < 2:
            return

        href = pagination[1].xpath(".//a/@href").extract()[0].strip()

        if href == "javascript:void(0)":
            return

        request = scrapy.Request(self.domain + href, callback=self.getInfomation, dont_filter=False)
        # make request for getting data
        request.meta["country"] = country
        request.meta["cars"] = cars
        yield request
