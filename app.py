from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy.orm import sessionmaker
from models.base import engine
from models.model import Usuario, SuperstoreOrder
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)

# Secret key para sesión
app.secret_key = os.environ.get("SECRET_KEY", "dev_key_fallback")

# Crear sesión SQLAlchemy
Session = sessionmaker(bind=engine)
db_session = Session()

# Setup de LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth'

@login_manager.user_loader
def load_user(user_id):
    return db_session.query(Usuario).get(int(user_id))

# Ruta principal
@app.route('/')
def home():
    return render_template('auth.html')

# Auth Login / Registro
@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == 'POST':
        action = request.form['action']
        username = request.form['username']
        password = request.form['password']

        if action == 'register':
            if db_session.query(Usuario).filter(Usuario.username == username).first():
                flash('El usuario ya existe', 'danger')
            else:
                new_user = Usuario(
                    username=username,
                    password=generate_password_hash(password)
                )
                db_session.add(new_user)
                db_session.commit()
                flash('Usuario creado exitosamente', 'success')
                return redirect(url_for('auth'))

        elif action == 'login':
            user = db_session.query(Usuario).filter(Usuario.username == username).first()
            if user and check_password_hash(user.password, password):
                login_user(user)
                flash('Sesión iniciada exitosamente', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Usuario o contraseña incorrectos', 'danger')
                return redirect(url_for('auth'))

    return render_template('auth.html')

# Dashboard protegido
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=current_user.username)

# Cerrar sesión
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth'))

# API para listar todas las órdenes
@app.route('/api/superstore_orders')
def api_superstore_orders():
    orders = db_session.query(SuperstoreOrder).all()
    results = []
    for order in orders:
        results.append({
            "OrderID": order.order_id,
            "OrderDate": order.order_date.strftime('%Y-%m-%d'),
            "CustomerName": order.customer_name,
            "Segment": order.segment,
            "Country": order.country,
            "City": order.city,
            "ProductName": order.product_name,
            "Category": order.category,
            "Sales": order.sales,
            "Quantity": order.quantity,
            "Profit": order.profit
        })
    return jsonify(results)

# API de filtros
@app.route('/api/filtros', methods=['GET'])
def obtener_filtros():
    segmento = request.args.getlist('segmento')
    categoria = request.args.getlist('categoria')
    ciudad = request.args.getlist('ciudad')

    query = db_session.query(SuperstoreOrder)

    if segmento:
        query = query.filter(SuperstoreOrder.segment.in_(segmento))
    if categoria:
        query = query.filter(SuperstoreOrder.category.in_(categoria))
    if ciudad:
        query = query.filter(SuperstoreOrder.city.in_(ciudad))

    data = query.all()

    segmentos = sorted({o.segment for o in data if o.segment})
    categorias = sorted({o.category for o in data if o.category})
    ciudades = sorted({o.city for o in data if o.city})

    return jsonify({
        'segmentos': segmentos,
        'categorias': categorias,
        'ciudades': ciudades
    })

# Listado CRUD protegido
@app.route('/listorders')
@login_required
def listorders():
    return render_template('crud/list.html')

# API para listar todas las órdenes (para tabla CRUD)
@app.route('/api/list_orders')
def api_list_orders():
    data = db_session.query(SuperstoreOrder).all()
    orders = []
    for order in data:
        orders.append({
            "id": order.id,
            "OrderID": order.order_id,
            "OrderDate": order.order_date.strftime('%Y-%m-%d'),
            "CustomerName": order.customer_name,
            "Segment": order.segment,
            "City": order.city,
            "ProductName": order.product_name,
            "Category": order.category,
            "Sales": order.sales,
            "Quantity": order.quantity,
            "Profit": order.profit
        })
    return jsonify(orders)

# Opciones para combos de filtros
@app.route('/api/opciones', methods=['GET'])
def obtener_opciones():
    segmentos = db_session.query(SuperstoreOrder.segment).distinct().all()
    categorias = db_session.query(SuperstoreOrder.category).distinct().all()
    ciudades = db_session.query(SuperstoreOrder.city).distinct().all()

    return jsonify({
        "segmentos": sorted([s[0] for s in segmentos if s[0]]),
        "categorias": sorted([c[0] for c in categorias if c[0]]),
        "ciudades": sorted([ci[0] for ci in ciudades if ci[0]])
    })

# Crear nueva orden
@app.route('/add/order', methods=['POST'])
def crear_order():
    data = request.json
    nueva = SuperstoreOrder(
        no=int(data.get('no')),
        row_id=int(data.get('row_id')),
        order_id=data.get('order_id'),
        order_date=data.get('order_date'),
        ship_date=data.get('ship_date'),
        ship_mode=data.get('ship_mode'),
        customer_id=data.get('customer_id'),
        customer_name=data.get('customer_name'),
        segment=data.get('segment'),
        country=data.get('country'),
        city=data.get('city'),
        state=data.get('state'),
        postal_code=data.get('postal_code'),
        region=data.get('region'),
        product_id=data.get('product_id'),
        category=data.get('category'),
        sub_category=data.get('sub_category'),
        product_name=data.get('product_name'),
        sales=float(data.get('sales')),
        quantity=int(data.get('quantity')),
        discount=float(data.get('discount')),
        profit=float(data.get('profit'))
    )
    db_session.add(nueva)
    db_session.commit()
    return jsonify({"mensaje": "Orden agregada correctamente"})

# Eliminar orden
@app.route('/del/order/<int:id>', methods=['DELETE'])
def eliminar_order(id):
    order = db_session.query(SuperstoreOrder).get(id)
    if order:
        db_session.delete(order)
        db_session.commit()
        return jsonify({"mensaje": "Eliminado correctamente"})
    return jsonify({"error": "Orden no encontrada"}), 404

# Actualizar orden
@app.route('/upd/order/<int:id>', methods=['PUT'])
def actualizar_order(id):
    data = request.json
    order = db_session.query(SuperstoreOrder).get(id)
    if not order:
        return jsonify({"error": "No encontrado"}), 404

    order.sales = float(data.get("sales"))
    order.quantity = int(data.get("quantity"))
    order.discount = float(data.get("discount"))
    order.profit = float(data.get("profit"))
    order.product_name = data.get("product_name")
    db_session.commit()
    return jsonify({"mensaje": "Actualizado correctamente"})

if __name__ == '__main__':
    app.run(debug=True)

##app.run(debug=True)
    port = int(os.environ.get("PORT", 5000))  # Render asigna el puerto dinámicamente
    app.run(host='0.0.0.0', port=port)
