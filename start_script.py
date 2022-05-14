import requests
import pandas as pd


def generate_colors():
    number_of_colors = 223
    counter = 0
    result = []
    while counter < number_of_colors:
        r = requests.get('http://www.colr.org/json/colors/random/7')
        lst = r.json()['matching_colors']
        for color in lst:
            if color != '' and counter < number_of_colors:
                result.append('#' + color)
                counter += 1
        print('\r', end='')
        print(f'Completed: {int((counter / number_of_colors) * 100)}%', end='')
    print()
    return result


def create_colors_file():
    countries = pd.read_csv('country_vaccinations.csv')['country'].unique()
    print('Start.')
    colors = generate_colors()
    dict_of_colors = pd.Series(index=countries, data=colors)
    dict_of_colors.to_csv('colors.csv')


def create_cumsums_file():
    vac_pd = pd.read_csv('country_vaccinations.csv')
    daily_vacc = vac_pd.pivot(index='date', columns='country', values='daily_vaccinations')
    daily_vacc = daily_vacc.fillna(0)
    daily_vacc = daily_vacc.cumsum()
    daily_vacc['Date'] = daily_vacc.index
    daily_vacc = pd.concat([daily_vacc], ignore_index=True)
    daily_vacc.to_csv('cumsums_vaccinated.csv')


def main():
    create_colors_file()
    create_cumsums_file()


if __name__ == '__main__':
    main()