from sqlalchemy import Column, Integer, String, ForeignKey, Date, Numeric, Text, Sequence, DateTime, SmallInteger,func, Float

from sqlalchemy.orm import relationship, declarative_base
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

Base= declarative_base()

class SuperstoreOrder(Base):
    __tablename__ = 'superstore_orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    no = Column(Integer, nullable=False)
    row_id = Column(Integer, nullable=False)
    order_id = Column(String(20), nullable=False)
    order_date = Column(Date, nullable=False)
    ship_date = Column(Date, nullable=False)
    ship_mode = Column(String(50), nullable=False)
    customer_id = Column(String(20), nullable=False)
    customer_name = Column(String(100), nullable=False)
    segment = Column(String(50), nullable=False)
    country = Column(String(50), nullable=False)
    city = Column(String(50), nullable=False)
    state = Column(String(50), nullable=False)
    postal_code = Column(String(20))
    region = Column(String(50), nullable=False)
    product_id = Column(String(20), nullable=False)
    category = Column(String(50), nullable=False)
    sub_category = Column(String(50), nullable=False)
    product_name = Column(String(255), nullable=False)
    sales = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    discount = Column(Float, nullable=False)
    profit = Column(Float, nullable=False)

    def __repr__(self):
        return f"<superstore_orders(name='{self.name}', platform='{self.platform}')>"

from flask_login import UserMixin

class Usuario(Base, UserMixin):
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

