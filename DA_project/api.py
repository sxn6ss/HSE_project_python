from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
from typing import List

# Load the dataset
data = pd.read_csv("car_data.csv")

app = FastAPI()

# Define a Pydantic model for the dataset
class CarData(BaseModel):
    car_name: str
    car_price: float
    car_engine_hp: float
    car_mileage: float
    car_age: int

# GET method to fetch filtered or paginated data
@app.get("/cars/")
def get_cars(skip: int = 0, limit: int = 10):
    """
    Get cars with pagination.
    Arguments:
    - skip: number of records to skip (default: 0)
    - limit: number of records to return (default: 10)
    """
    filtered_data = data.iloc[skip:skip + limit]
    return filtered_data.to_dict(orient="records")

# POST method to create a new car data instance
@app.post("/cars/")
def create_car(car: CarData):
    new_car = car.dict()
    # Append the new data to the dataframe (or handle database if needed)
    data = data.append(new_car, ignore_index=True)
    return new_car
