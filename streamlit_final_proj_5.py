import streamlit as st
import requests
from requests.exceptions import RequestException
import time
from flask import Flask, request

# Настройка страницы
st.set_page_config(
    page_title="Кластеризация фильмов",
    page_icon="🎥",
    layout="centered"
)


API_URL = "http://localhost:6006" 
MAX_DESCRIPTION_LENGTH = 1000

@st.cache_resource(ttl=300)
def check_api_health():
    try:
        response = requests.get(f"{API_URL}/health")
        status = requests.get
        return response.status_code == 200
    except:
        return False

api_available = check_api_health()

if not api_available:
    st.error("⚠️ Сервис предсказания не отвечает. Проверьте, запущен ли сервер.")
else:
    st.success("✅ Сервер доступен")

st.title("Предсказание кластера заголовка")


example_descriptions = [
    
]

movie_description = st.text_area(
    "Введите описание статьи",
    value=st.session_state.get('last_input', ''),
    height=180,
    help=f"Максимум {MAX_DESCRIPTION_LENGTH} символов"
)


if st.button("🔍 Предсказать кластер", type="primary"):
    if movie_description.strip() and len(movie_description) <= MAX_DESCRIPTION_LENGTH:
        with st.spinner("Идет анализ..."):
            try:
                response = requests.post(
                    f"{API_URL}/predict",
                    json={"description": movie_description},
                    timeout=10
                )

                if response.status_code == 200:
                    result = response.json()
                    st.session_state['last_input'] = movie_description

                    st.markdown("---")
                    st.success(f"**Предсказанный кластер:** {result['cluster']} - *{result['cluster_name']}*")

                    col1, col2 = st.columns(2)
                    col1.write(f"**Уверенность:** {result.get('confidence', 0.7):.2%}")
                    col2.write(f"**Модель:** {result.get('model_used', 'неизвестно')}")

                    with st.expander("ℹ️ Подробнее", expanded=True):
                        st.write(f"**Описание:** {movie_description}")
                        st.write(f"**ID кластера:** {result['cluster']}")
                        st.write(f"**Название кластера:** {result['cluster_name']}")

                        if 'probabilities' in result and result['probabilities']:
                            st.subheader("Вероятности по кластерам:")
                            for cluster, prob in result['probabilities'].items():
                                st.progress(prob)
                                st.write(f"- {cluster}: {prob:.2%}")

                        if 'warning' in result:
                            st.warning(result['warning'])

                        if 'error' in result:
                            st.error(result['error'])

                else:
                    st.error(f"Ошибка API: {response.status_code} - {response.text}")

            except RequestException as e:
                st.error(f"❌ Ошибка соединения с сервером: {str(e)}")
    elif len(movie_description) > MAX_DESCRIPTION_LENGTH:
        st.warning(f"⚠️ Ограничение: максимум {MAX_DESCRIPTION_LENGTH} символов")
    else:
        pass


with st.expander("📌 Примеры описаний"):
    for i, example in enumerate(example_descriptions):
        if st.button(f"Пример {i+1}", key=f"ex_{i}"):
            st.session_state['last_input'] = example


with st.sidebar:
    st.header("🔧 Информация")
    if st.button("🔄 Проверить состояние API", use_container_width=True):
        with st.spinner("Проверяю..."):
            try:
                response = requests.get(f"{API_URL}/health")

                if response.status_code == 200:
                    health = response.json()
                    st.success("✅ API активен")
                    st.json(health)
                else:
                    st.error(f"❌ Ошибка: {response.status_code}")
            except RequestException as e:
                st.error(f"❌ Не удалось связаться с API: {str(e)}")
