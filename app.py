from flask import Flask, render_template, jsonify
from invoice_utils import (
    generate_data_for_date,
    get_previous_working_day,
    get_last_day_of_month,
    get_euro_rate_from_day,
)
from datetime import date

app = Flask(__name__)

@app.route("/<date_str>")
def get_date(date_str: str):
    try:
        requested_date = date.fromisoformat(date_str)
        data = generate_data_for_date(requested_date)
        return jsonify(data)
    except ValueError:
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."})

@app.route("/<int:year>/<int:month>")
def month_page(year: int, month: int):
    today = date.today()
    try:
        year = int(year)
        month = int(month)
        if year > today.year or (year == today.year and month > today.month):
            return jsonify({"error": "Invalid date. Please use a date in the past."})
        
        end_of_month = get_last_day_of_month(month, year)
        fx_day = get_previous_working_day(end_of_month)
        fx_rate = get_euro_rate_from_day(fx_day)

        month_days = []
        for day in range(1, end_of_month.day + 1):
            try:
                requested_date = date(year, month, day)
                data = generate_data_for_date(requested_date)
                month_days.append(data)
            except ValueError:
                break
        return render_template(
            "month.html",
            year=year,
            month=month,
            end_of_month=end_of_month,
            fx_day=fx_day,
            fx_rate=fx_rate,
            month_days=month_days 
        )
    except ValueError:
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."})

@app.route("/")
def root():
    year = 2024
    result = []
    for month in range(12):
        dl = get_last_day_of_month(month + 1, year)
        dd = get_previous_working_day(dl)
        rate = get_euro_rate_from_day(dd)
        result.append({"month":f"{dd:%B}" , "end_day": dl, "fx_day": dd, "rate": rate})

    return render_template(
        "index.html",  months=result, year=year
    )

if __name__ == "__main__":
    app.run(debug=True)
