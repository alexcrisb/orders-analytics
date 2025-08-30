

# Orders Analytics

Small Python + SQLite demo:
- Generate `data/orders.csv`
- Load into `orders.db`
- Run analytics → CSVs in `reports/` + `reports/summary.md`

This system analyzes order data from a CSV file, loads it into an SQLite database, and generates detailed analytics reports including daily revenue, category performance, top products, and customer behavior insights.


## Quickstart (macOS)
```bash
python3 -m venv venv
source venv/bin/activate

# optional if you want to regenerate data
# python3 seed_orders.py

python3 load_db.py
python3 queries.py
```


## Outputs

reports/daily_revenue.csv

reports/revenue_by_category.csv

reports/top_products.csv

reports/repeat_customers.csv

reports/summary.md


## Notes

This project was built as a learning exercise. Development was assisted by Cline, an open-source AI coding agent for VS Code.
All code and analysis were reviewed, run, and adjusted manually as part of the learning process.