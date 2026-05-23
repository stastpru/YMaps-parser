"""Вспомогательные функции для парсера"""
import json
from datetime import datetime


def save_route_to_file(route_data, filename=None):
    """Сохраняет данные маршрута в JSON файл"""
    if not filename:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'route_{timestamp}.json'

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(route_data, f, ensure_ascii=False, indent=2)

    print(f"Маршрут сохранен в {filename}")
    return filename


def print_route_summary(route_data):
    """Выводит краткую информацию о маршруте"""
    if not route_data or not route_data.get('success'):
        print(f"Ошибка: {route_data.get('error', 'Неизвестная ошибка')}")
        return

    print("\n" + "=" * 60)
    print("САМЫЙ БЫСТРЫЙ МАРШРУТ")
    print("=" * 60)
    print(f"Тип: {route_data.get('type', 'auto')}")
    print(f"Длительность: {route_data.get('duration_text', 'N/A')}")
    print(f"Расстояние: {route_data.get('distance_km', 0)} км ({route_data.get('distance_meters', 0)} м)")

    if route_data.get('traffic_minutes'):
        print(f"С учетом пробок: {route_data['traffic_minutes']} мин")

    print(f"\nТочки маршрута:")
    for i, wp in enumerate(route_data.get('waypoints', [])):
        print(f"  {i + 1}. {wp.get('name', 'N/A')}")

    coords_count = len(route_data.get('coordinates', []))
    print(f"\nКоординат: {coords_count} точек")
    print("=" * 60)