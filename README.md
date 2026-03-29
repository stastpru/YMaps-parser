
# YMaps-parser

Парсит время поездки через яндекс карты


## Функции

- Парсит длительность поездки, расстояние и маршруты из Яндекс карт
- Разные типы маршрута(авто, пеший)

## Установка

```bash
pip install -r requirements.txt
```
    
## Пример

```python
from parser import YandexMapsRouteParser

if __name__ == "__main__":
    with YandexMapsRouteParser(headless=False) as parser:
        result = parser.get_fastest_route(
            from_point="55.781939,37.864434",  
            to_point="55.754025,37.617820",  
            mode="auto"
        )
        if result and result.get('success'):
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
```


## FAQ

#### Может ли скрипт работать на сервере без экрана?
нет, поддержка планируется
## TODO

- [ ] Работа на сервере без экрана
