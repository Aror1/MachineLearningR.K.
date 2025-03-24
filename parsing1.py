
from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
### Получение информаций
# GET - запрос

url = 'https://habr.com/ru/all/' 
page = requests.get(url)

page.status_code


soup = bs(page.text, 'html.parser')


bs(page.text, 'html.parser')


result_list = {'title': [], 'namecompany': [], 'description': [], 'rating': [], 'field': [], 'date': [], 'textpub': []}
pagenum = 1
for i in range(10):
  
    url = 'https://habr.com/ru/articles/page' + str(pagenum) + '/' # переход на ссылуку с определённым номером сраницы
    page = requests.get(url)
    soup = bs(page.text, 'html.parser')
    titles = soup.find_all('h2', class_='tm-title tm-title_h2')# получаем заголовки всех статей на этой странице
    
    for i in titles: 
        # переход на страницу статьи
        url = 'https://habr.com' + str(i.a.get('href')) 
        page = requests.get(url)
        soup = bs(page.text, 'html.parser')
        
        name_company = soup.find('a', class_='tm-company-snippet__title')# получаем название компаний
        desc_company = soup.find('div', class_='tm-company-snippet__description')# получаем описание компаний
        
        if (name_company is not None): #если на странице присутсвует компания
        
            result_list['title'].append(i.text) # записываем название статьи
            result_list['namecompany'].append(name_company.text) # записываем название компании
            result_list['description'].append(desc_company.text) # записываем описание компании
            
            datepub = soup.find('span', class_='tm-article-datetime-published') # находим дату публикаций
            result_list['date'].append(datepub.time['datetime'][0: 10]) # записываем дату публикаций
            
            # текст статьи
            try:
                textpub = soup.find('div', class_='article-formatted-body article-formatted-body article-formatted-body_version-2').get_text()
                textpub = textpub.replace('\n', ' ').replace('\t', ' ').replace('\xa0', ' ').replace('\u200e', ' ').replace('\r', ' ')
            except:
                textpub = soup.find('div', class_='article-formatted-body article-formatted-body article-formatted-body_version-1').get_text()
                textpub = textpub.replace('\n', ' ').replace('\t', ' ').replace('\xa0', ' ').replace('\u200e', ' ').replace('\r', ' ')
            result_list['textpub'].append(textpub)
            
            # переход на страницу компании
            url = 'https://habr.com' + str(name_company.get('href'))
            page = requests.get(url)
            soup = bs(page.text, 'html.parser')
            
            #записываем рейтинг
            rating = soup.find('span', class_='tm-votes-lever__score-counter tm-votes-lever__score-counter tm-votes-lever__score-counter_rating')
            if(rating is None):
                result_list['rating'].append('0')
            else:
                result_list['rating'].append((rating.text).strip())
               
             #записываем отрасли компаний
            fieldtext = ""
            fields = soup.find_all('a', 'tm-company-profile__categories-text')
            for field in fields:
                fieldtext = fieldtext + ((field.text).strip()) + ", "
            if (fields is None):
                result_list['field'].append(None)
            else:
                result_list['field'].append(fieldtext[0:-2])
            
    pagenum += 1

result_list
print("Количество нулевых значений в: ")
for i in result_list:
    print( i + " - " + str(result_list[i].count(None)))

### Сохранение данных
file_name = 'habr.csv'
df = pd.DataFrame(data=result_list)
df.to_csv(file_name)
df.head()
df.info()
