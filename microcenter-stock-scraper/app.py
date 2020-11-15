from bs4 import BeautifulSoup
import requests
import pandas as pd
from fake_useragent import UserAgent
import boto3
import json

class ProductStockResult:
  def __init__(self, name, isInStock):
    self.name = name
    self.isInStock = isInStock
  def toJson(self):
    return '{"name" : "' + self.name + '", "isInStock": "' + str(self.isInStock) + '"}'
    
class ProductToSearch:
  def __init__(self, name, url):
    self.name = name
    self.url = url


def lambda_handler(event, context):
    ua = UserAgent()
    sns = boto3.client('sns')
    header = {'User-Agent':str(ua.chrome)}

    products = [
        ProductToSearch("AMD Ryzen 7 5800X","https://www.microcenter.com/product/630284/amd-ryzen-7-5800x-vermeer-38ghz-8-core-am4-boxed-processor?storeid=101"),
        ProductToSearch("AMD Ryzen 5 5600X","https://www.microcenter.com/product/630285/amd-ryzen-5-5600x-vermeer-37ghz-6-core-am4-boxed-processor-with-wraith-stealth-cooler?storeid=101")
    ]

    res=[]
    for product in products:
        isInStock = False
        req = requests.get(product.url, header)
        soup = BeautifulSoup(req.content, 'html.parser')
        inventoryCountSpan=soup.find("span", class_="inventoryCnt")
    
        if inventoryCountSpan.getText() != "Sold Out":
            isInStock = False
            sns.publish(
            TopicArn='arn:aws:sns:us-west-1:640172007277:ryzen-in-stock',    
            Message=f'{product.name} in stock at Tustin Microcenter! {product.url}')
        res.append(ProductStockResult(product.name, isInStock).toJson())
        
    return res
