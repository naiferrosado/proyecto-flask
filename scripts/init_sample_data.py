import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from models.categoria import Categoria


def init_sample_data():
    print("🔄 Inicializando datos de ejemplo...")

    app = create_app()

    with app.app_context():
        # Crear categorías de ejemplo si no existen
        categorias = [
            "Herramientas",
            "Electrodomésticos",
            "Deportes",
            "Eventos y Fiestas",
            "Tecnología",
            "Hogar y Jardín",
            "Ropa y Accesorios",
            "Otros",
        ]

        for i, nombre in enumerate(categorias, 1):
            if not Categoria.query.filter_by(nombre=nombre).first():
                categoria = Categoria(
                    id_categoria=i,
                    nombre=nombre,
                    descripcion=f"Categoría de {nombre.lower()}",
                )
                db.session.add(categoria)

        db.session.commit()
        print("✅ Categorías inicializadas correctamente")


if __name__ == "__main__":
    init_sample_data()
