from fastapi import FastAPI
from datetime import date, timedelta
import holidays
import re

app = FastAPI()

def get_euro_rate_from_day(d: date):
    file_path=f"static/nbrfxrates{d:%Y}.xml"
    
    with open(file_path, 'r', encoding='utf-8') as response:
        xml = response.read()
        date_format=f"{d:%Y-%m-%d}"
        look_for_rate=False
        rate=0
        for l in xml.splitlines():
            # print(look_for_rate)
            if date_format in l:
                look_for_rate = True;
            if look_for_rate and "EUR" in l:
                match=re.search(r'<Rate currency="EUR">([\d.]+)</Rate>', l)
                rate=float(match.group(1))
                break    
    if rate == 0:
        rate = get_euro_rate_from_day(d-timedelta(days=1))           
    return rate

def get_previous_working_day(requested_date: date) -> date:
    while True:
        requested_date = requested_date - timedelta(days=1)
        if generate_data_for_date(requested_date)["public_holiday"] == False:
            return requested_date

def generate_data_for_date(requested_date: date, include_previous_working_day: bool=False) -> dict:
    ro_holidays=holidays.RO(years=requested_date.year)
    public_holiday = False
    public_holiday_name = None
    if requested_date in ro_holidays:
        public_holiday = True
        public_holiday_name = ro_holidays.get(requested_date)
    else:
        if requested_date.weekday() >=5:
            public_holiday = True
            public_holiday_name = "Weekend"
    return {
        "date":requested_date.isoformat(),
        "weekday":requested_date.strftime("%A"),
        "public_holiday":public_holiday,
        "public_holiday_name":public_holiday_name,
        "euro_rate":get_euro_rate_from_day(requested_date),
         "previous_working_day":get_previous_working_day(requested_date).isoformat() if include_previous_working_day else None
    }



@app.get("/{date_str}")
async def get_date(date_str:str):
    try:
        requested_date=date.fromisoformat(date_str)
        data = generate_data_for_date(requested_date, True)
        return data
    except ValueError:
        return {"error":"Invalid date format. Please use YYYY-MM-DD."}



    