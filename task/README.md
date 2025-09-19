# Flask Inventory Management Web Application

A simple, clean Flask-based web application to manage products, locations, and product movements with a balance report per location.

## Features
- Add/Edit/View Products
- Add/Edit/View Locations
- Add/Edit/View Product Movements
- Balance Report: Product-wise quantity per location
- Bootstrap 5 UI with a clean layout
- SQLite database using SQLAlchemy ORM

## Tech Stack
- Python 3.9+
- Flask 2.x
- Flask-SQLAlchemy
- Flask-WTF / WTForms
- SQLite (default; easily switchable to MySQL/PostgreSQL)

## Project Structure
```
.
├── app.py
├── populate_sample_data.py
├── requirements.txt
└── templates/
    ├── base.html
    ├── index.html
    ├── products.html
    ├── add_product.html
    ├── edit_product.html
    ├── view_product.html
    ├── locations.html
    ├── add_location.html
    ├── edit_location.html
    ├── view_location.html
    ├── movements.html
    ├── add_movement.html
    ├── edit_movement.html
    └── balance_report.html
```

## Database Schema
- `Product(product_id [PK], name, description)`
- `Location(location_id [PK], name, description)`
- `ProductMovement(movement_id [PK], timestamp, from_location [FK], to_location [FK], product_id [FK], qty)`

Notes:
- `from_location` or `to_location` (or both) can be null to represent stock-in or stock-out.
- Transfers are represented when both are filled.

## Setup
1. Create and activate a virtual environment (recommended)
```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# or cmd
.\.venv\Scripts\activate.bat
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Run the app
```bash
python app.py
```
The app will start at http://127.0.0.1:5000

## Populate Sample Data
This repository includes `populate_sample_data.py` which seeds:
- 4 products
- 4 locations
- 20+ product movements

Run it once after starting the app at least once (so the DB/tables are created):
```bash
python populate_sample_data.py
```

## How to Use
- Add Products via `Products -> Add Product`
- Add Locations via `Locations -> Add Location`
- Record Product Movements via `Movements -> Add Movement`
  - Stock In: leave `From Location` empty, set `To Location`
  - Stock Out: set `From Location`, leave `To Location` empty
  - Transfer: set both `From Location` and `To Location`
- View `Balance Report` to see per-product balances at each location

## Switching to MySQL (Optional)
If you want to use MySQL instead of SQLite:
1. Install a driver, e.g. `pip install mysqlclient` or `pip install PyMySQL`
2. Update the URI in `app.py`:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://user:password@localhost/inventory_db'
```
3. Create the database in MySQL and ensure credentials are correct.

## Screenshots
Add screenshots here (or embed images) showcasing:
- Products list and add form
- Locations list and add form
- Movements list and add form
- Balance report

## Notes
- CSRF protection is enabled via Flask-WTF; the app uses a basic `SECRET_KEY` set in `app.py`. For production, use a secure secret via environment variable.
- The UI is purposely simple and clean to keep the focus on functionality and code clarity.

## License
MIT
