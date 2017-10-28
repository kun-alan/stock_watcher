from stock_watcher import events


def event():
    fake_cards = [
        {
            'symbol': 'X',
            'price': '27.80',
            'change': '+0.34',
            'percent_change': '+2.34',
            'color_class': 'color-plus',
        },
        {
            'symbol': 'CLX',
            'price': '127.80',
            'change': '-0.74',
            'percent_change': '-0.54',
            'color_class': 'color-minus',
        },
        {
            'symbol': 'KLIC',
            'price': '21.80',
            'change': '-0.64',
            'percent_change': '-3.04',
            'color_class': 'color-minus',
        },
        {
            'symbol': 'CELG',
            'price': '121.80',
            'change': '0.00',
            'percent_change': '0.00',
            'color_class': 'color-even',
        },
        {
            'symbol': 'PG',
            'price': '75.40',
            'change': '0.00',
            'percent_change': '0.00',
            'color_class': 'color-even',
        },
    ]

    return fake_cards



def history():
    fake_cards = event()
    fake_cards = fake_cards[-1:] + fake_cards[:-1]
    return fake_cards