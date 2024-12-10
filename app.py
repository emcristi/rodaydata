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

@app.route("/")
def root():
    year = 2024
    result = []
    for month in range(12):
        dl = get_last_day_of_month(month + 1, year)
        dd = get_previous_working_day(dl)
        rate = get_euro_rate_from_day(dd)
        result.append({"month":f"{dd:%B}" , "end_day": f"{dl:%A, %d-%m-%Y}", "fx_day":f"{dd:%A, %d-%m-%Y}", "rate": rate})

    return render_template(
        "index.html", message=f"FX rate at the end of each month in {year}", months=result
    )

if __name__ == "__main__":
    app.run(debug=True)
