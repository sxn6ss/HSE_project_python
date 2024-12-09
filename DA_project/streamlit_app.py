import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.subplots as sp
import plotly.express as px
import io
import requests
from api import add_car

st.title("DATA analysis project")
st.title("Creator : Sergeev Nikita 241-1")

api_url = "http://127.0.0.1:8000"
data = pd.read_csv("car_data.csv")

st.header("Поиск машин")
brand = st.text_input("Марка машины:")
min_hp = st.number_input("Минимальная мощность (л.с.):", value=0)
max_hp = st.number_input("Максимальная мощность (л.с.):", value=500)
limit = st.number_input("Сколько объявлений показать", value=100, min_value=1)


if st.button("Get data about cars"):
    params = {"brand": brand,"min_hp": min_hp, "max_hp": max_hp, "limit": limit}
    response = requests.get(f"{api_url}/cars/", params=params)
    if response.status_code == 200:
        st.table(response.json())
    else:
        st.error(f"Ошибка: {response.json()['detail']}")

st.header("Add new car")
new_car = {
    "car_brand": st.text_input("Марка машины:", key="car_brand"),
    "car_model": st.text_input("Модель машины:", key="car_model"),
    "car_price": st.number_input("Цена:", value=0),
    "car_age": st.number_input("Возраст машины:", value=0),
    "car_mileage": st.number_input("Пробег:", value=0),
    "car_engine_hp": st.number_input("Мощность двигателя (л.с.):", value=0),
    "car_fuel": st.text_input("Тип топлива:", key="car_fuel"),
    "car_transmission": st.text_input("Тип коробки передач:", key="car_transmission"),
    "car_country": st.text_input("Страна производства:", key="car_country"),
}

if st.button("Добавить машину"):
    response = add_car(new_car)
    st.success(response["message"])
    st.write("Добавленная машина:")
    st.table(pd.DataFrame([response["car"]]))

    st.write("Обновленные данные:")
    st.table(data.tail(10))

st.table(data.head(10))
buffer = io.StringIO()
data.info(buf=buffer)
st.text(buffer.getvalue())
st.write("Все заголовки столбцов:")
st.table(data.columns)

st.write("Проверим данные на наличие пропусков вызовом набора методов для суммирования пропущенных значений.")
st.table(data.isnull().sum())
st.write("Проверяем датасет на наличие дубликатов, в случае наличия удаляем их.")
st.write("Найдено повторений: ", data.duplicated().sum())
st.write("Так как дубликаты есть, нужно их удалить.")
data = data.drop_duplicates().reset_index(drop=True)
st.write("Проверяем остались ли дубликаты после удаления.")
st.write("Дубликаты: ", data.duplicated().sum())
st.write("Добавим два новых столбца: price_per_hp — стоимость автомобиля за одну лошадиную силу и age_to_mileage_ratio — отношение возраста автомобиля к пробегу.")
data['price_per_hp'] = data['car_price'] / data['car_engine_hp']
data['age_to_mileage_ratio'] = data['car_age'] / data['car_mileage']
st.table(data.head(10))
st.write("Теперь в нашем датасете присутствуют еще два дополнительных столбца.")
st.write("Построим графики для двух новых столбцов.")
plt.figure(figsize=(8, 4))
plt.scatter(data["car_engine_hp"], data["price_per_hp"], label="Price per HP", color='blue')
plt.title("Стоимость за одну л.с.")
plt.ylabel("Price per HP")
plt.legend()
plt.grid()
st.pyplot(plt)
plt.close()

plt.figure(figsize=(8, 4))
plt.scatter(data['car_mileage'], data["age_to_mileage_ratio"], label="Age to Mileage Ratio", color='green')
plt.title("Отношение возраста к пробегу")
plt.ylabel("Age to Mileage Ratio")
plt.legend()
plt.grid()
st.pyplot(plt)
plt.close()

st.write("Найдем самую популярную для продажи машину.")
inf_model = data[['car_brand', 'car_model']]

st.write("Датасет с ифнормацией о бренде и марке машины:")
st.table(inf_model.head(10))

