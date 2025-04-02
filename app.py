
import streamlit as st
import json
import random
import os
from datetime import datetime
from pathlib import Path

# === Загрузка сценариев ===
with open("scenarios.json", "r", encoding="utf-8") as f:
    scenarios = json.load(f)

# === Настройки страницы ===
st.set_page_config(page_title="MP-Agent", page_icon="💊")
st.title("🧪 Тренажёр общения: Медпредставитель и Врач")

# === Выбор роли и имени ===
if "role" not in st.session_state:
    st.session_state.role = None
if "user_name" not in st.session_state:
    st.session_state.user_name = ""

if st.session_state.role is None:
    role = st.radio("Выберите вашу роль:", ["Медпредставитель", "Врач", "Тренер"])
    name = st.text_input("Введите ваше имя:")
    if st.button("Продолжить"):
        if name.strip() == "":
            st.warning("Пожалуйста, введите имя.")
        else:
            st.session_state.role = role
            st.session_state.user_name = name.strip()
            st.rerun()
    st.stop()

st.info(f"Вы вошли как **{st.session_state.role}** — {st.session_state.user_name}")

# === Выбор сценария и стиля врача ===
scenario_titles = [s["title"] for s in scenarios]
col1, col2 = st.columns(2)
with col1:
    scenario_choice = st.selectbox("Выберите сценарий", ["Случайный"] + scenario_titles)
with col2:
    style_choice = st.radio("Стиль врача", ["Нейтральный", "Доброжелательный", "Скептик"])

# === Получение сценария ===
scenario = random.choice(scenarios) if scenario_choice == "Случайный" else next(s for s in scenarios if s["title"] == scenario_choice)

# === Инициализация состояния ===
if "step" not in st.session_state:
    st.session_state.step = 0
    st.session_state.history = []
    st.session_state.log = {
        "scenario_id": scenario["id"],
        "scenario_title": scenario["title"],
        "style": style_choice,
        "role": st.session_state.role,
        "user_name": st.session_state.user_name,
        "dialog": [],
        "timestamp": datetime.now().isoformat()
    }

# === Диалог ===
st.subheader("💬 Диалог")
for entry in st.session_state.history:
    with st.chat_message(entry["role"]):
        st.markdown(entry["text"])

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
        st.rerun()
else:
    st.success("Диалог завершён ✅")

    # === Кнопка скачать лог ===
    log_json = json.dumps(st.session_state.log, ensure_ascii=False, indent=2)
    st.download_button("📥 Скачать диалог в формате JSON", log_json, "session_log.json", "application/json")

    # === Сохранение статистики ===
    stats_dir = Path("data")
    stats_dir.mkdir(exist_ok=True)
    stats_file = stats_dir / "stats.json"

    stats = []
    if stats_file.exists():
        with open(stats_file, "r", encoding="utf-8") as f:
            stats = json.load(f)
    stats.append(st.session_state.log)
    with open(stats_file, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    # === Автовыход ===
    if st.button("🔁 Начать новую сессию"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    # === Обратная связь только для тренера ===
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

        # === Просмотр статистики тренером ===
        with st.expander("📈 Статистика сессий"):
            st.markdown(f"**Всего сессий:** {len(stats)}")
            avg_len = round(sum(len(s['dialog']) for s in stats) / len(stats), 2)
            st.markdown(f"**Средняя длина диалога:** {avg_len} реплик")

            from collections import Counter
            role_counts = Counter(s["role"] for s in stats)
            for role, count in role_counts.items():
                st.markdown(f"- **{role}**: {count}")
