
import streamlit as st
import json

# Загрузка сценариев
@st.cache_data
def load_scenarios(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)["scenarios"]

# Найти нужный сценарий
def find_scenario(scenarios, objection, style):
    for item in scenarios:
        if item["objection"] == objection and item["style"] == style:
            return item
    return None

# Загрузка всех 20 сценариев с 3 шагами
scenarios = load_scenarios("scenarios_medrep_multistep_full_20.json")

# Заголовок
st.title("🧠 Мультишаговый тренажёр для медпредставителей")

# Выбор параметров
objection_options = sorted(list(set(s["objection"] for s in scenarios)))
style_options = ["нейтральный", "доброжелательный", "скептик", "раздражённый"]

selected_objection = st.selectbox("Выберите возражение", objection_options)
selected_style = st.selectbox("Выберите стиль врача", style_options)

# Найдём нужный сценарий
scenario = find_scenario(scenarios, selected_objection, selected_style)

if scenario:
    if "step" not in st.session_state or st.session_state.get("last_selection") != (selected_objection, selected_style):
        st.session_state.step = 0
        st.session_state.last_selection = (selected_objection, selected_style)
        st.session_state.feedback_shown = False

    steps = scenario["steps"]
    current_step = st.session_state.step

    if current_step < len(steps):
        step_data = steps[current_step]
        st.subheader(f"👨‍⚕️ Реплика врача (шаг {current_step + 1}/{len(steps)}):")
        st.markdown(f"> {step_data['doctor']}")

        st.subheader("💬 Выберите ответ:")
        for i, answer in enumerate(step_data["answers"]):
            if st.button(f"{i + 1}. {answer['text']}", key=f"step_{current_step}_ans_{i}"):
                st.session_state.selected_answer = answer
                st.session_state.feedback_shown = True

        if st.session_state.get("feedback_shown", False):
            answer = st.session_state.selected_answer
            st.markdown(f"**Тип ответа:** {answer['type']}")
            st.info(answer["feedback"])
            if st.button("➡️ Следующий шаг"):
                st.session_state.step += 1
                st.session_state.feedback_shown = False
                del st.session_state.selected_answer
    else:
        st.success("🎉 Вы завершили сценарий из 3 шагов!")
        if st.button("🔁 Начать заново"):
            st.session_state.step = 0
            st.session_state.feedback_shown = False
            if "selected_answer" in st.session_state:
                del st.session_state.selected_answer
else:
    st.warning("Сценарий не найден.")