st.write("Теперь посчитаем количество проданных машин каждой модели.")
model_counts = inf_model[['car_brand', 'car_model']].value_counts().reset_index()
model_counts.columns = ['car_brand', 'car_model', 'count']
st.table(model_counts.head(10))

st.write("Теперь на основе этих данных посторим график для 10 самых популярных для продажи машин.")
top_models = model_counts.nlargest(10, 'count')
sns.barplot(data=top_models, x='count', y='car_model', hue='car_brand', dodge=False)


plt.title('Top 10 Car Models and Brands')
plt.xlabel('Number of Occurrences')
plt.ylabel('Car Model')

st.pyplot(plt)
plt.close()

st.write("Эта диаграмма показывает, что Hyundai Solaris самая продаваемая машина.")

st.write("Узнаем какую часть авто-рынка занимают страны производители.")
st.write("Для начала соберем данные которые покажут сколько машин продается из той или иной страны.")
inf_about_country = data['car_country'].value_counts()
st.table(inf_about_country.head(10))
st.write("Дополним данные столбцом содержащим процентное соотношение количества машин из конкретных стран. А также добавим столбец с заголовком count, в котором будет хранится количество машин из каждой страны. ")
inf_about_country = data['car_country'].value_counts().reset_index()
inf_about_country.columns = ['car_country', 'count']
inf_about_country['percentage'] = (inf_about_country['count'] / inf_about_country['count'].sum()) * 100
st.table(inf_about_country.head(10))
st.write("Теперь нарисуем график в виде карты, но для начала нужно преобразовать все двухбуквенные записи в трехбуквенные, для правильной отрисовки.")
corrections_countries = {
    "JP": "JPN",
    "KR": "KOR",
    "DE": "DEU",
    "RUS": "RUS",
    "USA": "USA",
    "CN": "CHN",
    "FR": "FRA",
    "CZ": "CZE",
    "UK": "GBR",
    "SE": "SWE",
    "IT": "ITA",
    "ES": "ESP",
    "UZ": "UZB",
    "IR": "IRN",
    "UKR": "UKR",
}
st.table(corrections_countries)
st.write("Теперь заменим все аббревиатуры на переделанные.")
inf_about_country['car_country'] = inf_about_country['car_country'].replace(corrections_countries)
st.write("Измененный датасет о странах производителях:")
st.table(inf_about_country.head(10))

fig = px.choropleth(
    inf_about_country,
    locations="car_country",
    locationmode="ISO-3",
    color="percentage",
    hover_name="car_country",
    title="Car Country Distribution",
    color_continuous_scale=px.colors.sequential.Plasma
)

st.plotly_chart(fig)
st.write("На этой диаграмме отчетливо видно, что Япония лидирует по прадажам машин на рынке.")

st.write("Посчитаем количество машин по бренду и узнаем кто занимает большую часть авто-рынка.")
inf_about_cars_brand = data['car_brand'].value_counts().reset_index()
inf_about_cars_brand.columns = ["car_brand", "count"]
st.table(inf_about_cars_brand.head(10))
st.write("Добавим в наш собранный датаспет столбик, где будут храниться процентные значение от общего количества.")
inf_about_cars_brand['percentage'] = (inf_about_cars_brand['count'] / inf_about_cars_brand['count'].sum()) * 100
st.table(inf_about_cars_brand.head(10))
st.write("Теперь по собранным данным  нарисуем график, показывающий какую часть авто-рынка занимает каждый авто бренд из нашего датасета.")
fig = go.Figure(go.Treemap(
    labels=inf_about_cars_brand['car_brand'],
    parents=[""] * len(inf_about_cars_brand['car_brand']),
    values=inf_about_cars_brand['count'],
    textinfo="label+value",
    customdata=inf_about_cars_brand['percentage'],
    hovertemplate=(
        "<b>%{label}</b><br>"
        "Количество: %{value}<br>" 
        "Процент: %{customdata:.2f}%<extra></extra>"
    ),
    marker=dict(
        colorscale="RdYlGn",
        reversescale=True
    )
))

fig.update_layout(
    title="Информация по количеству брендов машин, занимающих авто-рынок",
    title_font_size=20
)

