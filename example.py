from parser import YandexMapsRouteParser

# Пример использования
if __name__ == "__main__":
    # Создаем парсер (headless=False чтобы видеть браузер)
    with YandexMapsRouteParser(headless=False) as parser:

        # Вариант 1: По координатам
        result = parser.get_fastest_route(
            from_point="55.781939,37.864434",  # М-7 Волга
            to_point="55.754025,37.617820",  # Большая Никольская
            mode="auto"
        )

        # Вариант 2: По названиям
        # result = parser.get_fastest_route(
        #     from_point="Москва, Кремль",
        #     to_point="Москва, ВДНХ",
        #     mode="auto"
        # )

        # Выводим результат
        if result and result.get('success'):
            print("\n" + "=" * 60)
            print("САМЫЙ БЫСТРЫЙ МАРШРУТ")
            print("=" * 60)
            print(f"Тип: {result['type']}")
            print(f"Длительность: {result['duration_text']} ({result['duration_seconds']} сек)")
            print(f"Расстояние: {result['distance_km']} км ({result['distance_meters']} м)")

            if result.get('traffic_minutes'):
                print(f"С учетом пробок: {result['traffic_minutes']} мин")

            print("\nМАРШРУТ:")
            for i, wp in enumerate(result['waypoints']):
                print(f"  {i + 1}. {wp['name']}")
        else:
            print(f"Ошибка: {result.get('error', 'Неизвестная ошибка')}")