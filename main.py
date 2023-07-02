import json
import sys
import aiohttp
import asyncio
import socket
from datetime import datetime, timedelta


MAX_NUM_DAY = 10
ALL_CURRENCY = ("UAH", "USD", "EUR", "CHF", "GBP", "PLZ", "SEK", "XAU", "CAD")


async def response_site(session, url):

    try:

        async with session.get(url) as response:

            if response.status == 200:

                web_response = await response.json()
                web_response_normal = normalize_json(web_response)

                return web_response_normal

            else:
                print(f"Error status: {response.status} for {url}")

    except aiohttp.ClientConnectorError as err:
        print(f'Connection error: {url}', str(err))
    return None


async def main(num_day):

    results = []

    if num_day > MAX_NUM_DAY:
        num_day = MAX_NUM_DAY
        print(f"Maximum number of days: {MAX_NUM_DAY}")
    elif num_day < 1:
        num_day = 1
        print("Minimum number of days: 1")

    async with aiohttp.ClientSession() as session:

        for days_ago in range(num_day):

            day_now = datetime.now().date() - timedelta(days=days_ago)
            url = f'https://api.privatbank.ua/p24api/exchange_rates?json&date={day_now.strftime("%d.%m.%Y")}'

            results.append(await response_site(session, url))

        return results


def normalize_json(jsons: dict):

    main_dict = {}
    dict_of_dicts = {}

    for cur in used_currency:

        for j in jsons['exchangeRate']:

            if j['currency'] == cur:

                try:
                    dict_of_dicts.update({cur: {'sale': j['saleRate'], 'purchase': j['purchaseRate']}})
                except KeyError:
                    dict_of_dicts.update({cur: {'sale': j['saleRateNB'], 'purchase': j['purchaseRateNB']}})

    main_dict.update({jsons['date']: dict_of_dicts})

    return main_dict


if __name__ == "__main__":

    used_currency = ["EUR", "USD"]
    sys_argv = sys.argv
    is_exchange = False

    try:
        num_day_write = int(sys_argv[1])
    except ValueError:
        if sys_argv[1] == "exchange":
            is_exchange = True
            sys_argv.pop(1)
            num_day_write = int(sys_argv[1])
        else:
            sys.exit("Input is not a number!")
    except IndexError:
        sys.exit("Value is not entered!")

    if len(sys_argv) > 2:
        custom_used_currency = []
        for c in sys_argv[2:]:

            if c.upper() in ALL_CURRENCY:
                custom_used_currency.append(c.upper())

        if len(custom_used_currency) > 0:
            used_currency = custom_used_currency
        else:
            if not is_exchange:
                print("You didn't write any of the correct currency! The standard currency used:", ", ".join(used_currency))

    else:
        if not is_exchange:
            print("You didn't write the currency! The standard currency used:", ", ".join(used_currency))

    result = asyncio.run(main(num_day_write))

    if is_exchange:
        sock = socket.socket()
        sock.connect(('localhost', 9090))
        user_encode_data = json.dumps(result).encode('utf-8')
        sock.send(user_encode_data)
        sock.close()
    else:
        if len(result) > 0:
            for line in result:
                print(line)

