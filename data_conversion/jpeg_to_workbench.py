import cv2
import pytesseract
import numpy as np

# Caminho do Tesseract (caso necessário)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_roi(image, roi):
    x, y, w, h = roi
    roi_img = image[y:y+h, x:x+w]
    roi_img = cv2.cvtColor(roi_img, cv2.COLOR_BGR2GRAY)
    roi_img = cv2.threshold(roi_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    text = pytesseract.image_to_string(roi_img, config='--psm 6')
    return text.strip()

def detect_tables(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    tables = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w > 150 and h > 100:  # Ajuste baseado na imagem fornecida
            tables.append((x, y, w, h))

    tables = sorted(tables, key=lambda x: (x[1], x[0]))  # Ordenação vertical
    return image, tables

def parse_table_text(text):
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    table_name = lines[0] if lines else "unknown"
    columns = []

    for line in lines[1:]:
        if line.startswith("PK") or line.startswith("FK"):
            continue
        parts = line.split()
        if len(parts) >= 2:
            col_name = parts[0]
            col_type = parts[1]
            columns.append((col_name, col_type))
        elif len(parts) == 1:
            columns.append((parts[0], "VARCHAR(255)"))

    return table_name.replace(":", "").replace("-", "_"), columns

def generate_sql_script(tables_data):
    sql_script = ""
    for table_name, columns in tables_data:
        sql_script += f"CREATE TABLE `{table_name}` (\n"
        for col_name, col_type in columns:
            sql_script += f"  `{col_name}` {col_type},\n"
        sql_script = sql_script.rstrip(',\n') + "\n);\n\n"
    return sql_script

def main(image_path, output_sql="output.sql"):
    image, rois = detect_tables(image_path)
    tables_data = []

    for roi in rois:
        text = extract_text_from_roi(image, roi)
        if len(text.strip()) == 0:
            continue
        table_name, columns = parse_table_text(text)
        if columns:
            tables_data.append((table_name, columns))

    sql_script = generate_sql_script(tables_data)

    with open(output_sql, "w", encoding="utf-8") as f:
        f.write(sql_script)

    print(f"Arquivo SQL gerado com sucesso: {output_sql}")

# Execução
if __name__ == "__main__":
    main("images\jpeg\image.jpeg")
