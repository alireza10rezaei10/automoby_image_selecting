import streamlit as st
from pathlib import Path
from utils import Utils


MAX_IMAGES_IN_A_ROW = 3

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "data.csv"
INPUT_FOLDERS = [BASE_DIR / "crawled_images", BASE_DIR / "gandomi_images"]
OUTPUT_FOLDER = BASE_DIR / "selected_images"
OUTPUT_FOLDER.mkdir(exist_ok=True)

utils = Utils(
    CSV_PATH=CSV_PATH,
    INPUT_FOLDERS=INPUT_FOLDERS,
    OUTPUT_FOLDER=OUTPUT_FOLDER,
)


def main():
    utils.setup_styles()
    df = utils.load_data()

    st.session_state.setdefault(key="row_index", default=0)
    st.session_state.setdefault(key="last_row_index", default=0)

    # نمایش انتخاب ردیف
    row_index = st.number_input(
        "شماره ردیف:",
        min_value=0,
        max_value=len(df) - 1,
        value=st.session_state["row_index"],
        step=1,
    )
    if row_index != st.session_state["last_row_index"]:
        st.session_state["row_index"] = int(row_index)
        st.session_state["last_row_index"] = int(row_index)
        st.rerun()

    # اطلاعات محصول جاری
    row = df.iloc[st.session_state["row_index"]]
    amp = str(row["amp"])
    supplier_code = str(row["supplier_product_code"]).split("_")[0]
    title = str(row["title"])

    st.subheader(f"📦 {title}")
    st.caption(f"AMP: {amp} | Supplier code: {supplier_code}")

    # پیدا کردن عکس‌ها
    images = utils.find_images(amp, supplier_code)
    if not images:
        st.warning("❌ هیچ تصویری برای این محصول یافت نشد.")
        return

    st.markdown("لطفاً اولویت هر عکس را تعیین کنید (۰ یعنی انتخاب نشده).")
    priority_data = {}

    cols = st.columns(MAX_IMAGES_IN_A_ROW)
    for i, img_path in enumerate(images):
        with cols[i % MAX_IMAGES_IN_A_ROW]:
            try:
                img_bytes = utils.read_image_bytes(img_path)
                st.image(img_bytes, caption=img_path.name, width="stretch")
            except Exception as e:
                st.warning(f"⚠️ خطا در خواندن عکس {img_path.name}: {e}")
                continue

            priority = st.number_input(
                f"اولویت عکس {i + 1}",
                min_value=0,
                max_value=30,
                value=0,
                key=f"prio_{st.session_state['row_index']}_{i}",
                help="۰ یعنی انتخاب نشده",
            )
            if priority > 0:
                priority_data[img_path] = priority

    # کنترل‌ها
    st.markdown("---")
    col_prev, col_save, col_next = st.columns([1, 2, 1])

    with col_prev:
        if st.button("⬅️ قبلی", use_container_width=True):
            if st.session_state["row_index"] > 0:
                st.session_state["row_index"] -= 1
                st.rerun()
            else:
                st.info("در اولین ردیف هستید.")

    with col_save:
        if st.button("💾 ذخیره انتخاب‌ها", use_container_width=True):
            utils.save_selected_images(amp, priority_data)
            if st.session_state["row_index"] + 1 < len(df):
                st.session_state["row_index"] += 1
                st.rerun()
            else:
                st.balloons()
                st.success("🎉 همه ردیف‌ها بررسی شدند!")

    with col_next:
        if st.button("بعدی ➡️", use_container_width=True):
            if st.session_state["row_index"] + 1 < len(df):
                st.session_state["row_index"] += 1
                st.rerun()
            else:
                st.info("آخرین ردیف است.")

    # عکس‌های انتخاب‌شده قبلی
    existing_selected = utils.list_existing_selected(amp)
    if existing_selected:
        st.markdown("---")
        st.subheader("📸 عکس‌های انتخاب‌شده قبلی:")
        cols2 = st.columns(4)
        for i, filename in enumerate(existing_selected):
            with cols2[i % 4]:
                img_bytes = utils.read_image_bytes(filename)
                st.image(img_bytes, caption=filename.name, width="stretch")


if __name__ == "__main__":
    main()
