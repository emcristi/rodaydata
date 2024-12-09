from fastapi import FastAPI
from datetime import date, timedelta, datetime
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import holidays
import re
from fastapi import Request

app = FastAPI()
templates = Jinja2Templates(directory="templates")

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
        if not is_public_holiday(requested_date):
            return requested_date
        
        
def is_public_holiday(requested_date: date) -> bool:
    ro_holidays=holidays.RO(years=requested_date.year)
    if requested_date in ro_holidays:
        return True
    else:
        if requested_date.weekday() >=5:
            return True
    return False

def generate_data_for_date(requested_date: date) -> dict:
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
        "previous_working_day":get_previous_working_day(requested_date).isoformat()
    }

def get_last_day_of_month(month:int, year:int)->datetime:
    last_day = 31
    one_day = timedelta(days=1)
    if month == 12: 
        last_day = datetime(year + 1, 1, 1) - one_day
    else:
        last_day = datetime(year, month+1, 1) - one_day
    # print(f"Last day of month {month} from {year} is: {last_day: %B(%m)/%d %0A}")
    return last_day


@app.get("/{date_str}")
async def get_date(date_str:str):
    try:
        requested_date=date.fromisoformat(date_str)
        data = generate_data_for_date(requested_date)
        return data
    except ValueError:
        return {"error":"Invalid date format. Please use YYYY-MM-DD."}



@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    year = 2024
    result= []
    for month in range(12):
        dd = get_previous_working_day(get_last_day_of_month(month+1, year))
        rate = get_euro_rate_from_day(dd) 
        result.append({"date":dd.isoformat(), "rate":rate, "month":month+1})

    return templates.TemplateResponse("index.html", {"message": "Hello World", "result":result, "request": request})
