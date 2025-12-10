import os
from dotenv import load_dotenv
import requests
import pyperclip

load_dotenv()
# Импорт токена из .env
WB_API_TOKEN = os.getenv('WB_API_TOKEN')

# Функция для проверки подключения к API Wildberries
def check_wb_connection() -> bool:
    response = requests.get(f'https://common-api.wildberries.ru/ping', headers={'Authorization': f'{WB_API_TOKEN}'})
    if response.status_code == 200:
        return True
    else:
        return False

# Функция для получения списка товаров из API Wildberries
def get_wb_products(objectId: int) -> list[dict]:
    headers = {
        'Authorization': f'Bearer {WB_API_TOKEN}',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }
    body = {
        "settings": {
            "cursor": {
                "limit": 100
            },
            "filter": {
                "objectIDs": [objectId],
                "withPhoto": -1
            }
        }
    }
    response = requests.post(f'https://content-api.wildberries.ru/content/v2/get/cards/list', headers=headers, json=body)
    if response.status_code == 200:
        return response.json()['cards']
    else:
        return None

# Функция для обработки списка товаров
def process_wb_products(products: list[dict]) -> list[dict]:
    result = []
    for product in products:
        for size in product['sizes']:
            for barcode in size['skus']:
                result.append({
                    'wb_nm_id': product['nmID'],
                    'wb_supplier_article': product['vendorCode'],
                    'wb_name': product['title'],
                    'wb_category': product['subjectName'],
                    'wb_barcodes': barcode,
                })
    return result

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
    if check_wb_connection():
        print('Подключение к API Wildberries успешно')
    else:
        print('Ошибка при проверке подключения к API Wildberries')

    products = get_wb_products(435)
    result = process_wb_products(products)
    print_for_copy_paste(result)
    copy_to_clipboard(result)