st.plotly_chart(fig)
st.write("Данный график показывает какое количество машин конкретной марки размещено на рынке и  процент рынка занимаемый ими. И лидирует по продажам Toyota.")
st.write("""Далее постараемся определить как образуются цены на машины.
1) Зависимость цены от возраста машины.
2) Зависимость цены от пробега машины.
3) Зависимость цены от мощности двигателя.
4) Зависимость цены от вида топлива.""")

st.write("Соберем датасет для каждой из ситуаций.")
price_and_age = data[['car_price', 'car_age']]
price_and_mileage = data[['car_price', 'car_mileage']]
price_and_power = data[['car_price', 'car_engine_hp']]
price_and_fuel = data[['car_price', 'car_fuel']]
show_inf_data = pd.concat([price_and_age, price_and_mileage, price_and_power, price_and_fuel], axis=1)
show_inf_data = show_inf_data.loc[:, ~((show_inf_data.columns.duplicated()) & (show_inf_data.columns == "car_price"))]
st.table(show_inf_data.head(10))
st.write("Отрисовка графиков и график общих выводов.")
fig = sp.make_subplots(rows=1, cols=4, subplot_titles=["Price | Age", "Price | Mileage", "Price | Power", "Price | Fuel"])

fig.add_trace(go.Scatter(x=price_and_age['car_age'], y=price_and_age['car_price'], mode='markers', name="Price | Age"), row=1, col=1)

fig.add_trace(go.Scatter(x=price_and_mileage['car_mileage'], y=price_and_mileage['car_price'], mode='markers', name="Price | Mileage"), row=1, col=2)

fig.add_trace(go.Scatter(x=price_and_power['car_engine_hp'], y=price_and_power['car_price'], mode='markers', name="Price | Power"), row=1, col=3)

fuel_means = price_and_fuel.groupby("car_fuel")['car_price'].mean()
fig.add_trace(go.Bar(x=fuel_means.index, y=fuel_means.values, name="Price | Fuel"), row=1, col=4)

fig.update_layout(height=500, width=1400, title={'text' : "Price Analysis", 'x': 0.5, 'xanchor': 'center'}, showlegend=False)
st.plotly_chart(fig)
st.write("Эти графики показывают, какие факторы могут влиять на ценообразование машин, например в среднем машины на дизеле стоят дороже.")
st.title("Гипотеза:")
st.write("Действительно ли, что машины марки Toyota покупают с автоматической коробкой передач и с пробегом до 70000 чаще чем с механической коробкоц передач и пробегом до 100000?")
st.write("Для начала соберем все данные о машинах марки Toyota из нашего датасета. ")
data_of_toyota = data[(data['car_brand'] == 'Toyota')]
st.table(data_of_toyota.head(10))
st.write("Теперь мы должны взять из этого датасета информацию о пробеге и коробке передач.")
data_of_toyota = data_of_toyota[['car_transmission', 'car_mileage']]
st.table(data_of_toyota.head(10))
st.write("Теперь возьмем все значения удовлетворяющие нашим условиям.")
main_inf_of_toyota = data_of_toyota.loc[((data_of_toyota['car_transmission'] == 'automatic') & (data_of_toyota['car_mileage'] <= 70000))]
contr_inf_of_toyota = data_of_toyota.loc[((data_of_toyota['car_transmission'] == 'manual') & (data_of_toyota['car_mileage'] < 100000))]
st.write("Автомобили Toyota с автоматической коробкой передач и пробегом меньше 70000:")
st.table(main_inf_of_toyota.head(10))
st.write("Автомобили Toyota с механической коробкой передач и пробегом меньше 100000:")
st.table(contr_inf_of_toyota.head(10))
st.write("Найдем сколько машин подошли по нашим условиям для каждого из двух случаев.")
counts = [main_inf_of_toyota.shape[0], contr_inf_of_toyota.shape[0]]
conditions = ['automatic and car_mileage < 70000 |', '| manual and car_mileage < 100000']
plt.bar(conditions, counts, color = ['blue', 'green'])
plt.ylabel('Количество машин')
plt.title('Сравнение количества машин')

st.pyplot(plt)
plt.close()