import  argparse
from parser import YandexMapsParser
from parser.utils import print_route_summary

parser = argparse.ArgumentParser(
                    prog='YMaps parser',
                    description='Парсит время поездки через яндекс карты')

parser.add_argument("--fr")
parser.add_argument("--to")
parser.add_argument("-t", "--type", default="auto")
parser.add_argument("-m", "--method", default="requests")

args = parser.parse_args()

with YandexMapsParser(backend='requests', timeout=30) as parser:
    route = parser.get_fastest_route(
        from_point=args.fr,  # М-7 Волга
        to_point=args.to,  # Большая Никольская
        mode=args.type
    )

    print_route_summary(route)