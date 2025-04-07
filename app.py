
import streamlit as st
import json
from datetime import datetime
import os

st.set_page_config(page_title="AI Тренажёр для медпредов", layout="wide")

@st.cache_data
def load_scenarios(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)["scenarios"]

def find_scenario(scenarios, objection, style):
    for item in scenarios:
        if item["objection"] == objection and item["style"] == style:
            return item
    return None

def save_log(entry, path="logs.json"):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []
    data.append(entry)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

scenarios = load_scenarios("scenarios_multistep_20_final.json")

st.title("🧠 AI Тренажёр для медицинских представителей")

role = st.radio("Выберите роль", ["Медпредставитель", "Тренер"], horizontal=True)

if role == "Медпредставитель":
    tab1, tab2 = st.tabs(["🎯 Тренировка", "📊 Просмотр логов"])

    with tab1:
        user_name = st.text_input("Введите ваше имя", value="Пользователь")

        objection_options = sorted(list(set(s["objection"] for s in scenarios)))
        style_options = ["нейтральный", "доброжелательный", "скептик", "раздражённый"]

        selected_objection = st.selectbox("Выберите возражение", objection_options)
        selected_style = st.selectbox("Выберите стиль врача", style_options)

        scenario = find_scenario(scenarios, selected_objection, selected_style)

        if scenario:
            if (
                "step" not in st.session_state
                or st.session_state.get("last_selection") != (selected_objection, selected_style, user_name)
            ):
                st.session_state.step = 0
                st.session_state.last_selection = (selected_objection, selected_style, user_name)
                st.session_state.session_log = []
                st.session_state.answer_submitted = False
                st.session_state.go_next = False

            steps = scenario["steps"]
            current_step = st.session_state.step

            if current_step < len(steps):
                step_data = steps[current_step]
                st.subheader(f"👨‍⚕️ Реплика врача (шаг {current_step + 1}/{len(steps)}):")
                st.markdown(f"> {step_data['doctor']}")

                if not st.session_state.answer_submitted:
                    with st.form(key=f"form_step_{current_step}"):
                        selected_text = st.radio(
                            "💬 Выберите ответ:",
                            [a["text"] for a in step_data["answers"]],
                            key=f"radio_{current_step}"
                        )
                        submitted = st.form_submit_button("Ответить")

                    if submitted:
                        selected = next((a for a in step_data["answers"] if a["text"] == selected_text), None)
                        if selected:
                            st.session_state.answer_submitted = True
                            st.session_state.last_feedback = {
                                "text": selected["text"],
                                "type": selected["type"],
                                "feedback": selected["feedback"],
                                "doctor": step_data["doctor"]
                            }
                            st.session_state.session_log.append({
                                "doctor": step_data["doctor"],
                                "answer": selected["text"],
                                "type": selected["type"]
                            })
                            st.rerun()

                elif st.session_state.answer_submitted and not st.session_state.go_next:
                    feedback = st.session_state.last_feedback
                    st.markdown(f"**Тип ответа:** {feedback['type']}")
                    st.info(feedback["feedback"])
                    if st.button("Продолжить"):
                        st.session_state.go_next = True
                        st.rerun()

                elif st.session_state.go_next:
                    st.session_state.step += 1
                    st.session_state.answer_submitted = False
                    st.session_state.go_next = False
                    st.rerun()
            else:
                st.success("🎉 Вы завершили сценарий из 3 шагов!")

                if st.button("💾 Сохранить тренировку"):
                    save_log({
                        "user": user_name,
                        "timestamp": datetime.now().isoformat(),
                        "objection": selected_objection,
                        "style": selected_style,
                        "steps": st.session_state.session_log
                    })
                    st.success("✅ Результаты сохранены")

                if st.button("🔁 Пройти заново"):
                    st.session_state.step = 0
                    st.session_state.session_log = []
                    st.session_state.answer_submitted = False
                    st.session_state.go_next = False
        else:
            st.warning("Сценарий не найден.")

    with tab2:
        log_path = "logs.json"
        st.header("📊 Логи тренировок")

        if os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if data:
                user_filter = st.selectbox("Фильтр по пользователю", ["Все"] + list({entry["user"] for entry in data}))
                filtered = data if user_filter == "Все" else [d for d in data if d["user"] == user_filter]

                st.write(f"🔢 Найдено записей: {len(filtered)}")

                for entry in filtered[::-1]:
                    with st.expander(f"👤 {entry['user']} — {entry['objection']} / {entry['style']} — {entry['timestamp']}"):
                        for i, step in enumerate(entry["steps"], 1):
                            st.markdown(f"**Шаг {i}**")
                            st.markdown(f"> 👨‍⚕️ Врач: {step['doctor']}")
                            st.markdown(f"➡️ Ответ: *{step['answer']}*")
                            st.markdown(f"🟡 Тип: **{step['type']}**")
                            st.markdown("---")
            else:
                st.info("Лог пуст. Пройдите хотя бы один сценарий.")
        else:
            st.info("Файл logs.json не найден.")

else:
    st.info("🔒 Режим тренера активен. Здесь будет доступ к результатам и аналитике (в будущей версии).")
