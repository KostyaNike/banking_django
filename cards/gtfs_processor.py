# cards/gtfs_processor.py

def get_routes(departure, arrival, date):
    # Пример данных маршрутов
    routes = [
        {
            "train_number": "123",
            "departure_time": "10:00",
            "arrival_time": "14:00",
            "duration": "4 ч 00 мин",
            "link": "https://booking.uz.gov.ua/"
        },
        {
            "train_number": "456",
            "departure_time": "12:00",
            "arrival_time": "16:00",
            "duration": "4 ч 00 мин",
            "link": "https://booking.uz.gov.ua/"
        }
    ]
    return routes
