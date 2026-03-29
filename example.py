#!/usr/bin/env python
# -*- coding: utf-8 -*-

from parser import YandexMapsParser
from parser.utils import print_route_summary, save_route_to_file


def main():
    # Пример 1: Используем requests (быстро, но может сломаться)
    print("\n" + "=" * 60)
    print("ЗАПУСК С BACKEND='REQUESTS'")
    print("=" * 60)

    with YandexMapsParser(backend='requests', timeout=30) as parser:
        route = parser.get_fastest_route(
            from_point="55.816515,36.968468",  # М-7 Волга
            to_point="55.740193,37.434370",  # Большая Никольская
            mode="auto"
        )

        print_route_summary(route)

    # Пример 2: Используем selenium (надежно, но медленнее)
    #print("\n" + "=" * 60)
    #print("ЗАПУСК С BACKEND='SELENIUM'")
    #print("=" * 60)
#
    #with YandexMapsParser(backend='selenium', headless=True, timeout=30) as parser:
    #    route = parser.get_fastest_route(
    #        from_point="Москва, Красная площадь",
    #        to_point="Москва, ВДНХ",
    #        mode="auto"
    #    )
#
    #    print_route_summary(route)

if __name__ == "__main__":
    main()