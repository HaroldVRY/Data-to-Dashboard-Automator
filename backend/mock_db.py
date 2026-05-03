"""
Mock database generator for testing.
Creates SQLite database with sample data for Users, Transactions, and Products.
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, timedelta
import random

# Create base class for declarative models
Base = declarative_base()


# Define database models
class Usuario(Base):
    """User table model."""
    __tablename__ = 'usuarios'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    pais = Column(String(50), nullable=False)
    
    # Relationship with transactions
    transacciones = relationship("Transaccion", back_populates="usuario")


class Producto(Base):
    """Product table model."""
    __tablename__ = 'productos'
    
    id_producto = Column(Integer, primary_key=True, autoincrement=True)
    nombre_producto = Column(String(100), nullable=False)
    categoria = Column(String(50), nullable=False)
    precio = Column(Float, nullable=False)
    
    # Relationship with transactions
    transacciones = relationship("Transaccion", back_populates="producto")


class Transaccion(Base):
    """Transaction table model."""
    __tablename__ = 'transacciones'
    
    id_transaccion = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    id_producto = Column(Integer, ForeignKey('productos.id_producto'), nullable=False)
    monto = Column(Float, nullable=False)
    fecha_compra = Column(Date, nullable=False)
    
    # Relationships
    usuario = relationship("Usuario", back_populates="transacciones")
    producto = relationship("Producto", back_populates="transacciones")


def init_db():
    """
    Initialize database with tables and sample data.
    Creates test_data.db file in backend directory.
    """
    # Create database engine
    engine = create_engine('sqlite:///backend/test_data.db', echo=True)
    
    # Create all tables
    Base.metadata.drop_all(engine)  # Drop existing tables
    Base.metadata.create_all(engine)
    
    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Insert sample users
        usuarios = [
            Usuario(nombre="Juan Pérez", email="juan.perez@email.com", pais="Colombia"),
            Usuario(nombre="María García", email="maria.garcia@email.com", pais="México"),
            Usuario(nombre="Carlos Rodríguez", email="carlos.rodriguez@email.com", pais="Argentina"),
            Usuario(nombre="Ana Martínez", email="ana.martinez@email.com", pais="España"),
            Usuario(nombre="Luis Hernández", email="luis.hernandez@email.com", pais="Colombia"),
            Usuario(nombre="Sofia López", email="sofia.lopez@email.com", pais="Chile"),
            Usuario(nombre="Diego Torres", email="diego.torres@email.com", pais="Perú"),
            Usuario(nombre="Laura Ramírez", email="laura.ramirez@email.com", pais="México"),
            Usuario(nombre="Pedro Sánchez", email="pedro.sanchez@email.com", pais="España"),
            Usuario(nombre="Carmen Díaz", email="carmen.diaz@email.com", pais="Colombia"),
        ]
        session.add_all(usuarios)
        session.commit()
        print(f"✓ Inserted {len(usuarios)} users")
        
        # Insert sample products
        productos = [
            Producto(nombre_producto="Laptop Dell XPS 15", categoria="Electrónica", precio=1299.99),
            Producto(nombre_producto="iPhone 14 Pro", categoria="Electrónica", precio=999.99),
            Producto(nombre_producto="Samsung Galaxy S23", categoria="Electrónica", precio=849.99),
            Producto(nombre_producto="Auriculares Sony WH-1000XM5", categoria="Audio", precio=349.99),
            Producto(nombre_producto="Teclado Mecánico Logitech", categoria="Accesorios", precio=129.99),
            Producto(nombre_producto="Monitor LG 27 pulgadas", categoria="Electrónica", precio=299.99),
            Producto(nombre_producto="Mouse Logitech MX Master 3", categoria="Accesorios", precio=99.99),
            Producto(nombre_producto="Webcam Logitech C920", categoria="Accesorios", precio=79.99),
            Producto(nombre_producto="Tablet iPad Air", categoria="Electrónica", precio=599.99),
            Producto(nombre_producto="Smartwatch Apple Watch Series 8", categoria="Wearables", precio=399.99),
        ]
        session.add_all(productos)
        session.commit()
        print(f"✓ Inserted {len(productos)} products")
        
        # Insert sample transactions (distributed over last 6 months)
        transacciones = []
        base_date = datetime.now()
        
        # Generate 30 realistic transactions
        transaction_data = [
            (1, 1, 1299.99, -150),  # Juan bought Laptop 5 months ago
            (2, 2, 999.99, -120),   # María bought iPhone 4 months ago
            (3, 3, 849.99, -90),    # Carlos bought Samsung 3 months ago
            (1, 4, 349.99, -80),    # Juan bought Headphones
            (4, 5, 129.99, -70),    # Ana bought Keyboard
            (5, 6, 299.99, -60),    # Luis bought Monitor
            (2, 7, 99.99, -50),     # María bought Mouse
            (6, 8, 79.99, -45),     # Sofia bought Webcam
            (7, 9, 599.99, -40),    # Diego bought iPad
            (3, 10, 399.99, -35),   # Carlos bought Apple Watch
            (8, 1, 1299.99, -30),   # Laura bought Laptop
            (9, 2, 999.99, -25),    # Pedro bought iPhone
            (10, 4, 349.99, -20),   # Carmen bought Headphones
            (4, 6, 299.99, -15),    # Ana bought Monitor
            (5, 7, 99.99, -10),     # Luis bought Mouse
            (6, 3, 849.99, -8),     # Sofia bought Samsung
            (7, 5, 129.99, -6),     # Diego bought Keyboard
            (8, 8, 79.99, -4),      # Laura bought Webcam
            (9, 9, 599.99, -3),     # Pedro bought iPad
            (10, 10, 399.99, -2),   # Carmen bought Apple Watch
            (1, 7, 99.99, -1),      # Juan bought Mouse recently
            (2, 5, 129.99, -1),     # María bought Keyboard recently
            (3, 8, 79.99, 0),       # Carlos bought Webcam today
            (4, 2, 999.99, -90),    # Ana bought iPhone 3 months ago
            (5, 1, 1299.99, -100),  # Luis bought Laptop
            (6, 6, 299.99, -75),    # Sofia bought Monitor
            (7, 4, 349.99, -65),    # Diego bought Headphones
            (8, 3, 849.99, -55),    # Laura bought Samsung
            (9, 10, 399.99, -48),   # Pedro bought Apple Watch
            (10, 9, 599.99, -38),   # Carmen bought iPad
        ]
        
        for id_usuario, id_producto, monto, days_offset in transaction_data:
            fecha = (base_date + timedelta(days=days_offset)).date()
            transaccion = Transaccion(
                id_usuario=id_usuario,
                id_producto=id_producto,
                monto=monto,
                fecha_compra=fecha
            )
            transacciones.append(transaccion)
        
        session.add_all(transacciones)
        session.commit()
        print(f"✓ Inserted {len(transacciones)} transactions")
        
        print("\n" + "="*50)
        print("✓ Database initialized successfully!")
        print(f"✓ Location: backend/test_data.db")
        print(f"✓ Total records: {len(usuarios)} users, {len(productos)} products, {len(transacciones)} transactions")
        print("="*50)
        
    except Exception as e:
        session.rollback()
        print(f"✗ Error initializing database: {str(e)}")
        raise
    finally:
        session.close()


def print_sample_queries():
    """Print sample SQL queries that can be tested with this database."""
    print("\n" + "="*50)
    print("SAMPLE QUERIES TO TEST:")
    print("="*50)
    
    queries = [
        "Show all users from Colombia",
        "List products in the Electronics category",
        "Show total sales by country",
        "Find users who spent more than $1000",
        "Show monthly sales for the last 6 months",
        "List top 5 best-selling products",
        "Show users who bought iPhones",
        "Calculate average transaction amount by category",
        "Find products never purchased",
        "Show users with multiple purchases"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"{i}. {query}")
    
    print("="*50 + "\n")


if __name__ == "__main__":
    print("\n" + "="*50)
    print("INITIALIZING MOCK DATABASE")
    print("="*50 + "\n")
    
    init_db()
    print_sample_queries()

# Made with Bob
