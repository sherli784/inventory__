#!/usr/bin/env python3
"""
Script to populate the inventory database with sample data
This creates products, locations, and movements as specified in the requirements
"""

from app import app, db, Product, Location, ProductMovement
from datetime import datetime, timedelta
import random

def populate_sample_data():
    with app.app_context():
        # Ensure tables exist
        db.create_all()
        # Clear existing data
        ProductMovement.query.delete()
        Product.query.delete()
        Location.query.delete()
        db.session.commit()
        
        # Create Products
        products = [
            Product(product_id='PROD001', name='Laptop Computer', description='High-performance business laptop'),
            Product(product_id='PROD002', name='Wireless Mouse', description='Ergonomic wireless optical mouse'),
            Product(product_id='PROD003', name='Office Chair', description='Adjustable ergonomic office chair'),
            Product(product_id='PROD004', name='Monitor 24"', description='24-inch LED monitor with HDMI'),
        ]
        
        for product in products:
            db.session.add(product)
        
        # Create Locations
        locations = [
            Location(location_id='WH001', name='Main Warehouse', description='Primary storage facility'),
            Location(location_id='WH002', name='Secondary Warehouse', description='Overflow storage facility'),
            Location(location_id='STORE01', name='Retail Store Front', description='Customer-facing retail location'),
            Location(location_id='OFFICE', name='Office Storage', description='Internal office supply storage'),
        ]
        
        for location in locations:
            db.session.add(location)
        
        db.session.commit()
        
        # Create Product Movements (20+ movements as requested)
        movements = []
        movement_counter = 1
        
        # Initial stock movements (bringing products into warehouses)
        base_date = datetime.now() - timedelta(days=30)
        
        # Stock in movements
        stock_in_movements = [
            ('PROD001', None, 'WH001', 50, base_date + timedelta(days=1)),
            ('PROD002', None, 'WH001', 100, base_date + timedelta(days=1)),
            ('PROD003', None, 'WH001', 25, base_date + timedelta(days=2)),
            ('PROD004', None, 'WH001', 40, base_date + timedelta(days=2)),
            ('PROD001', None, 'WH002', 30, base_date + timedelta(days=3)),
            ('PROD002', None, 'WH002', 75, base_date + timedelta(days=3)),
        ]
        
        for product_id, from_loc, to_loc, qty, timestamp in stock_in_movements:
            movement = ProductMovement(
                movement_id=f'MOV{movement_counter:03d}',
                product_id=product_id,
                from_location=from_loc,
                to_location=to_loc,
                qty=qty,
                timestamp=timestamp
            )
            movements.append(movement)
            movement_counter += 1
        
        # Transfer movements between locations
        transfer_movements = [
            ('PROD001', 'WH001', 'WH002', 10, base_date + timedelta(days=5)),
            ('PROD002', 'WH001', 'STORE01', 20, base_date + timedelta(days=6)),
            ('PROD003', 'WH001', 'STORE01', 5, base_date + timedelta(days=7)),
            ('PROD004', 'WH001', 'STORE01', 8, base_date + timedelta(days=8)),
            ('PROD001', 'WH002', 'STORE01', 5, base_date + timedelta(days=10)),
            ('PROD002', 'WH002', 'OFFICE', 15, base_date + timedelta(days=12)),
            ('PROD003', 'WH001', 'OFFICE', 3, base_date + timedelta(days=14)),
            ('PROD004', 'WH001', 'WH002', 12, base_date + timedelta(days=15)),
        ]
        
        for product_id, from_loc, to_loc, qty, timestamp in transfer_movements:
            movement = ProductMovement(
                movement_id=f'MOV{movement_counter:03d}',
                product_id=product_id,
                from_location=from_loc,
                to_location=to_loc,
                qty=qty,
                timestamp=timestamp
            )
            movements.append(movement)
            movement_counter += 1
        
        # Stock out movements (sales/usage)
        stock_out_movements = [
            ('PROD001', 'STORE01', None, 3, base_date + timedelta(days=16)),
            ('PROD002', 'STORE01', None, 8, base_date + timedelta(days=17)),
            ('PROD003', 'STORE01', None, 2, base_date + timedelta(days=18)),
            ('PROD004', 'STORE01', None, 4, base_date + timedelta(days=19)),
            ('PROD002', 'OFFICE', None, 5, base_date + timedelta(days=20)),
            ('PROD001', 'WH001', None, 7, base_date + timedelta(days=22)),
        ]
        
        for product_id, from_loc, to_loc, qty, timestamp in stock_out_movements:
            movement = ProductMovement(
                movement_id=f'MOV{movement_counter:03d}',
                product_id=product_id,
                from_location=from_loc,
                to_location=to_loc,
                qty=qty,
                timestamp=timestamp
            )
            movements.append(movement)
            movement_counter += 1
        
        # Add all movements to database
        for movement in movements:
            db.session.add(movement)
        
        db.session.commit()
        
        print(f"Sample data populated successfully!")
        print(f"Created {len(products)} products")
        print(f"Created {len(locations)} locations")
        print(f"Created {len(movements)} product movements")
        
        # Print summary of current balances
        print("\nCurrent inventory balances:")
        for product in products:
            print(f"\n{product.product_id} - {product.name}:")
            for location in locations:
                # Calculate balance
                incoming = db.session.query(db.func.sum(ProductMovement.qty)).filter(
                    ProductMovement.product_id == product.product_id,
                    ProductMovement.to_location == location.location_id
                ).scalar() or 0
                
                outgoing = db.session.query(db.func.sum(ProductMovement.qty)).filter(
                    ProductMovement.product_id == product.product_id,
                    ProductMovement.from_location == location.location_id
                ).scalar() or 0
                
                balance = incoming - outgoing
                if balance > 0:
                    print(f"  {location.location_id}: {balance} units")

if __name__ == '__main__':
    populate_sample_data()
