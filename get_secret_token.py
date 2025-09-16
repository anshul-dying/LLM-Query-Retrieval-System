import requests
from bs4 import BeautifulSoup

url = input("Enter the URL: ")

response = requests.get(url)

soup = BeautifulSoup(response.text, 'html.parser')
token_element = soup.find(id='token')

print(token_element.text)
