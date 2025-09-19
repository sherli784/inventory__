from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, DateTimeField, TextAreaField
from wtforms.validators import DataRequired, NumberRange
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class Product(db.Model):
    product_id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Product {self.product_id}>'

class Location(db.Model):
    location_id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Location {self.location_id}>'

class ProductMovement(db.Model):
    movement_id = db.Column(db.String(50), primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    from_location = db.Column(db.String(50), db.ForeignKey('location.location_id'), nullable=True)
    to_location = db.Column(db.String(50), db.ForeignKey('location.location_id'), nullable=True)
    product_id = db.Column(db.String(50), db.ForeignKey('product.product_id'), nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    
    # Relationships
    product = db.relationship('Product', backref='movements')
    from_loc = db.relationship('Location', foreign_keys=[from_location], backref='outgoing_movements')
    to_loc = db.relationship('Location', foreign_keys=[to_location], backref='incoming_movements')
    
    def __repr__(self):
        return f'<ProductMovement {self.movement_id}>'

# Forms
class ProductForm(FlaskForm):
    product_id = StringField('Product ID', validators=[DataRequired()])
    name = StringField('Product Name', validators=[DataRequired()])
    description = TextAreaField('Description')

class LocationForm(FlaskForm):
    location_id = StringField('Location ID', validators=[DataRequired()])
    name = StringField('Location Name', validators=[DataRequired()])
    description = TextAreaField('Description')

class ProductMovementForm(FlaskForm):
    movement_id = StringField('Movement ID', validators=[DataRequired()])
    product_id = SelectField('Product', validators=[DataRequired()])
    from_location = SelectField('From Location', choices=[('', 'Select Location')])
    to_location = SelectField('To Location', choices=[('', 'Select Location')])
    qty = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    timestamp = DateTimeField('Timestamp', default=datetime.now)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

# Product Routes
@app.route('/products')
def products():
    products = Product.query.all()
    return render_template('products.html', products=products)

@app.route('/products/add', methods=['GET', 'POST'])
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        # Check if product already exists
        existing_product = Product.query.get(form.product_id.data)
        if existing_product:
            flash('Product ID already exists!', 'error')
            return render_template('add_product.html', form=form)
        
        product = Product(
            product_id=form.product_id.data,
            name=form.name.data,
            description=form.description.data
        )
        db.session.add(product)
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('products'))
    return render_template('add_product.html', form=form)

@app.route('/products/edit/<product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)
    form.product_id.render_kw = {'readonly': True}
    
    if form.validate_on_submit():
        product.name = form.name.data
        product.description = form.description.data
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('products'))
    return render_template('edit_product.html', form=form, product=product)

@app.route('/products/view/<product_id>')
def view_product(product_id):
    product = Product.query.get_or_404(product_id)
    movements = ProductMovement.query.filter_by(product_id=product_id).order_by(ProductMovement.timestamp.desc()).all()
    return render_template('view_product.html', product=product, movements=movements)

# Location Routes
@app.route('/locations')
def locations():
    locations = Location.query.all()
    return render_template('locations.html', locations=locations)

@app.route('/locations/add', methods=['GET', 'POST'])
def add_location():
    form = LocationForm()
    if form.validate_on_submit():
        # Check if location already exists
        existing_location = Location.query.get(form.location_id.data)
        if existing_location:
            flash('Location ID already exists!', 'error')
            return render_template('add_location.html', form=form)
        
        location = Location(
            location_id=form.location_id.data,
            name=form.name.data,
            description=form.description.data
        )
        db.session.add(location)
        db.session.commit()
        flash('Location added successfully!', 'success')
        return redirect(url_for('locations'))
    return render_template('add_location.html', form=form)

@app.route('/locations/edit/<location_id>', methods=['GET', 'POST'])
def edit_location(location_id):
    location = Location.query.get_or_404(location_id)
    form = LocationForm(obj=location)
    form.location_id.render_kw = {'readonly': True}
    
    if form.validate_on_submit():
        location.name = form.name.data
        location.description = form.description.data
        db.session.commit()
        flash('Location updated successfully!', 'success')
        return redirect(url_for('locations'))
    return render_template('edit_location.html', form=form, location=location)

@app.route('/locations/view/<location_id>')
def view_location(location_id):
    location = Location.query.get_or_404(location_id)
    incoming_movements = ProductMovement.query.filter_by(to_location=location_id).order_by(ProductMovement.timestamp.desc()).all()
    outgoing_movements = ProductMovement.query.filter_by(from_location=location_id).order_by(ProductMovement.timestamp.desc()).all()
    return render_template('view_location.html', location=location, incoming_movements=incoming_movements, outgoing_movements=outgoing_movements)

# Product Movement Routes
@app.route('/movements')
def movements():
    movements = ProductMovement.query.order_by(ProductMovement.timestamp.desc()).all()
    return render_template('movements.html', movements=movements)

@app.route('/movements/add', methods=['GET', 'POST'])
def add_movement():
    form = ProductMovementForm()
    
    # Populate choices
    form.product_id.choices = [(p.product_id, f"{p.product_id} - {p.name}") for p in Product.query.all()]
    locations = [('', 'Select Location')] + [(l.location_id, f"{l.location_id} - {l.name}") for l in Location.query.all()]
    form.from_location.choices = locations
    form.to_location.choices = locations
    
    if form.validate_on_submit():
        # Validate that at least one location is selected
        if not form.from_location.data and not form.to_location.data:
            flash('Please select at least one location (from or to)', 'error')
            return render_template('add_movement.html', form=form)
        
        # Check if movement ID already exists
        existing_movement = ProductMovement.query.get(form.movement_id.data)
        if existing_movement:
            flash('Movement ID already exists!', 'error')
            return render_template('add_movement.html', form=form)
        
        movement = ProductMovement(
            movement_id=form.movement_id.data,
            product_id=form.product_id.data,
            from_location=form.from_location.data if form.from_location.data else None,
            to_location=form.to_location.data if form.to_location.data else None,
            qty=form.qty.data,
            timestamp=form.timestamp.data
        )
        db.session.add(movement)
        db.session.commit()
        flash('Product movement added successfully!', 'success')
        return redirect(url_for('movements'))
    return render_template('add_movement.html', form=form)

@app.route('/movements/edit/<movement_id>', methods=['GET', 'POST'])
def edit_movement(movement_id):
    movement = ProductMovement.query.get_or_404(movement_id)
    form = ProductMovementForm(obj=movement)
    form.movement_id.render_kw = {'readonly': True}
    
    # Populate choices
    form.product_id.choices = [(p.product_id, f"{p.product_id} - {p.name}") for p in Product.query.all()]
    locations = [('', 'Select Location')] + [(l.location_id, f"{l.location_id} - {l.name}") for l in Location.query.all()]
    form.from_location.choices = locations
    form.to_location.choices = locations
    
    if form.validate_on_submit():
        # Validate that at least one location is selected
        if not form.from_location.data and not form.to_location.data:
            flash('Please select at least one location (from or to)', 'error')
            return render_template('edit_movement.html', form=form, movement=movement)
        
        movement.product_id = form.product_id.data
        movement.from_location = form.from_location.data if form.from_location.data else None
        movement.to_location = form.to_location.data if form.to_location.data else None
        movement.qty = form.qty.data
        movement.timestamp = form.timestamp.data
        db.session.commit()
        flash('Product movement updated successfully!', 'success')
        return redirect(url_for('movements'))
    return render_template('edit_movement.html', form=form, movement=movement)

@app.route('/movements/view/<movement_id>')
def view_movement(movement_id):
    movement = ProductMovement.query.get_or_404(movement_id)
    return render_template('view_movement.html', movement=movement)

# Balance Report Route
@app.route('/balance-report')
def balance_report():
    # Calculate balance for each product in each location
    balance_data = []
    
    products = Product.query.all()
    locations = Location.query.all()
    
    for product in products:
        for location in locations:
            # Calculate incoming quantity
            incoming = db.session.query(db.func.sum(ProductMovement.qty)).filter(
                ProductMovement.product_id == product.product_id,
                ProductMovement.to_location == location.location_id
            ).scalar() or 0
            
            # Calculate outgoing quantity
            outgoing = db.session.query(db.func.sum(ProductMovement.qty)).filter(
                ProductMovement.product_id == product.product_id,
                ProductMovement.from_location == location.location_id
            ).scalar() or 0
            
            balance = incoming - outgoing
            
            if balance != 0:  # Only show locations with non-zero balance
                balance_data.append({
                    'product': product,
                    'location': location,
                    'balance': balance
                })
    
    # Pass generated timestamp to template
    return render_template('balance_report.html', balance_data=balance_data, generated_on=datetime.now())

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
