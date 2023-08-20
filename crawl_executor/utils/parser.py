import re
from lxml import html
from crawl_executor.utils.data_extractors.amazon.product import ProductPage


class Parser:
    def html_parser(self, response_text: str):
        """Removes unwanted characters, css and scripts and creates parser object

        Args:
         response_text: Response text as string

        Returns:
         parser_object: html parser object used to extract data
        """
        cleaned_response = response_text.replace("\0", "")
        cleaned_response = cleaned_response.strip().replace("\x00", "")
        cleaned_response = " ".join(cleaned_response.split())
        cleaned_response = re.sub(r"(?s)<(script).*?</\1>", "", cleaned_response)
        cleaned_response = re.sub(r"(?s)<(style).*?</\1>", "", cleaned_response)

        parser_object = html.fromstring(cleaned_response)
        return parser_object


class Amazon:
    def get_product_data(self, response_text: str):
        parser_object = Parser().html_parser(response_text=response_text)
        amazon_parser = ProductPage(parser=parser_object)
        data = amazon_parser.get_data()
        return data


parser_classes = {"amazon": Amazon}
