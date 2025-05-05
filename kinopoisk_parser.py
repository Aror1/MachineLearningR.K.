import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import time
import random
from datetime import datetime

# Заголовки для имитации браузера
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Sec-Ch-Ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"macOS"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1'
}

def make_request(url, max_retries=3):
    """Выполняет запрос к сайту с повторными попытками"""
    for attempt in range(max_retries):
        try:
            time.sleep(random.uniform(2, 4))  # Увеличиваем задержку
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            # Проверяем на наличие капчи
            if 'captcha' in response.text.lower():
                print(f"Обнаружена капча на странице {url}")
                time.sleep(random.uniform(5, 10))  # Увеличенная задержка при капче
                continue
                
            return response
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе {url}: {e}")
            if attempt == max_retries - 1:
                raise
            time.sleep(random.uniform(3, 6))  # Увеличенная задержка между попытками
    return None

def parse_movie_page(url):
    """Парсит страницу отдельного фильма"""
    try:
        response = make_request(url)
        if not response:
            return None
        
        soup = bs(response.text, 'html.parser')
        
        # Получаем основную информацию
        title = soup.find('h1', class_='styles_title__3l3IW')
        if title is not None:
            title = title.text.strip()
        else:
            title = None
        
        # Получаем рейтинг
        rating = soup.find('span', class_='styles_rating__3yWnZ')
        rating = rating.text.strip() if rating else None
        
        # Получаем год
        year = soup.find('span', class_='styles_year__2o3Gq')
        year = year.text.strip() if year else None
        
        # Получаем описание
        description = soup.find('div', class_='styles_description__3W8ze')
        description = description.text.strip() if description else None
        
        # Получаем жанры
        genres = []
        genre_tags = soup.find_all('a', class_='styles_genre__1h8Zq')
        for genre in genre_tags:
            genres.append(genre.text.strip())
        
        # Получаем режиссера
        director = soup.find('a', class_='styles_director__2ZqGX')
        director = director.text.strip() if director else None
        
        # Получаем бюджет
        budget = soup.find('div', class_='styles_budget__2qGXZ')
        budget = budget.text.strip() if budget else None
        
        # Получаем сборы
        box_office = soup.find('div', class_='styles_boxOffice__2qGXZ')
        box_office = box_office.text.strip() if box_office else None
        
        return {
            'title': title,
            'rating': rating,
            'year': year,
            'description': description,
            'genres': ', '.join(genres),
            'director': director,
            'budget': budget,
            'box_office': box_office,
            'url': url
        }
    except Exception as e:
        print(f"Ошибка при парсинге страницы {url}: {e}")
        return None

def main():
    # Список для хранения данных о фильмах
    movies_data = []
    
    # URL страницы с топ-250 фильмов
    base_url = 'https://www.kinopoisk.ru/lists/top250/'
    
    try:
        # Получаем список фильмов
        response = make_request(base_url)
        if not response:
            return
        
        soup = bs(response.text, 'html.parser')
        
        # Сохраняем HTML для отладки
        with open('kinopoisk_response.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
            
        movie_links = soup.find_all('a', class_='styles_movie__3lNvh')
        
        movie_links = movie_links[:250]
        
        print(f"Найдено {len(movie_links)} фильмов")
        
        # Парсим каждый фильм
        for i, link in enumerate(movie_links, 1):
            movie_url = 'https://www.kinopoisk.ru' + str(link.get('href'))
            print(f"Обработка фильма {i}/250: {movie_url}")
            
            movie_data = parse_movie_page(movie_url)
            if movie_data:
                movies_data.append(movie_data)
            
            # Добавляем случайную задержку между запросами
            time.sleep(random.uniform(3, 5))
        
        # Создаем DataFrame и сохраняем в CSV
        if movies_data:
            df = pd.DataFrame(movies_data)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'kinopoisk_top250_{timestamp}.csv'
            df.to_csv(filename, index=False, encoding='utf-8')
            print(f"\nДанные сохранены в файл: {filename}")
            
            # Выводим статистику
            print("\nСтатистика:")
            print(f"Всего обработано фильмов: {len(movies_data)}")
            print("\nТоп-5 фильмов по рейтингу:")
            print(df.nlargest(5, 'rating')[['title', 'rating', 'year']])
        else:
            print("\nНе удалось получить данные о фильмах")
        
    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    main() 