import pandas as pd
from sqlalchemy import create_engine
import os
import sys
from datetime import datetime

# Agrega el path al directorio raíz del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.model import Base, SuperstoreOrder
from sqlalchemy.orm import sessionmaker

# Configura tu conexión
DATABASE_URL = "postgresql://postgres:123456@localhost:5432/superstore_orders"  # ← cámbialo si es necesario

# Crear engine y sesión
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Crear tablas si no existen
Base.metadata.create_all(engine)

# Leer el CSV con pandas
CSV_URL = "https://raw.githubusercontent.com/rudyluis/DashboardJS/refs/heads/main/superstore_data.csv"
df = pd.read_csv(CSV_URL)

# Convertir fechas
df['OrderDate'] = pd.to_datetime(df['OrderDate'], format='%m/%d/%Y')
df['ShipDate'] = pd.to_datetime(df['ShipDate'], format='%m/%d/%Y')

# Convertir DataFrame en lista de objetos SuperstoreOrder
records = [
    SuperstoreOrder(
        no=int(row['No']),
        row_id=int(row['RowID']),
        order_id=row['OrderID'],
        order_date=row['OrderDate'].date(),
        ship_date=row['ShipDate'].date(),
        ship_mode=row['ShipMode'],
        customer_id=row['CustomerID'],
        customer_name=row['CustomerName'],
        segment=row['Segment'],
        country=row['Country'],
        city=row['City'],
        state=row['State'],
        postal_code=str(row['Postal Code']) if not pd.isna(row['Postal Code']) else None,
        region=row['Region'],
        product_id=row['ProductID'],
        category=row['Category'],
        sub_category=row['Sub-Category'],
        product_name=row['ProductName'],
        sales=float(row['Sales']),
        quantity=int(row['Quantity']),
        discount=float(row['Discount']),
        profit=float(row['Profit'])
    )
    for index, row in df.iterrows()
]

# Insertar en la base de datos
session.bulk_save_objects(records)
session.commit()
print("✅ Migración de datos de Superstore completada")
session.close()
