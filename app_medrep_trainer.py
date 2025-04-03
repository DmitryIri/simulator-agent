
import streamlit as st
import json

# Загрузка сценариев
@st.cache_data
def load_scenarios(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)["scenarios"]

# Функция поиска нужного сценария
def find_scenario(scenarios, objection, style):
    for item in scenarios:
        if item["objection"] == objection and item["style"] == style:
            return item
    return None

# Загружаем данные
scenarios = load_scenarios("scenarios_medrep_20of20.json")

# Заголовок
st.title("🎯 Тренажёр для медицинских представителей")

# Выбор параметров
objection_options = sorted(list(set(s["objection"] for s in scenarios)))
style_options = ["нейтральный", "доброжелательный", "скептик", "раздражённый"]

selected_objection = st.selectbox("Выберите возражение врача", objection_options)
selected_style = st.selectbox("Выберите стиль врача", style_options)

# Поиск сценария
scenario = find_scenario(scenarios, selected_objection, selected_style)

if scenario:
    st.subheader("🩺 Реплика врача:")
    st.markdown(f"> {scenario['doctor']}")

    st.subheader("💬 Выберите ответ:")
    for i, ans in enumerate(scenario["answers"], 1):
        st.button(f"Ответ {i}: {ans}")
else:
    st.warning("Сценарий не найден.")
