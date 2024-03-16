import platform

import aiohttp
import asyncio
from datetime import datetime, timedelta


async def call_pryvat_bank_api(days):

    base_url = "https://api.privatbank.ua/p24api/exchange_rates?date="
    today_date = datetime.now().date()
    date_range = [today_date - timedelta(days=i) for i in range(days)]

    async with aiohttp.ClientSession() as session:
        tasks = []
        for date in date_range:
            formatted_date = date.strftime("%d.%m.%Y")
            url = base_url+formatted_date
            tasks.append(asyncio.create_task(process_url(session, url)))
            result = await asyncio.gather(*tasks)
        return await format_api_response(result)


async def format_api_response(response):
    api_result_for_user = []

    for item in response:
        date = item["date"]
        exchange_rate = item["exchangeRate"]
        eur_curr = None
        usd_curr = None
        eur_sale_rate = None
        eur_purchase_rate = None
        usd_sale_rate = None
        usd_purchase_rate = None
        for item in exchange_rate:
            if item["currency"] == "EUR":
                eur_curr = item
                eur_sale_rate = item["saleRate"]
                eur_purchase_rate = item["purchaseRate"]
            elif item["currency"] == "USD":
                usd_curr = item
                usd_sale_rate = item["saleRate"]
                usd_purchase_rate = item["purchaseRate"]
                break
        formatted_data = {
            date: {"EUR": {"sale": eur_sale_rate, "purchase": eur_purchase_rate}, "USD": {"sale": usd_sale_rate, "purchase": usd_purchase_rate}}}
        api_result_for_user.append(formatted_data)

    return api_result_for_user


async def process_url(session, url):
    async with session.get(url) as response:
        try:
            result = await response.json()
            return result
        except aiohttp.ClientConnectionError as error:
            print(f'Connection error: {url}', str(error))


async def main():
    while True:
        try:
            user_input = int(
                input("Enter a range of dates you want to retrive(min:1, max:10): "))
            if 1 <= user_input <= 10:
                result = await call_pryvat_bank_api(user_input)
                print(result)
            else:
                print("Invalid day entered. Please enter number from 1 to 10 ")

        except ValueError:
            print("Invalid day format. Please enter number from 1 to 10 ")


if __name__ == "__main__":
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
