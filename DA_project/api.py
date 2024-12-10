from fastapi import FastAPI, HTTPException
import pandas as pd

app = FastAPI()

data = pd.read_csv("car_data.csv")

data['price_per_hp'] = data['car_price'] / data['car_engine_hp']
data['age_to_mileage_ratio'] = data['car_age'] / data['car_mileage']


@app.get("/cars/")
def get_cars(brand: str = None, min_hp: float = None, max_hp: float = None, limit: int = None):
    filtered_data = data.copy()

    if brand:
        filtered_data = filtered_data[filtered_data['car_brand'].str.lower() == brand.strip().lower()]
    
    if min_hp is not None:
        if min_hp < 0:
            raise HTTPException(status_code=400, detail="min_hp must be a positive value.")
        filtered_data = filtered_data[filtered_data['car_engine_hp'] >= min_hp]

    if max_hp is not None:
        if max_hp < 0:
            raise HTTPException(status_code=400, detail="max_hp must be a positive value.")
        filtered_data = filtered_data[filtered_data['car_engine_hp'] <= max_hp]

    if filtered_data.empty:
        raise HTTPException(status_code=404, detail="No cars found matching the criteria.")

    return filtered_data.head(limit).to_dict(orient="records")

@app.post("/cars/")
def add_car(car: dict):
    try:
        global data
        
        missing_columns = set(car.keys()) - set(data.columns)
        if missing_columns:
            raise ValueError(f"The following columns are not in the dataset: {missing_columns}")

        new_car = pd.DataFrame([car])
        data = pd.concat([data, new_car], ignore_index=True).reset_index(drop=True)

        data.to_csv("car_data.csv", index=False)

        return {
            "message": "Car added successfully!",
            "car": car,
            "updated_data": data.tail(10).to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error adding car: {e}")
