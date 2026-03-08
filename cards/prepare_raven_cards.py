import cv2
import numpy as np
from pdf2image import convert_from_path
from pathlib import Path

PDF_PATH = "../assets/cards/all-modules.pdf"
OUTPUT_DIR = Path("raven")

DPI = 400


def straighten(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    thresh = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )[1]

    coords = np.column_stack(np.where(thresh > 0))

    angle = cv2.minAreaRect(coords)[-1]

    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    (h, w) = img.shape[:2]
    center = (w // 2, h // 2)

    M = cv2.getRotationMatrix2D(center, angle, 1.0)

    rotated = cv2.warpAffine(
        img,
        M,
        (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE
    )

    return rotated


def deskew(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    edges = cv2.Canny(gray, 50, 150)

    lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)

    if lines is None:
        return image

    angles = []

    for rho, theta in lines[:, 0]:
        angle = (theta - np.pi / 2) * 180 / np.pi
        angles.append(angle)

    median_angle = np.median(angles)

    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)

    M = cv2.getRotationMatrix2D(center, median_angle, 1.0)

    rotated = cv2.warpAffine(
        image,
        M,
        (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE
    )

    return rotated


def module_letter(index):
    if index < 12:
        return "A"
    if index < 24:
        return "B"
    if index < 36:
        return "C"
    if index < 48:
        return "D"
    return "E"


def detect_elements(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    thresh = cv2.threshold(
        blur,
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )[1]

    contours, _ = cv2.findContours(
        thresh,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    h, w = gray.shape

    matrix_box = None
    answer_boxes = []

    for c in contours:

        x, y, cw, ch = cv2.boundingRect(c)
        area = cw * ch

        if area < 5000:
            continue

        # największy element to matryca
        if matrix_box is None or area > matrix_box[2] * matrix_box[3]:
            matrix_box = (x, y, cw, ch)

    if matrix_box is None:
        return None, []

    mx, my, mw, mh = matrix_box

    for c in contours:

        x, y, cw, ch = cv2.boundingRect(c)
        area = cw * ch

        if area < 3000:
            continue

        # odpowiedzi znajdują się poniżej matrycy
        if y > my + mh:

            ratio = cw / ch

            if 0.5 < ratio < 1.5:
                answer_boxes.append((x, y, cw, ch))

    # sortowanie wierszami
    answer_boxes = sorted(answer_boxes, key=lambda b: (b[1], b[0]))

    return matrix_box, answer_boxes


def process():
    pages = convert_from_path(PDF_PATH, dpi=DPI)

    for i, page in enumerate(pages):

        module = module_letter(i)
        number = (i % 12) + 1

        card_name = f"{module}{number:02d}"

        card_dir = OUTPUT_DIR / module / card_name
        card_dir.mkdir(parents=True, exist_ok=True)

        img = cv2.cvtColor(np.array(page), cv2.COLOR_RGB2BGR)

        img = deskew(img)

        matrix_box, answer_boxes = detect_elements(img)

        if matrix_box is None:
            print("matrix not found", card_name)
            continue

        mx, my, mw, mh = matrix_box
        matrix = img[my:my + mh, mx:mx + mw]
        matrix = straighten(matrix)

        cv2.imwrite(str(card_dir / "matrix.png"), matrix)

        for idx, (x, y, w, h) in enumerate(answer_boxes):
            ans = img[y:y + h, x:x + w]
            ans = straighten(ans)

            cv2.imwrite(
                str(card_dir / f"{idx + 1}.png"),
                ans
            )

        print(
            "processed",
            card_name,
            "answers:",
            len(answer_boxes)
        )


if __name__ == "__main__":
    process()
