from flask import Flask, request, jsonify
from . import create_app
from .models import db, Company

import yfinance as yf

app = create_app()
print("a")

@app.route('/')
def hello():
    companies = Company.query.all()
    print(companies[1].company_name + " " + companies[1].stock_code)
    return 'Hello World!'

@app.route('/api/stock', methods=['GET'])
def get_stock_data():
    company_code = request.args.get('company_code')
    stock = yf.Ticker(company_code)
    current_price = stock.history(period="1d")['Close'][0]
    valuation = "適正" if current_price >= 100 else "割安" if current_price < 100 else "割高"
    return jsonify({"current_price": current_price, "valuation": valuation})

if __name__ == '__main__':
    app.run(debug=True)