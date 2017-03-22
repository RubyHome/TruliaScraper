import scrapy, time
import json
# from truliaSpider.items import TruliaspiderItem


class truliascraperSpider(scrapy.Spider):
    name = 'truliaSpider'
    url_template = "https://www.trulia.com/CA/Manhattan_Beach/%s/"
    cnt = 0 
    item = {}
    def __init__(self):
        self.zipcode = "90266"
    def start_requests(self):
        url = self.url_template % (self.zipcode)
        print url
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):    
        urls = response.xpath('.//div[@class="containerFluid"]//div[@class="smlCol12 lrgCol8 ptm cardContainer positionRelative"]//div[@class="card backgroundBasic"]//a/@href').extract()
        for url in urls:      
            request = scrapy.Request(response.urljoin(url) , callback=self.parse_page)      
            yield request
            # break 
        nextpage = response.xpath('.//div[@class="paginationContainer plm mtl ptl mbm"]//a[@aria-label="Next"]/@href').extract_first() 
        request1 = scrapy.Request(response.urljoin(nextpage))
        yield request1
    def parse_page(self , response):
        
        URL = response.url
        send_key = str((URL.split("/")[4]).split("-")[0])
        send_url = "https://www.trulia.com/_service/TruliaLeadForm/form/property/"+ send_key + ".json?searchType=for%20sale&ab=796:;864:864b&userId=170321nml2c731pdjmrneqmir3k0pqj5&userIdType=truliaLifetimeId&adType=SSA&logged_in_user_id=0&source=www&lgi=undefined&stateCode=CA"
        print("--------------------------", send_url)
        # state = response.xpath('//li[@id="region-state"]/a/text()').extract_first()
        addr1 = response.xpath('.//div[@id="propertyDetails"]//span[@class="headingDoubleSuper h2 typeWeightNormal mvn ptn"]/text()').extract_first()
        addr2 = response.xpath('.//div[@id="propertyDetails"]//span[@class="headlineDoubleSub typeWeightNormal typeLowlight man"]/text()').extract_first()
        self.item["Site_Url"] = response.url
        self.item["Address"] = addr1.strip() + ", " + addr2.strip()
        details = response.xpath('.//div[@id="propertyDetails"]//ul[@class="listBulleted listingDetails mrn mtm list3cols"]//li')
        pro_arr = ["Type", "Bed", "Bath", "Square", "Price/Square", "Lot Size", "Built Year", "Info"]
        for detail in details:
            data = detail.xpath('./text()').extract_first()
            if "Bed" in data : 
                self.item["Bed"] = data
            if "sqft" in data and "size" not in data and "$" not in data:
                self.item["Square"] = data
            if "/sqft" in data : 
                self.item["Price_Square"] = data
            if "size" in data : 
                self.item["Lot_Size"] = data
            if "Build" in data : 
                self.item["Built_Year"] = data
            if "Days" in data : 
                self.item["Info"] = data
            if "Bath" in data : 
                self.item["Bath"] = data   
        
        request2 = scrapy.Request( send_url, callback = self.getJson)
        
        yield request2

        # return self.item
        
        # yield self.item
        # with open("test.html", 'wb') as f:
        #     f.write(response.body)
       
    def manual(self,var_str):
        if var_str is None:
            return ""
        return var_str
    def getJson(self, response):
        # print("+++++++++++++++++++++++++++++",response.body)
        fetch_data = json.loads(response.body)
        realtors_data = fetch_data['contact_recipients']
        description = ""
        for realtor in realtors_data : 
            description = description + " || Name : " + realtor["display_name"] + ", " + "Phone : (" + str(realtor["phone"]["areacode"]) + ") " + str(realtor["phone"]["prefix"]) + "-" + str(realtor["phone"]["number"])      
        self.item["Realtors"] = description
        return self.item

        # response.xpath('.//div[@class="normalPdpContent"]//div[@class="line asideFloaterContainer"]//div[@class="col cols16"]//div[@class="box boxHighlight pal mvm"]').extract_first()
# https://www.trulia.com/_service/TruliaLeadForm/form/property/3260829621.json?searchType=for%20sale&ab=796:;864:864b&userId=170321nml2c731pdjmrneqmir3k0pqj5&userIdType=truliaLifetimeId&adType=SSA&logged_in_user_id=0&source=www&lgi=undefined&stateCode=CA