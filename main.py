import tkinter as tk
import threading
import time
import re

import mss
import pytesseract
from PIL import Image


# =========================
# CONFIG
# =========================

SCAN_INTERVAL = 1.0

# If Tesseract isn't in PATH, uncomment this:
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# =========================
# TARGET
# =========================

target = input("Enter target number: ").strip()

if not re.fullmatch(r"\d{1,2}", target):
    print("Enter a number such as 26.")
    raise SystemExit

print(f"Looking for: {target}")
print("Press Ctrl+C in this terminal to stop.")


# =========================
# OVERLAY
# =========================

root = tk.Tk()
root.title("OCR Target Finder")

root.attributes("-fullscreen", True)
root.attributes("-topmost", True)

# Transparent window
root.configure(bg="black")
root.wm_attributes("-transparentcolor", "black")

canvas = tk.Canvas(
    root,
    bg="black",
    highlightthickness=0
)
canvas.pack(fill="both", expand=True)


# =========================
# SCREEN OCR
# =========================

sct = mss.mss()

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()


def scan_screen():
    while True:
        try:
            # Screenshot entire primary monitor
            screenshot = sct.grab({
                "left": 0,
                "top": 0,
                "width": screen_width,
                "height": screen_height
            })

            image = Image.frombytes(
                "RGB",
                screenshot.size,
                screenshot.rgb
            )

            # OCR with bounding boxes
            data = pytesseract.image_to_data(
                image,
                config="--psm 6",
                output_type=pytesseract.Output.DICT
            )

            matches = []

            for i, text in enumerate(data["text"]):
                text = text.strip()

                if not text:
                    continue

                # OCR sometimes adds spaces/punctuation
                cleaned = re.sub(r"\D", "", text)

                if cleaned == target:
                    x = data["left"][i]
                    y = data["top"][i]
                    w = data["width"][i]
                    h = data["height"][i]

                    matches.append((x, y, w, h))

            # Update overlay from tkinter's main thread
            root.after(0, draw_boxes, matches)

        except Exception as e:
            print("OCR error:", e)

        time.sleep(SCAN_INTERVAL)


# =========================
# DRAW BOXES
# =========================

def draw_boxes(matches):
    canvas.delete("target")

    for x, y, w, h in matches:
        padding = 5

        canvas.create_rectangle(
            x - padding,
            y - padding,
            x + w + padding,
            y + h + padding,
            outline="red",
            width=4,
            tags="target"
        )


# =========================
# START
# =========================

thread = threading.Thread(
    target=scan_screen,
    daemon=True
)

thread.start()

root.mainloop()
