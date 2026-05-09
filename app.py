import csv
import random
import time
from datetime import datetime
from pathlib import Path

import streamlit as st


IMAGES_DIR = Path("images")
REFERENCE_IMAGE = Path("reference/reference.png")
RATINGS_FILE = Path("ratings.csv")
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
CSV_HEADER = [
    "participant_id",
    "image_id",
    "score",
    "confidence",
    "response_time_seconds",
    "submitted_at",
]
SCORE_SLIDER_KEY = "score_slider"
SCORE_NUMBER_KEY = "score_number"
SCORE_OPTIONS = ["NA"] + list(range(101))
CONFIDENCE_OPTIONS = list(range(1, 6))


def get_images():
    return [
        image_path
        for image_path in IMAGES_DIR.iterdir()
        if image_path.is_file() and image_path.suffix.lower() in IMAGE_EXTENSIONS
    ]


def shuffle_images(images):
    shuffled_images = images.copy()
    random.shuffle(shuffled_images)
    return shuffled_images


def start_session(participant_id, total_rounds, images):
    st.session_state.participant_id = participant_id
    st.session_state.total_rounds = total_rounds
    st.session_state.current_round = 1
    st.session_state.current_round_images = shuffle_images(images)
    st.session_state.finished = False
    st.session_state.answer_number = 0
    go_to_next_image(images)


def go_to_next_image(images):
    if not st.session_state.current_round_images:
        st.session_state.current_round += 1

        if st.session_state.current_round > st.session_state.total_rounds:
            st.session_state.finished = True
            return

        st.session_state.current_round_images = shuffle_images(images)

    st.session_state.current_image = st.session_state.current_round_images.pop(0)
    st.session_state.image_started_at = None
    st.session_state.score_value = "NA"
    st.session_state.reset_score_widgets = True
    st.session_state.answer_number += 1


def update_score_from_slider():
    score = st.session_state[SCORE_SLIDER_KEY]
    st.session_state.score_value = score
    st.session_state[SCORE_NUMBER_KEY] = "" if score == "NA" else str(score)


def update_score_from_number():
    score_text = st.session_state[SCORE_NUMBER_KEY].strip()

    if score_text.isdigit() and 0 <= int(score_text) <= 100:
        st.session_state.score_value = int(score_text)
        st.session_state[SCORE_NUMBER_KEY] = str(st.session_state.score_value)
    else:
        st.session_state.score_value = "NA"

    st.session_state[SCORE_SLIDER_KEY] = st.session_state.score_value


def needs_header():
    if st.session_state.get("csv_header_ready"):
        return False

    if not RATINGS_FILE.exists() or RATINGS_FILE.stat().st_size == 0:
        return True

    with RATINGS_FILE.open("r", newline="", encoding="utf-8") as csv_file:
        first_row = next(csv.reader(csv_file), [])

    st.session_state.csv_header_ready = first_row == CSV_HEADER
    return first_row != CSV_HEADER


def save_rating(image_path, score, confidence, response_time):
    submitted_at = datetime.now().isoformat(timespec="seconds")

    with RATINGS_FILE.open("a", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)

        if needs_header():
            writer.writerow(CSV_HEADER)
            st.session_state.csv_header_ready = True

        writer.writerow(
            [
                st.session_state.participant_id,
                image_path.name,
                score,
                confidence,
                round(response_time, 2),
                submitted_at,
            ]
        )


st.set_page_config(page_title="Classificador de gatos-do-mato", layout="centered")
st.title("Classificação de pelagens")

IMAGES_DIR.mkdir(exist_ok=True)

if "images" not in st.session_state:
    st.session_state.images = get_images()

images = st.session_state.images

if not images:
    st.info("A pasta images/ está vazia. Adicione imagens jpg, jpeg, png ou webp para começar.")
    st.stop()

if "participant_id" not in st.session_state:
    if REFERENCE_IMAGE.exists():
        st.image(str(REFERENCE_IMAGE), use_container_width=True)

    participant_id = st.text_input("Nome ou identificador do avaliador")
    total_rounds = st.number_input("Número de rodadas", min_value=1, step=1, value=3)
    st.caption("Cada rodada leva aproximadamente 10 minutos.")

    if st.button("Começar"):
        if not participant_id.strip():
            st.warning("Informe o nome do avaliador antes de começar.")
        else:
            start_session(participant_id.strip(), int(total_rounds), images)
            st.rerun()

    st.stop()

if st.session_state.finished:
    st.success("Suas respostas foram registradas! Muito obrigado pela participação! :)")
    st.stop()

current_image = st.session_state.current_image
total_images = len(st.session_state.images)
progress_in_round = (total_images - len(st.session_state.current_round_images)) / total_images

st.write(f"Rodada {st.session_state.current_round} de {st.session_state.total_rounds}")
st.progress(progress_in_round)
st.image(str(current_image), use_container_width=True)

if st.session_state.image_started_at is None:
    st.session_state.image_started_at = time.time()

st.write("Nota de pelagem")
st.caption("0 = padrão totalmente de pintas sólidas | 100 = padrão totalmente de rosetas")

score_column, number_column = st.columns([3, 1])

if (
    st.session_state.pop("reset_score_widgets", False)
    or SCORE_SLIDER_KEY not in st.session_state
    or SCORE_NUMBER_KEY not in st.session_state
):
    st.session_state.score_value = "NA"
    st.session_state[SCORE_SLIDER_KEY] = "NA"
    st.session_state[SCORE_NUMBER_KEY] = ""

with number_column:
    st.text_input(
        "Valor",
        placeholder="NA",
        key=SCORE_NUMBER_KEY,
        on_change=update_score_from_number,
    )

score_text = st.session_state[SCORE_NUMBER_KEY].strip()
if score_text.isdigit() and 0 <= int(score_text) <= 100:
    st.session_state.score_value = int(score_text)
    st.session_state[SCORE_SLIDER_KEY] = st.session_state.score_value
else:
    st.session_state.score_value = "NA"
    st.session_state[SCORE_SLIDER_KEY] = "NA"

with score_column:
    st.select_slider(
        "Nota",
        options=SCORE_OPTIONS,
        format_func=lambda value: "NA" if value == "NA" else str(value),
        label_visibility="collapsed",
        key=SCORE_SLIDER_KEY,
        on_change=update_score_from_slider,
    )

score = st.session_state.score_value

with st.form(key=f"rating_form_{st.session_state.answer_number}"):
    confidence = st.radio(
        "Confiança",
        options=CONFIDENCE_OPTIONS,
        format_func=lambda value: "⭐" * value,
        horizontal=True,
        index=None,
        key=f"confidence_{st.session_state.answer_number}",
    )
    submitted = st.form_submit_button("Submeter")

if submitted:
    score_text = st.session_state[SCORE_NUMBER_KEY].strip()
    if score_text.isdigit() and 0 <= int(score_text) <= 100:
        score = int(score_text)

    if not isinstance(score, int) or confidence is None:
        st.warning("Escolha uma nota válida e a confiança antes de submeter.")
    else:
        response_time = time.time() - st.session_state.image_started_at
        save_rating(current_image, score, confidence, response_time)
        go_to_next_image(images)
        st.rerun()
