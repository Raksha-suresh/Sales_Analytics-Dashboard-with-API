from flask import Flask, jsonify, request, render_template, send_from_directory
import pandas as pd

app = Flask(__name__, static_folder='static', template_folder='templates')
DATA_FILE = 'data/sales.csv'

def load_data():
    df = pd.read_csv(DATA_FILE, parse_dates=['date'])
    df['quantity'] = df['quantity'].astype(int)
    df['price'] = df['price'].astype(float)
    df['revenue'] = df['quantity'] * df['price']
    return df

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/sales', methods=['GET'])
def api_sales():
    df = load_data()
    start = request.args.get('start_date')
    end = request.args.get('end_date')
    if start:
        df = df[df['date'] >= pd.to_datetime(start)]
    if end:
        df = df[df['date'] <= pd.to_datetime(end)]
    records = df.sort_values('date').to_dict(orient='records')
    for r in records:
        r['date'] = r['date'].strftime('%Y-%m-%d')
    return jsonify(records)

@app.route('/api/sales/summary', methods=['GET'])
def api_summary():
    df = load_data()
    start = request.args.get('start_date')
    end = request.args.get('end_date')
    if start:
        df = df[df['date'] >= pd.to_datetime(start)]
    if end:
        df = df[df['date'] <= pd.to_datetime(end)]
    total_revenue = float(df['revenue'].sum())
    total_orders = int(df['order_id'].nunique())
    avg_order_value = float(total_revenue / total_orders) if total_orders else 0.0
    return jsonify({
        'total_revenue': round(total_revenue,2),
        'total_orders': total_orders,
        'avg_order_value': round(avg_order_value,2)
    })

@app.route('/api/sales/daily', methods=['GET'])
def api_daily():
    df = load_data()
    start = request.args.get('start_date')
    end = request.args.get('end_date')
    if start:
        df = df[df['date'] >= pd.to_datetime(start)]
    if end:
        df = df[df['date'] <= pd.to_datetime(end)]
    daily = df.groupby(df['date'].dt.date)['revenue'].sum().reset_index()
    daily['date'] = daily['date'].astype(str)
    result = daily.rename(columns={'revenue':'revenue'}).to_dict(orient='records')
    return jsonify(result)

@app.route('/api/sales/top-products', methods=['GET'])
def api_top_products():
    n = int(request.args.get('n', 5))
    df = load_data()
    top = df.groupby('product')['revenue'].sum().reset_index().sort_values('revenue', ascending=False).head(n)
    records = top.to_dict(orient='records')
    return jsonify(records)

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
