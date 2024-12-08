import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load the dataset
data = pd.read_csv("car_data.csv")
data['price_per_hp'] = data['car_price'] / data['car_engine_hp']
data['age_to_mileage_ratio'] = data['car_age'] / data['car_mileage']

# Streamlit title and introduction
st.title("Car Data Analysis")
st.write("""
    This app provides analysis of car data, including price per horsepower, 
    and age-to-mileage ratio. Use the options below to view different aspects 
    of the project and interact with the data.
""")

# Sidebar menu
option = st.sidebar.selectbox(
    "Select an option",
    ("Dataset", "Price per Horsepower", "Age to Mileage Ratio", "Statistics")
)

if option == "Dataset":
    st.subheader("Dataset")
    st.write(data.head(10))  # Displaying first 10 rows

elif option == "Price per Horsepower":
    st.subheader("Price per Horsepower")
    plt.figure(figsize=(8, 4))
    plt.plot(data["car_engine_hp"], data["price_per_hp"], label="Price per HP", color='blue')
    plt.title("Стоимость за одну л.с.")
    plt.xlabel("Мощность двигателя (л.с.)")
    plt.ylabel("Цена за одну л.с.")
    plt.legend()
    plt.grid()
    st.pyplot()

elif option == "Age to Mileage Ratio":
    st.subheader("Age to Mileage Ratio")
    plt.figure(figsize=(8, 4))
    plt.plot(data['car_mileage'], data["age_to_mileage_ratio"], label="Age to Mileage Ratio", color='green')
    plt.title("Отношение возраста к пробегу")
    plt.xlabel("Пробег (км)")
    plt.ylabel("Отношение возраста к пробегу")
    plt.legend()
    plt.grid()
    st.pyplot()

elif option == "Statistics":
    st.subheader("Data Statistics")
    st.write(data.describe())  # Display statistics for dataset
