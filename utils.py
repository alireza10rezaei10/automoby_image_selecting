import streamlit as st
from pathlib import Path
import pandas as pd
import re
import os
import shutil


class Utils:
    def __init__(self, CSV_PATH: Path, INPUT_FOLDERS: list[Path], OUTPUT_FOLDER: Path):
        self.CSV_PATH = CSV_PATH
        self.INPUT_FOLDERS = INPUT_FOLDERS
        self.OUTPUT_FOLDER = OUTPUT_FOLDER

    def setup_styles(self):
        st.set_page_config(page_title="ILookup")

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

    def load_data(self) -> pd.DataFrame:
        """خواندن فایل CSV از دیسک"""
        if not self.CSV_PATH.exists():
            st.error(f"❌ فایل CSV یافت نشد: {self.CSV_PATH}")
            st.stop()
        df = pd.read_csv(self.CSV_PATH)
        if df.empty:
            st.warning("⚠️ فایل CSV خالی است.")
            st.stop()
        return df

    def find_images(self, amp: str, supplier_code: str) -> list[bytes]:
        """پیدا کردن عکس‌های مرتبط در پوشه‌ها"""
        images = []
        pattern = re.compile(
            rf"^({re.escape(amp)}|{re.escape(supplier_code)})", re.IGNORECASE
        )
        for folder in self.INPUT_FOLDERS:
            if not folder.exists():
                st.error(f"❌ پوشه {folder} یافت نشد.")
                st.stop()
            for file in os.listdir(folder):
                if pattern.match(file) and file.lower().endswith(
                    (".jpg", ".jpeg", ".png")
                ):
                    images.append(folder / file)
        return images

    def read_image_bytes(self, path: Path) -> bytes:
        """خواندن تصویر از دیسک به صورت بایت"""
        with open(path, "rb") as f:
            return f.read()

    def save_selected_images(self, amp: str, priority_data: dict[str, int]):
        """ذخیره عکس‌های انتخاب‌شده با اولویت در پوشه خروجی"""
        # حذف فایل‌های قبلی برای این AMP
        for file in self.OUTPUT_FOLDER.glob(f"{amp}-*"):
            file.unlink(missing_ok=True)

        if not priority_data:
            st.info("⚠️ هیچ عکسی انتخاب نشده است.")
            return

        sorted_images = sorted(priority_data.items(), key=lambda x: x[1])
        for i, (img_path, prio) in enumerate(sorted_images, start=1):
            ext = img_path.suffix
            dest_path = self.OUTPUT_FOLDER / f"{amp}-{i}{ext}"
            shutil.copy(img_path, dest_path)

        st.success(f"{len(sorted_images)} عکس برای AMP {amp} ذخیره شد ✅")

    def list_existing_selected(self, amp: str) -> list[Path]:
        """لیست عکس‌های ذخیره‌شده قبلی برای AMP"""
        return sorted(
            self.OUTPUT_FOLDER.glob(f"{amp}-*"),
            key=lambda p: int(re.findall(r"-(\d+)", p.stem)[0])
            if re.findall(r"-(\d+)", p.stem)
            else 0,
        )
