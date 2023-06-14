

from flask import Flask, jsonify, request
import pandas as pd
from datetime import datetime, timezone

app = Flask(__name__)

# Load the dataset
@app.before_request
def load_dataset():
    global dataset
    dataset = pd.read_csv('D:/Volopay-Backend assignment/data.csv')
    dataset['date'] = pd.to_datetime(dataset['date']) 

# Route to calculate the total seats sold in marketing for Q3
@app.route('/marketing/total_seats_sold_q3')
def total_seats_sold_q3():
    q3_start = datetime(datetime.now().year, 7, 1)  # Q3 starts on July 1st
    q3_end = datetime(datetime.now().year, 9, 30)  # Q3 ends on September 30th
    
    q3_sales = dataset[(dataset['date'] >= q3_start) & (dataset['date'] <= q3_end) & (dataset['department'] == 'marketing')]
    total_seats_sold = q3_sales['seats'].sum()
    
    return str(total_seats_sold)

# Route to calculate the total items or seats sold
@app.route('/api/total_items')
def total_items():
    total_items_sold = dataset['seats'].sum()
    
    return str(total_items_sold)

@app.route('/api/nth_most_total_item/q4_quantity', methods=['GET'])
def q4_quantity():
    q4_sales = dataset.loc[dataset['date'].dt.quarter == 4, ['software', 'seats']]
    q4_sales = q4_sales.groupby('software')['seats'].sum().reset_index()
    q4_sales = q4_sales.sort_values('seats', ascending=False)
    
    if len(q4_sales) >= 2:
        second_most_sold = q4_sales.iloc[1]['software']
        return second_most_sold
    else:
        return 'Insufficient data'

# Route to get the fourth most sold item in terms of total price in q2
@app.route('/api/nth_most_total_item/q2_price', methods=['GET'])
def q2_price():
    q2_sales = dataset.loc[dataset['date'].dt.quarter == 2, ['software', 'amount']]
    q2_sales = q2_sales.groupby('software')['amount'].sum().reset_index()
    q2_sales = q2_sales.sort_values('amount', ascending=False)
    
    if len(q2_sales) >= 4:
        fourth_most_sold = q2_sales.iloc[3]['software']
        return fourth_most_sold
    else:
        return 'Insufficient data'


@app.route('/api/percentage_of_department_wise_sold_items')
def sold_items_percentage():
    department_wise_sold = dataset.groupby('department')['seats'].sum()
    total_sold = department_wise_sold.sum()

    percentage_sold = (department_wise_sold / total_sold) * 100

    result = {
        'percentage_sold': percentage_sold.to_dict()
    }

    return jsonify(result)
# Route to retrieve monthly sales for a specific product
@app.route('/api/monthly_sales', methods=['GET'])
def monthly_sales():
    product_name = request.args.get('product_name')  # Get the product name from the request query parameters
    
    product_sales = dataset.loc[dataset['software'] == product_name, ['date', 'seats']]
    product_sales['date'] = pd.to_datetime(product_sales['date'])
    product_sales.set_index('date', inplace=True)
    monthly_sales = product_sales.resample('M').sum()
    
    monthly_sales_values = monthly_sales['seats'].tolist()
    
    return jsonify(monthly_sales_values)

if __name__ == '__main__':
    app.run()