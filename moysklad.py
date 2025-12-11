import requests
import pyperclip
import os
import base64
from dotenv import load_dotenv
from wb import get_wb_vendor_codes, get_wb_products

load_dotenv()
MOYSKLAD_API_LOGIN = os.getenv('MOYSKLAD_API_LOGIN')
MOYSKLAD_API_PASSWORD = os.getenv('MOYSKLAD_API_PASSWORD')
MOYSKLAD_FILTER_PATH_NAME = os.getenv('MOYSKLAD_FILTER_PATH_NAME')

# Функция для возвращения шапки с авторизацией
def get_headers():
    # Кодируем логин и пароль в Base64
    encoded_login_password = base64.b64encode(f'{MOYSKLAD_API_LOGIN}:{MOYSKLAD_API_PASSWORD}'.encode()).decode()
    headers = {
        'Authorization': f'Basic {encoded_login_password}'
    }
    return headers

# Функция получения списка товаров
def get_products():
    products = []

    wb_products = get_wb_products(435)
    wb_vendor_codes = get_wb_vendor_codes(wb_products)

    for vendor_code in wb_vendor_codes:
        url = f'https://api.moysklad.ru/api/remap/1.2/entity/product?filter=article={vendor_code}&filter=pathName=Дом и красота/Тест'
        response = requests.get(url, headers=get_headers())
        if response.status_code == 200:
            for row in response.json()['rows']:
                for barcode in row['barcodes']:
                    products.append({
                        'ms_id': row['id'],
                        'ms_article': row['article'],
                        'ms_path_name': row['pathName'],
                        'ms_name': row['name'],
                        'ms_barcodes': barcode['code128'],
                    })
        else:
            print(response.json())

    return products

# Функция для форматирования данных в формат TSV (удобно для копирования)
def format_for_copy_paste(data: list[dict]) -> str:
    """
    Форматирует данные в формат TSV (табуляция) для вставки в Google Sheets.
    Google Sheets автоматически распознает табуляцию и разместит данные по колонкам.
    """
    if not data:
        return ""
    
    # Получаем заголовки из первого элемента
    headers = list(data[0].keys())
    
    # Создаем строку с заголовками, разделенными табуляцией
    result = "\t".join(headers) + "\n"
    
    # Добавляем строки данных
    for row in data:
        values = []
        for header in headers:
            value = row.get(header, "")
            # Преобразуем в строку и заменяем табуляции/переносы строк на пробелы
            value_str = str(value).replace("\t", " ").replace("\n", " ").replace("\r", " ")
            values.append(value_str)
        result += "\t".join(values) + "\n"
    
    return result

# Функция для копирования данных в буфер обмена
def copy_to_clipboard(data: list[dict]):
    """
    Копирует данные в буфер обмена для вставки в Google Sheets.
    """
    formatted = format_for_copy_paste(data)
    pyperclip.copy(formatted)
    print(f"✓ Данные скопированы в буфер обмена! ({len(data)} строк)")
    print("Теперь просто вставьте их в Google Sheets (Ctrl+V)")

# Функция для вывода данных в консоль (удобно для копирования)
def print_for_copy_paste(data: list[dict]):
    """
    Выводит данные в формате, удобном для копирования в Google Sheets.
    """
    formatted = format_for_copy_paste(data) 
    print("\n" + "="*80)
    print("ДАННЫЕ ДЛЯ КОПИРОВАНИЯ В GOOGLE SHEETS:")
    print("="*80)
    print(formatted)
    print("="*80)
    print(f"\nВсего строк: {len(data)}")
    print("Скопируйте данные выше (Ctrl+A, затем Ctrl+C) и вставьте в Google Sheets (Ctrl+V)")


if __name__ == '__main__':
    products = get_products()
    print_for_copy_paste(products)
    copy_to_clipboard(products)