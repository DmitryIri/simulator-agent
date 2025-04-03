
import streamlit as st
import json
from datetime import datetime

# === Загрузка структурированных сценариев ===
with open("scenarios_structured.json", "r", encoding="utf-8") as f:
    scenarios = json.load(f)

# === Заголовок ===
st.set_page_config(page_title="MP-Agent: Структурированный", page_icon="🧩")
st.title("🧩 Тренажёр: Работа с возражениями (по этапам)")

# === Выбор сценария ===
scenario_titles = [s["title"] for s in scenarios]
scenario_choice = st.selectbox("Выберите сценарий:", scenario_titles)
scenario = next(s for s in scenarios if s["title"] == scenario_choice)

# === Инициализация состояния ===
if "structured_step" not in st.session_state:
    st.session_state.structured_step = 0
    st.session_state.structured_results = []
    st.session_state.structured_start = datetime.now().isoformat()

# === Получение текущего этапа ===
step = st.session_state.structured_step
if step < len(scenario["stages"]):
    stage = scenario["stages"][step]
    st.subheader(f"🧭 Этап: {stage['name']}")
    st.markdown(f"**👨‍⚕️ Врач:** _{stage['doctor_says']}_")

    options = stage["options"]
    labels = [f"{opt['text']}" for opt in options]
    choice = st.radio("👉 Выберите ответ:", labels, key=f"stage_{step}")

    if st.button("Ответить", key=f"submit_{step}"):
        selected_option = next(opt for opt in options if opt["text"] == choice)
        st.session_state.structured_results.append({
            "stage": stage["name"],
            "choice": selected_option["text"],
            "label": selected_option["label"]
        })
        st.session_state.structured_step += 1
        st.rerun()
else:
    st.success("✅ Все этапы пройдены!")

    results = st.session_state.structured_results
    st.subheader("📊 Результаты прохождения:")
    for r in results:
        emoji = {"правильный": "✅", "нейтральный": "⚠️", "ошибочный": "❌"}[r["label"]]
        st.markdown(f"- **{r['stage']}**: {emoji} {r['choice']}")

    correct = sum(1 for r in results if r["label"] == "правильный")
    total = len(results)
    score = round(correct / total * 100)
    st.markdown(f"**Итоговая оценка: {correct} из {total} ({score}%)**")

    if st.button("🔁 Пройти заново"):
        for key in ["structured_step", "structured_results", "structured_start"]:
            del st.session_state[key]
        st.rerun()
