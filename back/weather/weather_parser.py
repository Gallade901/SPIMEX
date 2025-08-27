
import requests
from bs4 import BeautifulSoup
import pandas as pd
import calendar

def parse_month_data(year, month_num):
    month_name = calendar.month_name[month_num].lower()
    url = f"https://spb.ginfo.ru/pogoda-{month_name}-{year}/"
    response = requests.get(url, verify=False)
    soup = BeautifulSoup(response.content, 'html.parser')

    weather_data = []
    for day_block in soup.find_all('a', class_='pogoda_day'):
        date_str = day_block.find('div', class_='name_day').find('br').next_sibling.strip()
        day = int(date_str.split(' ')[0])
        
        # Extracting temperatures
        temperatures = day_block.find_all('div', class_='temper')
        if len(temperatures) >= 2:
            max_temp = int(temperatures[0].get_text(strip=True).replace('°', '').replace('−', '-'))
            min_temp = int(temperatures[1].get_text(strip=True).replace('°', '').replace('−', '-'))
        else:
            max_temp = None
            min_temp = None

        weather_data.append({
            'Date': f'{day:02d}.{month_num:02d}.{year}',
            'Max_Temp': max_temp,
            'Min_Temp': min_temp
        })
    return weather_data


def main():
    all_weather_data = []
    for year in range(2020, 2026): # 2020 to 2025
        for month_num in range(1, 13):
            print(f"Parsing data for {calendar.month_name[month_num]} {year}...")
            all_weather_data.extend(parse_month_data(year, month_num))

    df = pd.DataFrame(all_weather_data)
    df.to_excel('weather_data_spb_2020-2025.xlsx', index=False)
    print("Data successfully saved to weather_data_spb_2020-2025.xlsx")

if __name__ == "__main__":
    main()
