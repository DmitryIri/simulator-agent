
import streamlit as st
import json
import random
from datetime import datetime

# --- Загружаем сценарии из файла ---
with open("scenarios.json", "r", encoding="utf-8") as f:
    scenarios = json.load(f)

# --- Заголовок ---
st.set_page_config(page_title="MP-Agent", page_icon="💊")
st.title("🧪 Тренажёр общения: Медпредставитель и Врач")

# --- Выбор роли ---
if "role" not in st.session_state:
    st.session_state.role = None

if st.session_state.role is None:
    role = st.radio("Выберите вашу роль:", ["Медпредставитель", "Врач", "Тренер"])
    if st.button("Продолжить"):
        st.session_state.role = role
        st.experimental_rerun()
    st.stop()

st.info(f"Вы вошли как **{st.session_state.role}**")

# --- Выбор сценария и стиля врача ---
scenario_titles = [s["title"] for s in scenarios]
col1, col2 = st.columns(2)
with col1:
    scenario_choice = st.selectbox("Выберите сценарий", ["Случайный"] + scenario_titles)
with col2:
    style_choice = st.radio("Стиль врача", ["Нейтральный", "Доброжелательный", "Скептик"])

# --- Получаем выбранный сценарий ---
if scenario_choice == "Случайный":
    scenario = random.choice(scenarios)
else:
    scenario = next(s for s in scenarios if s["title"] == scenario_choice)

# --- Стейт ---
if "step" not in st.session_state:
    st.session_state.step = 0
    st.session_state.history = []
    st.session_state.log = {
        "scenario_id": scenario["id"],
        "style": style_choice,
        "role": st.session_state.role,
        "dialog": [],
        "timestamp": datetime.now().isoformat()
    }

# --- Выводим чат-историю ---
st.subheader("💬 Диалог")
for entry in st.session_state.history:
    with st.chat_message(entry["role"]):
        st.markdown(entry["text"])

# --- Диалог ---
if st.session_state.step < len(scenario["steps"]):
    step = scenario["steps"][st.session_state.step]
    style = scenario["style_variants"][style_choice]
    doctor_text = f"{style['prefix']}{step['text']}{style['suffix']}"

    with st.chat_message("Врач"):
        st.markdown(doctor_text)
    st.session_state.history.append({"role": "Врач", "text": doctor_text})
    st.session_state.log["dialog"].append({"role": "Врач", "text": doctor_text})

    user_input = st.chat_input("Ваш ответ:")
    if user_input:
        st.session_state.history.append({"role": "МП", "text": user_input})
        st.session_state.log["dialog"].append({"role": "МП", "text": user_input})
        st.session_state.step += 1
        st.experimental_rerun()

# --- Обратная связь от тренера + лог сессии ---
else:
    st.success("Диалог завершён ✅")

    # Кнопка для скачивания JSON-лога
    log_json = json.dumps(st.session_state.log, ensure_ascii=False, indent=2)
    st.download_button(
        label="📥 Скачать диалог в формате JSON",
        data=log_json,
        file_name="session_log.json",
        mime="application/json"
    )

    if st.session_state.role == "Тренер":
        with st.expander("📊 Обратная связь от тренера"):
            st.markdown("""
**1. Аргументация:** 4/5  
Хорошо раскрыты преимущества, но не были указаны клинические данные.

**2. Контакт с врачом:** 5/5  
Диалог уважительный, задан уточняющий вопрос.

**3. Логика и структура:** 4/5  
Последовательность соблюдена, но не было резюмирующего вывода.

**💬 Рекомендация:**  
Добавьте финальный вопрос типа: _Могу ли я предложить Проспекту для таких пациентов?_

**⭐ Итог:** 4.3 / 5
            """)
