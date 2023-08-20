import re
import json


class ProductPage:
    def __init__(self, parser):
        self.parser = parser

    def get_data(self):
        name = self.get_product_name()
        asin = self.get_asin()
        brand = self.get_brand_name()
        price = self.get_product_price()
        images = self.get_product_images()
        average_rating = self.get_product_rating()
        product_review_count = self.get_product_review_count()
        short_description = self.get_product_short_description()
        data = {
            "name": name,
            "asin": asin,
            "brand": brand,
            "price": price,
            "images": images,
            "average_rating": average_rating,
            "review_count": product_review_count,
            "short_description": short_description,
        }
        return data

    def get_product_name(self):
        xpath_list = (
            "//h1[@id='title']/span/text()",
            "//div[@class='feature_Title celwidget']//h1/span/text()",
            '//span[@id="productTitle"]/text()',
            "//meta[@name='title']/@content",
        )
        name = extract_content(self.parser, xpath_list)
        return name

    def get_asin(self):
        text = self.parser.xpath(
            "//script[contains(text(), 'parentAsin') and contains(text(), 'currentAsin')]/text()"
        )
        if text:
            regex_asin = re.findall('currentAsin" : "(.*)", "parentAsin', text[0])
            if regex_asin:
                current_asin = regex_asin[0].strip()
                if current_asin != "":
                    return current_asin

        xpath_list = ["//link[@rel='canonical']/@href"]
        asin = extract_content(self.parser, xpath_list)
        if asin:
            asin = asin.split("/")[-1]
            return asin
        script_js = self.parser.xpath(
            '//script[contains(text(), "window.INITIAL_STATE")]/text()'
        )
        if script_js:
            regex_asin = re.findall('selectedAsin":"(.*)","asinInUrl', script_js[0])
            if regex_asin:
                current_asin = regex_asin[0].strip()
                if current_asin != "":
                    return current_asin
        return None

    def get_brand_name(self):
        """Get product brand name"""
        xpath_list = [
            "//div[@data-feature-name='bylineInfo']//a[contains(@id,'bylineInfo')]//text()",
            "//li[contains(b/text(),'Brand')]/text()",
            "//th[contains(text(),'Brand')]/following-sibling::td//text()",
            "//a[contains(@id, 'bylineInfo')]/text()",
            "//div[contains(@id,'brandBar')]//img/@alt",
            "//a[@id='brand']/text()",
            "//div/@data-brand",
            "//th[contains(text(), 'Brand')]/following-sibling::td/text()",
            "//li/b[contains(text(),'Brand')]/parent::li/text()",
            "//div[contains(@id, 'bylineInfoUS')]/div/text()",
            '//div[@id="amznStoresBylineLogoTextContainer"]/a/text()',
            '//div[@cel_widget_id="ByLine"]//a/text()',
        ]
        brand = extract_content(self.parser, xpath_list)
        if brand:
            if brand.startswith("by"):
                brand = brand.replace("by ", "").strip()
            elif brand.startswith("Visit"):
                brand = brand.replace("Visit the ", "").replace(" Store", "").strip()
            elif brand.startswith("Brand"):
                brand = brand.replace("Brand: ", "").strip()
        return brand

    def get_product_price(self):
        xpath_list = [
            "//span[@id='priceblock_ourprice']/text()",
            "//span[@id='priceblock_ourprice']//span/text()",
            "//span[contains(@id,'priceblock_saleprice')]//text()",
            "//span[contains(@id, 'priceblock_snsprice_Based')]/span[1]/text()",
            "//span[contains(@id,'priceblock_pospromoprice')]/text()",
            "//span[contains(@id,'priceblock_usedprice')]//text()",
            "//span[@id='priceblock_dealprice']//text()",
            "//span[contains(@id,'price_inside_buybox')]//text()",
            "//div[@id='buyNewSection']//span[contains(@class, 'price')]/text()",
            "//div[@id='usedBuySection']//span[contains(@class,'offer-price')]//text()",
            "//td[contains(text(), 'Kindle Price')]/following-sibling::td/text()",
            "//td[contains(text(), 'Kindle Price')]/following-sibling::td/span/text()",
            "//td[contains(text(), 'Buy Now Price')]/following-sibling::td/text()",
            "//td[contains(text(), 'Buy Now Price')]/following-sibling::td/span/text()",
            "//span[@id='newBuyBoxPrice']/text()",
            (
                "//div[contains(@id, 'corePriceDisplay')]/parent::div[@style='' or not(@style='display:none;')]"
                "//div[span[contains(@class, 'savingPriceOverride')]]//span[contains(@class, 'priceToPay')]"
                "/span[@class='a-offscreen']/text()"
            ),
            (
                "//div[contains(@id, 'corePriceDisplay')]/parent::div[@style='' or not(@style='display:none;')]"
                "//span[contains(@class, 'priceToPay')]/span[@class='a-offscreen']/text()"
            ),
            '//div[contains(@class, "goudaBuyBox")]//span[contains(@class, "price")]/text()',
            '//div[@id="mediaTab_content_landing"]//span[contains(@class, "price header-price")]/text()',
            '//div[@cel_widget_id="PriceBlock"]//span[contains(@class, "price-block-our-price")]/text()',
            (
                '//div[div[@id="desktop_qualifiedBuyBox"]]//div[@id="apex_offerDisplay_desktop"]'
                '//span[contains(@class, "aok-align-center")]//span[@class="a-offscreen"]//text()'
            ),
        ]
        price = extract_content(self.parser, xpath_list)
        return price

    def get_product_images(self):
        """Fetch product images as list of urls"""
        images = []
        image_data = {}

        raw_image_list = [
            re.sub("._.*_", "", i)
            for i in self.parser.xpath(
                '//div[@data-feature-name="imageBlock"]//li//img/@src | //img[contains(@class, "coverImage")]/@src'
            )
        ]

        if raw_image_list:
            images = [
                i
                for i in raw_image_list
                if not ("transparent-pixel.gif" in i or "data:image" in i)
            ]
            images = ", ".join(images) if images else None
            return images

        images_json = self.parser.xpath(
            '//script[contains(text(), "var data") and contains(text(), "colorImages")]/text()'
        )
        for i in images_json:
            raw_image_list_2 = re.findall("'colorImages': ({.*}), 'colorToAsin", i)
            if not raw_image_list_2:
                continue
            try:
                image_data = json.loads(raw_image_list_2[0].replace("'", '"'))
            except Exception:
                try:
                    image_data = json.loads(raw_image_list_2[0])
                except Exception:
                    image_data = {}
        image_initial_data = image_data.get("initial", [])
        if image_initial_data:
            for i in image_initial_data:
                if i.get("hiRes", None):
                    images.append(i["hiRes"])
                else:
                    images.append(i["large"])
        images = ", ".join(images) if images else None
        return images

    def get_product_rating(self):
        xpath_list = [
            "//div[@id='averageCustomerReviews']//span[@id='acrPopover']//@title",
            "//span[@data-hook='rating-out-of-text']/text()",
        ]
        avg_rating = extract_content(self.parser, xpath_list, " | ")
        if avg_rating and " | " in avg_rating:
            avg_rating = avg_rating.split(" | ")[0]
        return avg_rating

    def get_product_review_count(self):
        xpath_list = [
            "//span[contains(@id,'CustomerReviewText')]//text()",
            "//div[@data-hook='total-review-count']/span/text()",
        ]
        total_reviews = extract_content(self.parser, xpath_list)
        if total_reviews:
            total_reviews = total_reviews.split()[0].strip()
        return total_reviews

    def get_product_short_description(self):
        xpath_list = [
            '//div[@id="feature-bullets"]//li/span[contains(@class, "a-list-item")]/text()',
            '//div[@id="feature-bullets"]//li[not(contains(@id, "replacementPartsFitmentBullet"))]/span[contains(@class, "a-list-item")]/text()',  # noqa
            "//div[@id='feature-bullets']//span[@class='a-list-item']/text()",
        ]
        short_description = extract_content(self.parser, xpath_list)
        return short_description


def extract_content(parser, xpath_list, separator=""):
    """Parses content from list of xpaths, cleans and returns data

    Args:
     parser: html parser object
     xpath_list: list of xpaths to fetch data
     separator: separator used to join data after splitting. Used to remove extra white space
    """
    content = ""
    for xpath in xpath_list:
        raw_data = parser.xpath(xpath)
        if not raw_data:
            continue
        content = " ".join(separator.join(raw_data).split()).strip()
        if content:
            break
    return content
