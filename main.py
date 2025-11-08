import streamlit as st
import pandas as pd
import os
import shutil
from PIL import Image

# تنظیمات صفحه
st.set_page_config(page_title="انتخاب عکس‌ها")
st.markdown(
    """
        <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;500;700&display=swap" rel="stylesheet">

        <style>
        html, body, [class*="css"] {
            font-family: 'Vazirmatn', sans-serif !important;
            direction: rtl;
            text-align: right;
        }

        .stApp, .block-container, .css-1outpf7 {
            font-family: 'Vazirmatn', sans-serif !important;
        }

        h1, h2, h3, h4, h5, h6 {
            font-family: 'Vazirmatn', sans-serif !important;
        }
        </style>
        """,
    unsafe_allow_html=True,
)

# مسیرها
csv_path = "data.csv"
input_folders = ["crawled_images", "gandomi_images"]
output_folder = "selected_images"
os.makedirs(output_folder, exist_ok=True)

# خواندن CSV
@st.cache_data
def load_data(csv_path):
    return pd.read_csv(csv_path)

df = load_data(csv_path)

# مقدار اولیه
if "row_index" not in st.session_state:
    st.session_state["row_index"] = 0

# کنترل شماره ردیف
row_index = st.number_input(
    "شماره ردیف:",
    min_value=0,
    max_value=len(df) - 1,
    value=st.session_state["row_index"],
)
st.session_state["row_index"] = row_index  # همگام‌سازی

row = df.iloc[row_index]
amp = str(row["amp"])
supplier_code = str(row["supplier_product_code"]).split("_")[0]
title = str(row["title"])

st.subheader(f"📦 {title}")
st.caption(f"AMP: {amp} | Supplier code: {supplier_code}")

# پیدا کردن عکس‌های مرتبط
images = []
for folder in input_folders:
    if os.path.exists(folder):
        for file in os.listdir(folder):
            if file.startswith(amp) or file.startswith(supplier_code):
                if file.lower().endswith((".jpg", ".jpeg", ".png")):
                    images.append(os.path.join(folder, file))

if not images:
    st.warning("هیچ عکسی برای این ردیف پیدا نشد.")
    st.stop()

# 🔸 نمایش عکس‌ها و انتخاب اولویت
st.write("اولویت هر عکس را مشخص کنید (مثلاً ۱ برای بهترین عکس).")
priority_data = {}

cols = st.columns(4)
for i, img_path in enumerate(images):
    with cols[i % 4]:
        img = Image.open(img_path)
        st.image(img, caption=os.path.basename(img_path), width="stretch")
        priority = st.number_input(
            f"اولویت عکس {i + 1}",
            min_value=0,
            max_value=10,
            value=0,
            key=f"prio_{row_index}_{i}",
            help="۰ یعنی انتخاب نشده",
        )
        if priority > 0:
            priority_data[img_path] = priority

# 🔹 عکس‌های ذخیره‌شده قبلی
existing_selected = sorted(
    [f for f in os.listdir(output_folder) if f.startswith(f"{amp}-")],
    key=lambda x: int(x.split("-")[-1].split(".")[0]),
)

# --- دکمه‌ها ---
col_prev, col_save, col_next = st.columns([1, 2, 1])

with col_prev:
    if st.button("➡ ردیف قبلی", use_container_width=True):
        if st.session_state["row_index"] > 0:
            st.session_state["row_index"] -= 1
            st.rerun()
        else:
            st.warning("در اولین ردیف هستید!")

with col_save:
    if st.button("💾 ذخیره انتخاب‌ها", use_container_width=True):
        # حذف عکس‌های قبلی برای این AMP
        for file in os.listdir(output_folder):
            if file.startswith(f"{amp}-"):
                os.remove(os.path.join(output_folder, file))

        if priority_data:
            # مرتب‌سازی بر اساس اولویت
            sorted_images = sorted(priority_data.items(), key=lambda x: x[1])
            for i, (img_path, prio) in enumerate(sorted_images, start=1):
                ext = os.path.splitext(img_path)[1]
                dest_path = os.path.join(output_folder, f"{amp}-{i}{ext}")
                shutil.copy(img_path, dest_path)
            st.success(f"{len(sorted_images)} عکس برای AMP {amp} ذخیره شد ✅")
        else:
            st.info("هیچ عکسی انتخاب نشد، چیزی ذخیره نشد.")

        # رفتن خودکار به ردیف بعد
        if st.session_state["row_index"] + 1 < len(df):
            st.session_state["row_index"] += 1
            st.rerun()
            

with col_next:
    if st.button("ردیف بعدی ⬅", use_container_width=True):
        if st.session_state["row_index"] + 1 < len(df):
            st.session_state["row_index"] += 1
            st.rerun()
        else:
            st.info("به آخر لیست رسیدید ✅")
            st.balloons()
            st.success("🎉 همه ردیف‌ها بررسی شدند!")

# نمایش عکس‌های تاییدشده قبلی
if existing_selected:
    st.markdown("---")
    st.subheader("📸 عکس‌های تاییدشده قبلی:")
    cols2 = st.columns(4)
    for i, filename in enumerate(existing_selected):
        with cols2[i % 4]:
            img_path = os.path.join(output_folder, filename)
            if os.path.exists(img_path):
                st.image(img_path, caption=filename, width="stretch")
