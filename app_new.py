import streamlit as st
import json
import os

st.set_page_config(page_title="Тренажер ДЗМ: Хирургия (новая база)", page_icon="🩺", layout="centered")
st.title("🩺 Экзаменационный симулятор ДЗМ по хирургии (новая база)")
st.write("Интерактивная база ситуационных задач из файла «тестирование».")

ФАЙЛ_БАЗЫ = "questions_new.json"


def загрузить_и_очистить():
    if not os.path.exists(ФАЙЛ_БАЗЫ):
        return []
    try:
        with open(ФАЙЛ_БАЗЫ, "r", encoding="utf-8") as f:
            вопросы = json.load(f)

        уникальные = []
        виденные = set()
        for q in вопросы:
            текст = q["vopros"].strip().lower()
            if текст not in виденные:
                виденные.add(текст)
                уникальные.append(q)

        for i, item in enumerate(уникальные, start=1):
            item["nomer"] = i

        return уникальные
    except Exception as e:
        st.error(f"Ошибка чтения файла {ФАЙЛ_БАЗЫ}: {e}")
        return []


БАЗА = загрузить_и_очистить()

if not БАЗА:
    st.warning(
        f"Файл '{ФАЙЛ_БАЗЫ}' не найден или пуст. "
        "Сначала запустите convert_excel.py, чтобы создать базу из тестирование.xlsx."
    )
else:
    if "current_idx" not in st.session_state:
        st.session_state.current_idx = 0

    st.sidebar.markdown(f"### Задач в базе: **{len(БАЗА)}**")

    все_темы = ["Все темы"] + sorted(list(set(q["tema"] for q in БАЗА)))
    выбранная_тема = st.sidebar.selectbox("Раздел:", все_темы)

    if выбранная_тема == "Все темы":
        текущие = БАЗА
    else:
        текущие = [q for q in БАЗА if q["tema"] == выбранная_тема]

    if "last_theme" not in st.session_state or st.session_state.last_theme != выбранная_тема:
        st.session_state.current_idx = 0
        st.session_state.last_theme = выбранная_тема

    if st.session_state.current_idx >= len(текущие):
        st.session_state.current_idx = 0

    st.sidebar.write("---")

    def шаг_назад():
        if st.session_state.current_idx > 0:
            st.session_state.current_idx -= 1

    def шаг_вперед():
        if st.session_state.current_idx < len(текущие) - 1:
            st.session_state.current_idx += 1

    def ручной_ввод():
        n = st.session_state.manual_input_key - 1
        if 0 <= n < len(текущие):
            st.session_state.current_idx = n

    st.sidebar.number_input(
        f"Перейти к задаче (1–{len(текущие)}):",
        min_value=1,
        max_value=len(текущие),
        value=int(st.session_state.current_idx + 1),
        step=1,
        key="manual_input_key",
        on_change=ручной_ввод,
    )

    item = текущие[st.session_state.current_idx]

    st.sidebar.write(
        f"Вы на вопросе **{st.session_state.current_idx + 1}** "
        f"из **{len(текущие)}** в этом разделе."
    )

    st.markdown(f"### ❓ Задача №{item['nomer']} — {item['tema']}")
    st.info(item["vopros"])

    выбор = st.radio(
        "Выберите один вариант ответа:",
        options=item["varianty"],
        key=f"v_{item['nomer']}",
        index=None,
    )

    if выбор:
        user_idx = item["varianty"].index(выбор)
        правильный_текст = item["varianty"][item["otvet"]]

        if user_idx == item["otvet"]:
            st.success("🎉 Верно!")
        else:
            st.error("❌ Неправильно. Попробуйте другой вариант.")

        st.markdown(
            f"✅ <b>Правильный ответ:</b> "
            f"<span style='background-color:#d4efdf; padding:2px 6px; "
            f"border-radius:4px;'>{правильный_текст}</span>",
            unsafe_allow_html=True,
        )
        st.markdown(f"**Обоснование:** {item['obyasnenie']}")

    st.write("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.button("⬅️ Назад", on_click=шаг_назад,
                  disabled=(st.session_state.current_idx == 0))

    with col2:
        st.markdown(
            f"<p style='text-align:center;font-weight:bold;padding-top:5px;'>"
            f"Вопрос {st.session_state.current_idx + 1} из {len(текущие)}</p>",
            unsafe_allow_html=True,
        )

    with col3:
        st.button("Вперед ➡️", on_click=шаг_вперед,
                  disabled=(st.session_state.current_idx == len(текущие) - 1))