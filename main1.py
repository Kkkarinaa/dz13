import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import math
import seaborn as sns
import random

with st.echo(code_location='below'):
    def degree_check(n):
        if n < 1000:
            return 1, 1
        a = int(math.log10(n))
        return a, 10**(a)

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
        
    def dynamic_plot_of_vaccinations_start_function(number_of_tops, time_start_date, time_stop_date):
        if st.button('Остановить'):
            return
        daily_vacc = pd.read_csv('cumsums_vaccinated.csv')
        daily_vacc = daily_vacc.drop(columns=['Unnamed: 0'])
        dict_of_colors = pd.read_csv('colors.csv')
        progress_bar = st.progress(0)
        status_bar = st.empty()
        dict_of_colors = pd.Series(index=dict_of_colors['Unnamed: 0'], data=dict_of_colors['0'].values)
        with st.empty():
            for i in range(time_start_date, time_stop_date):
                progress_bar.progress(int(100 * (i - time_start_date) / (time_stop_date - time_start_date)))
                status_bar.text(f'{int(100 * (i - time_start_date) / (time_stop_date - time_start_date))}% Completed')
                sorted_vacc = daily_vacc.drop(columns=['Date']).loc[i].sort_values(ascending=False)[:number_of_tops]
                degree_clear, ten_devide = degree_check(sorted_vacc[-1])
                plt.xlabel(f'Величина, разделенная на 10^{degree_clear}')
                plt.barh(sorted_vacc.index[::-1], sorted_vacc.values[::-1] / ten_devide,
                             color=dict_of_colors.loc[sorted_vacc.index[::-1]])
                st.pyplot(plt, clear_figure=True)
            progress_bar.empty()
            status_bar.empty()
        st.button("Re-run")


    def tourists_plot_start_function(input_countries):
        all_countries_pd = pd.read_csv('API_ST.INT.ARVL_DS2_en_csv_v2_1927083.csv')
        all_countries_pd = all_countries_pd.set_index(all_countries_pd['Country Name'])
        countries_from_list = all_countries_pd.loc[input_countries]
        countries_from_list = countries_from_list.loc[:, '1995':]
        fig, ax = plt.subplots()
        plt.figure(figsize=(15, 15))
        ccc = countries_from_list.transpose()
        ccc = ccc.rename(index=int)
        max_value = ccc.max().max()
        degree_clear, ten_divide = degree_check(max_value)
        for column in ccc.columns:
            ccc[column] = ccc[column] / ten_divide
        sns.set_theme(style="darkgrid")
        g = sns.relplot(data=ccc, kind='line')
        g.set(xlabel='Год', ylabel=f'Количество туристов, деленное на 10^{degree_clear}')
        plt.xticks(rotation=30, horizontalalignment='right')
        st.pyplot(g)


    def build_plot_of_top_billioners(top_number):
        dict_of_colors = pd.read_csv('colors.csv')
        random_colors = random.sample(list(dict_of_colors['0'].values), top_number)
        billioners_csv = pd.read_csv('2022_forbes_billionaires.csv')
        networth_pd = pd.Series(dtype='float64')
        for i in range(len(billioners_csv.index)):
            billioners_csv.loc[i, 'networth'] = float(billioners_csv.loc[i, 'networth'][1:-1])
        fig = plt.figure(figsize=(8, 6))
        plt.xlabel('Биллионы долларов')
        plt.barh(billioners_csv['name'].values[:top_number][::-1], billioners_csv['networth'].values[:top_number][::-1], color=random_colors)
        st.pyplot(plt,clear_figure=True)


    def billioners_ages_start_function():
        billioners_csv = pd.read_csv('2022_forbes_billionaires.csv')
        for i in range(len(billioners_csv.index)):
            billioners_csv.loc[i, 'networth'] = float(billioners_csv.loc[i, 'networth'][1:-1])
        cumsums_ages = billioners_csv[['networth', 'age']]
        cumsums_ages = cumsums_ages.groupby('age').mean()
        billions = []
        for i in cumsums_ages.index:
            billions.append(cumsums_ages.loc[i][0])
        plt.xlabel('Возраст')
        plt.ylabel('Биллионы долларов')
        plt.bar(cumsums_ages.index, billions)
        st.pyplot(plt, clear_figure=True)


    def build_pie_countries_start_function(top_number):
        billioners_csv = pd.read_csv('2022_forbes_billionaires.csv')
        cumsums_countries = billioners_csv['country']
        cumsums_countries = cumsums_countries.value_counts()
        cumsums_countries = cumsums_countries[:top_number]
        names, skipped = plt.pie(cumsums_countries.values)
        plt.legend(names, cumsums_countries.index, loc='best')
        plt.axis('equal')
        plt.tight_layout()
        st.pyplot(plt, clear_figure=True)


    def joke(age):
        billioners_csv = pd.read_csv('2022_forbes_billionaires.csv')
        cumsums_countries = billioners_csv['age']
        cumsums_countries = cumsums_countries.value_counts()
        if age in cumsums_countries.index:
            return cumsums_countries[age]
        else:
            return 0


    def main():

        time_bar_df = pd.read_csv('cumsums_vaccinated.csv')
        time_bar_df = pd.Series(index=time_bar_df['Date'].values, data=time_bar_df.index)
        input_countries = []
        """
        ## Проект по визуализации данных туризма и вакцинации в разных странах, а также доходов и количества долларовых биллионеров в мире!
        """
        """
        ### Первая визуализация посвящена туризму. Она показывает изменение количества туристов в разных странах с 1995 по 2019 год.
        """

        number_of_countries = st.number_input('Выбери количество стран', min_value=1, max_value=100, step=1)
        #buff, col, buff2 = st.columns([1, 3, 1])
        with st.form(key='432'):
            all_countries_pd = pd.read_csv('API_ST.INT.ARVL_DS2_en_csv_v2_1927083.csv')
            for i in range(number_of_countries):
                input_countries.append(st.selectbox(f'Страна №{i + 1}', tuple(all_countries_pd['Country Name'])))
            submit_tourists_plot = st.form_submit_button(label='Построить график')
        if submit_tourists_plot:
            tourists_plot_start_function(input_countries)
        """
        ### Следующая визуализация посвящена акутальной проблеме в нашем мире - вакцинации. Она показывает количество вакцинировавшихся в топе стран, то есть вы можете выбрать желаемый топ стран и период времени, и тогда построится динамический график, показывающий рост вакцинаций с начальной до конечной точки.
        """
        with st.form(key='123'):
            number_of_tops = st.slider('Выбери количество стран', 3, 30, step=1)
            time_start, time_end = st.select_slider('Выбери период времени', options=time_bar_df.index, value=('2020-12-02', '2022-03-29'))
            submit_dynamic = st.form_submit_button(label='Построить динамический график')
        if submit_dynamic:
            dynamic_plot_of_vaccinations_start_function(number_of_tops, int(time_bar_df[time_start]), int(time_bar_df[time_end]))
        input_countries.clear()
        """
        ### Последний набор визуализаций посвящен мировым долларовым биллионерам.
        """
        """
        ##### Здесь первая визуализация показывает топ долларовых биллионеров.
        """
        numer_of_top_billioners = st.number_input('Выбери топ биллионеров', min_value=2, max_value=2600, step=1)
        build_plot_of_top_billioners(numer_of_top_billioners)
        """
        ##### Вторая визуализация показывает совокупный доход биллионеров в определенном возрасте, то есть она показывает общее количество доходов 20-летних, 40-летних и т.д. биллионеров.
        """
        input_age = st.number_input('Сколько тебе лет?', min_value=1, max_value=100, step=1, )
        st.write(f'В 2021 году целых {joke(input_age)} человека твоего возраста заработал billion$')
        billioners_ages_start_function()
        """
        ##### Третья визуализация показывает общее количество долларовых биллионеров в топе стран, то есть можно посмотреть, где больше всего биллионеров в мире.
        """
        top_countries = st.number_input('Выбери топ-количество стран', min_value=2, max_value=75, step=1)
        build_pie_countries_start_function(top_countries)
        st.echo()


    if __name__ == '__main__':
        main()






