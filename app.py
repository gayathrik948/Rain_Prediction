from fastapi import FastAPI, Request
from typing import Optional
from uvicorn import run as app_run
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from rain.components.model_prediction import CostPredictor, RainPredictionData
from rain.constants import APP_HOST, APP_PORT
from rain.pipeline.training_pipeline import TrainingPipeline

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DataForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.Date: Optional[str] = None
        self.Location: Optional[str] = None
        self.MinTemp: Optional[str] = None
        self.MaxTemp: Optional[str] = None
        self.Rainfall: Optional[str] = None
        self.WindGustDir: Optional[str] = None
        self.WindGustSpeed: Optional[str] = None
        self.WindDir9am: Optional[str] = None
        self.WindDir3pm: Optional[str] = None
        self.WindSpeed9am: Optional[str] = None
        self.WindSpeed3pm: Optional[str] = None
        self.Humidity9am: Optional[str] = None
        self.Humidity3pm: Optional[str] = None
        self.Pressure9am: Optional[str] = None
        self.Pressure3pm: Optional[str] = None
        self.Cloud9am: Optional[str] = None
        self.Cloud3pm: Optional[str] = None
        self.Temp9am: Optional[str] = None
        self.Temp3pm: Optional[str] = None
        self.RainToday: Optional[str] = None
        self.RISK_MM: Optional[str] = None

    async def get_rain_data(self):
        form = await self.request.form()
        self.Date = form.get("Date")
        self.Location = form.get("Location")
        self.MinTemp = form.get("MinTemp")
        self.MaxTemp = form.get("MaxTemp")
        self.Rainfall = form.get("Rainfall")
        self.WindGustDir = form.get("WindGustDir")
        self.WindGustSpeed= form.get("WindGustSpeed")
        self.WindDir9am = form.get("WindDir9am")
        self.WindDir3pm = form.get("WindDir3pm")
        self.WindSpeed9am = form.get("WindSpeed9am")
        self.WindSpeed3pm = form.get("WindSpeed3pm")
        self.Humidity9am = form.get("Humidity9am")
        self.Humidity3pm = form.get("Humidity3pm")
        self.Pressure9am = form.get("Pressure9am")
        self.Pressure3pm = form.get("Pressure3pm")
        self.Cloud9am = form.get("Cloud9am")
        self.Cloud3pm = form.get("Cloud3pm")
        self.Temp9am = form.get("Temp9am")
        self.Temp3pm= form.get("Temp3pm")
        self.RainToday = form.get("RainToday")
        self.RISK_MM = form.get("RISK_MM")


@app.get("/train")
async def trainRouteClient():
    try:
        train_pipeline = TrainingPipeline()
        train_pipeline.run_pipeline()
        return Response("Training successful !!")

    except Exception as e:
        return Response(f"Error Occurred! {e}")


@app.get("/predict")
async def predictGetRouteClient(request: Request):
    try:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "context": "Rendering"},
        )

    except Exception as e:
        return Response(f"Error Occurred! {e}")


@app.post("/predict")
async def predictRouteClient(request: Request):
    try:
        form = DataForm(request)
        await form.get_rain_data()
        rain_data = RainPredictionData(
            Date=form.Date,
            Location=form.Location,
            MinTemp=form.MinTemp,
            MaxTemp=form.MaxTemp,
            Rainfall=form.Rainfall,
            WindGustDir=form.WindGustDir,
            WindGustSpeed=form.WindGustSpeed,
            WindDir9am=form.WindDir9am,
            WindDir3pm=form.WindDir3pm,
            WindSpeed9am=form.WindSpeed9am,
            WindSpeed3pm=form.WindSpeed3pm,
            Humidity9am=form.Humidity9am,
            Humidity3pm=form.Humidity3pm,
            Pressure9am=form.Pressure9am,
            Pressure3pm=form.Pressure3pm,
            Cloud9am=form.Cloud9am,
            Cloud3pm=form.Cloud3pm,
            Temp9am=form.Temp9am,
            Temp3pm=form.Temp3pm,
            RainToday=form.RainToday,
            RISK_MM=form.RISK_MM
        )

        cost_df = rain_data.get_input_data_frame()
        cost_predictor = CostPredictor()
        cost_value = (cost_predictor.predict(X=cost_df)[0], 2)

        if cost_value == "1":
            answer = "Rainy"
            # return templates.TemplateResponse(
            #     "after_rainy.html", {"request": request, "context": answer})
        else:
            answer = "No Rainy"
            # return templates.TemplateResponse(
            #     "after_sunny.html", {"request": request, "context": answer})

        return templates.TemplateResponse(
            "index.html",
            {"request": request, "context": answer}
        )

    except Exception as e:
        return e


if __name__ == "__main__":
    app_run(app, host=APP_HOST, port=APP_PORT)

# if __name__ == "__main__":
# 	pipeline = TrainingPipeline()
# 	pipeline.run_pipeline()
