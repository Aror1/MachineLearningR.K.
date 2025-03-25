import requests
from bs4 import BeautifulSoup
import pandas as pd



# URL страницы IMDb Top 250
url = "https://ru.wikipedia.org/wiki/250_лучших_фильмов_по_версии_IMDb"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers)
if response.status_code != 200:
    print(f"{response.status_code}")
    exit()

soup = BeautifulSoup(response.text, "html.parser")
movies_inf = soup.find_all("tr")[1:]  # Пропускаем заголовок таблицы

movies_data = []
for row in movies_inf:
    cells = row.find_all("td")
    if len(cells) >= 5:  # Проверяем, что есть все необходимые ячейки
        movie = {
            'Место': cells[0].text.strip(),
            'Название': cells[1].text.strip(),
            'Год': cells[2].text.strip(),
            'Режиссёр': cells[3].text.strip(),
            'Рейтинг': cells[4].text.strip()
        }
        movies_data.append(movie)

# Создаем DataFrame
df = pd.DataFrame(movies_data)

# Устанавливаем Место как индекс
df.set_index('Место', inplace=True)

# Настраиваем отображение
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

# Выводим красивую таблицу
print("\nТоп-250 фильмов по версии IMDb:")
print("=" * 100)
print(df)


# [{1,2,3,4,5}, {1,2,3,4,5}, {1,2,3,4,5}]



