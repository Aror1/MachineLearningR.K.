import polars as pl
import spacy
import gc
import pandas as pd

# Загружаем модель один раз с максимальными оптимизациями
nlp = spacy.load("ru_core_news_sm", disable=["parser", "ner", "textcat", "attribute_ruler"])
nlp.max_length = 3000000  # Увеличиваем лимит для больших текстов

# Стоп-слова как set для быстрого поиска
russian_stopwords = set(nlp.Defaults.stop_words)

def tokenize_single_text(text):
    """Токенизация одного текста"""
    if text is None or text == "" or pd.isna(text):
        return ""
    
    try:
        doc = nlp(str(text))
        tokens = []
        for token in doc:
            lemma = token.lemma_
            if (len(lemma) > 1 and 
                lemma not in russian_stopwords and 
                not token.is_punct and 
                not token.is_space and
                token.is_alpha):
                tokens.append(lemma)
        
        return " ".join(tokens)
    except Exception:
        return ""

def tokenize_batch_ultra_fast(texts):
    """Максимально быстрая токенизация с лемматизацией"""
    processed = []
    
    # Предобработка текстов - обработка None и пустых значений
    cleaned_texts = []
    for text in texts:
        if text is None or text == "" or pd.isna(text):
            cleaned_texts.append("")  # Заменяем пустые значения на пустую строку
        else:
            cleaned_texts.append(str(text))  # Приводим к строке на всякий случай
    
    print(f"Обрабатываем {len(cleaned_texts)} текстов...")
    
    # Оптимальные параметры для максимальной скорости
    try:
        for i, doc in enumerate(nlp.pipe(cleaned_texts, batch_size=1000, n_process=-1, disable=["tagger"])):
            # Обработка пустых документов
            if not doc.text.strip():
                processed.append("")
                continue
                
            # Быстрая фильтрация с предварительной проверкой
            tokens = []
            for token in doc:
                lemma = token.lemma_
                # Объединяем все проверки в одну для скорости
                if (len(lemma) > 1 and 
                    lemma not in russian_stopwords and 
                    not token.is_punct and 
                    not token.is_space and
                    token.is_alpha):
                    tokens.append(lemma)
            
            processed.append(" ".join(tokens))
            
            # Периодическая очистка памяти и прогресс
            if (i + 1) % 1000 == 0:
                print(f"Обработано: {i + 1}/{len(cleaned_texts)}")
                gc.collect()
                
    except Exception as e:
        print(f"Ошибка при обработке: {e}")
        # В случае ошибки заполняем оставшиеся позиции пустыми строками
        while len(processed) < len(cleaned_texts):
            processed.append("")
    
    print(f"Токенизация завершена. Обработано: {len(processed)} из {len(texts)}")
    
    # Проверяем соответствие длин
    if len(processed) != len(texts):
        print(f"ВНИМАНИЕ: Несоответствие длин! Входных текстов: {len(texts)}, обработанных: {len(processed)}")
        # Дополняем до нужной длины пустыми строками
        while len(processed) < len(texts):
            processed.append("")
        # Или обрезаем лишние
        processed = processed[:len(texts)]
    
    return processed

# Основной код - используем Polars для максимальной скорости
print("Запуск быстрой токенизации...")

# Вариант 1: Через map_elements (рекомендуемый для Polars)
df_clean = df_clean.with_columns([
    pl.col("full_text")
    .map_elements(
        lambda x: tokenize_single_text(x) if x is not None else "", 
        return_dtype=pl.Utf8
    )
    .alias("text_tokenize")
])

print("Результат:")
print(df_clean.columns)
print(df_clean["text_tokenize"].head(5))