# src/routes/admin.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from extensions import db
from sqlalchemy import or_, func
from models.usuario import Usuario
from models.objeto import Objeto
from models.categoria import Categoria
from models.incidencia import Incidencia
from models.reserva import Reserva
from models.pago import Pago
from models.opinion import Opinion
from datetime import datetime, date, timedelta

admin_bp = Blueprint("admin", __name__)


# ------------------- MIDDLEWARE -------------------
def admin_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or getattr(current_user, "id_rol", None) != 1:
            flash("No tienes permisos para acceder a esta sección", "error")
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)

    decorated_function.__name__ = f.__name__
    return decorated_function


# ------------------- DASHBOARD -------------------
@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    stats = {
        "total_usuarios": Usuario.query.count(),
        "total_objetos": Objeto.query.count(),
        "total_reservas": Reserva.query.count(),
        "total_categorias": Categoria.query.count(),
        "incidencias_pendientes": Incidencia.query.filter_by(estado="Abierta").count(),
        "ingresos_hoy": 0,
        "nuevos_usuarios_hoy": Usuario.query.filter(Usuario.fecha_registro == date.today()).count(),
        "nuevos_objetos_hoy": Objeto.query.filter(Objeto.fecha_publicacion == date.today()).count(),
        "reservas_hoy": Reserva.query.filter(Reserva.fecha_reserva == date.today()).count(),
    }

    actividad_reciente = [
        {
            "titulo": "Nuevo usuario registrado",
            "descripcion": "Usuario se registró en la plataforma",
            "fecha": datetime.now(),
            "tipo": "info",
        }
    ]

    usuarios_recientes = Usuario.query.order_by(Usuario.fecha_registro.desc()).limit(5).all()
    objetos_recientes = Objeto.query.order_by(Objeto.fecha_publicacion.desc()).limit(5).all()

    return render_template(
        "admin/dashboard.html",
        stats=stats,
        actividad_reciente=actividad_reciente,
        usuarios_recientes=usuarios_recientes,
        objetos_recientes=objetos_recientes,
        now=datetime.now(),
    )


# ------------------- USUARIOS -------------------
@admin_bp.route("/usuarios")
@login_required
@admin_required
def usuarios():
    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "", type=str)
    rol = request.args.get("rol", "", type=str)
    estado = request.args.get("estado", "", type=str)

    query = Usuario.query

    if search:
        like = f"%{search}%"
        query = query.filter(
            (Usuario.nombre.ilike(like)) |
            (Usuario.apellido.ilike(like)) |
            (Usuario.correo.ilike(like))
        )

    if rol:
        query = query.filter(Usuario.id_rol == int(rol))

    if estado:
        query = query.filter(Usuario.estado == estado)

    usuarios_paginados = query.order_by(Usuario.fecha_registro.desc()).paginate(page=page, per_page=10)

    return render_template("admin/usuarios.html", usuarios=usuarios_paginados)


@admin_bp.route("/usuarios/<int:id>/eliminar", methods=["POST"])
@login_required
@admin_required
def eliminar_usuario(id):
    usuario = Usuario.query.get_or_404(id)

    if usuario.id_rol == 1:
        flash("No se puede eliminar a un administrador.", "error")
        return redirect(url_for("admin.usuarios"))

    db.session.delete(usuario)
    db.session.commit()

    flash(f"Usuario {usuario.nombre} eliminado correctamente.", "success")
    return redirect(url_for("admin.usuarios"))


@admin_bp.route("/usuarios/<int:id>")
@login_required
@admin_required
def ver_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    return render_template("admin/ver_usuario.html", usuario=usuario)


@admin_bp.route("/usuarios/<int:id>/editar", methods=["GET", "POST"])
@login_required
@admin_required
def editar_usuario(id):
    usuario = Usuario.query.get_or_404(id)

    if request.method == "POST":
        usuario.nombre = request.form.get("nombre")
        usuario.apellido = request.form.get("apellido")
        usuario.correo = request.form.get("correo")
        usuario.telefono = request.form.get("telefono")
        id_rol = request.form.get("id_rol")
        usuario.id_rol = int(id_rol) if id_rol else usuario.id_rol
        db.session.commit()
        flash("Usuario actualizado correctamente", "success")
        return redirect(url_for("admin.usuarios"))

    return render_template("admin/editar_usuario.html", usuario=usuario)


# ------------------- CATEGORIAS -------------------
@admin_bp.route("/categorias")
@login_required
@admin_required
def categorias():
    categorias = Categoria.query.all()
    total_objetos = Objeto.query.count()

    categoria_mas_popular = None
    max_objetos = 0
    for categoria in categorias:
        cantidad = len(categoria.objetos)
        if cantidad > max_objetos:
            categoria_mas_popular = categoria
            max_objetos = cantidad

    categorias_sin_objetos = sum(1 for c in categorias if len(c.objetos) == 0)

    return render_template(
        "admin/categorias.html",
        categorias=categorias,
        total_objetos=total_objetos,
        categoria_mas_popular=categoria_mas_popular,
        categorias_sin_objetos=categorias_sin_objetos,
    )


@admin_bp.route("/categorias/crear", methods=["POST"])
@login_required
@admin_required
def crear_categoria():
    nombre = request.form.get("nombre")
    descripcion = request.form.get("descripcion", "")

    if not nombre:
        flash("El nombre de la categoría es requerido", "error")
        return redirect(url_for("admin.categorias"))

    if Categoria.query.filter_by(nombre=nombre).first():
        flash("Ya existe una categoría con ese nombre", "error")
        return redirect(url_for("admin.categorias"))

    nueva_categoria = Categoria(nombre=nombre, descripcion=descripcion)
    db.session.add(nueva_categoria)
    db.session.commit()

    flash("Categoría creada correctamente", "success")
    return redirect(url_for("admin.categorias"))


@admin_bp.route("/categorias/editar", methods=["POST"])
@login_required
@admin_required
def editar_categoria():
    categoria_id = request.form.get("categoria_id")
    nombre = request.form.get("nombre")
    descripcion = request.form.get("descripcion", "")

    categoria = Categoria.query.get_or_404(categoria_id)

    if not nombre:
        flash("El nombre es requerido", "error")
        return redirect(url_for("admin.categorias"))

    existe = Categoria.query.filter(Categoria.nombre == nombre, Categoria.id_categoria != categoria_id).first()
    if existe:
        flash("Ya existe otra categoría con ese nombre", "error")
        return redirect(url_for("admin.categorias"))

    categoria.nombre = nombre
    categoria.descripcion = descripcion
    db.session.commit()

    flash("Categoría actualizada correctamente", "success")
    return redirect(url_for("admin.categorias"))


@admin_bp.route("/categorias/<int:id>/eliminar", methods=["POST"])
@login_required
@admin_required
def eliminar_categoria(id):
    categoria = Categoria.query.get_or_404(id)

    if categoria.objetos:
        flash("No se puede eliminar una categoría con objetos.", "error")
        return redirect(url_for("admin.categorias"))

    db.session.delete(categoria)
    db.session.commit()

    flash("Categoría eliminada correctamente", "success")
    return redirect(url_for("admin.categorias"))


# ------------------- INCIDENCIAS -------------------
@admin_bp.route("/incidencias")
@login_required
@admin_required
def incidencias():
    estado = request.args.get("estado", "")
    query = Incidencia.query
    if estado:
        query = query.filter_by(estado=estado)

    incidencias = query.order_by(Incidencia.fecha_reporte.desc()).all()
    incidencias_pendientes = Incidencia.query.filter_by(estado="Abierta").count()

    return render_template("admin/incidencias.html", incidencias=incidencias, incidencias_pendientes=incidencias_pendientes)


@admin_bp.route("/incidencias/<int:id>/actualizar", methods=["POST"])
@login_required
@admin_required
def actualizar_incidencia(id):
    incidencia = Incidencia.query.get_or_404(id)
    nuevo_estado = request.form.get("nuevo_estado")
    if nuevo_estado not in ["Abierta", "En Proceso", "Resuelta"]:
        flash("Estado no válido", "error")
        return redirect(url_for("admin.incidencias"))
    incidencia.estado = nuevo_estado
    db.session.commit()
    flash("Incidencia actualizada correctamente", "success")
    return redirect(url_for("admin.incidencias"))


# ------------------- REPORTES -------------------
@admin_bp.route("/reportes")
@login_required
@admin_required
def reportes():
    # Leer parámetros GET
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")
    tipo_reporte = request.args.get("tipo", "general")

    # Fechas por defecto (últimos 30 días)
    fecha_fin = date.today()
    fecha_inicio = fecha_fin - timedelta(days=30)

    # Parsear fechas
    try:
        if start_date_str:
            fecha_inicio = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        if end_date_str:
            fecha_fin = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except Exception:
        flash("Formato de fecha inválido. Se usarán las fechas por defecto.", "error")

    if fecha_inicio > fecha_fin:
        fecha_inicio, fecha_fin = fecha_fin, fecha_inicio

    # Obtener datos para vista previa
    datos = obtener_datos_reporte(tipo_reporte, fecha_inicio, fecha_fin)

    return render_template(
        "admin/reportes.html",
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        tipo_reporte=tipo_reporte,
        datos=datos
    )


def obtener_datos_reporte(tipo, inicio, fin):
    """Helper para obtener datos según el tipo de reporte"""
    data = []
    
    if tipo == "usuarios":
        usuarios = Usuario.query.filter(Usuario.fecha_registro.between(inicio, fin)).all()
        for u in usuarios:
            data.append({
                "ID": u.id_usuario,
                "Nombre": f"{u.nombre} {u.apellido}",
                "Correo": u.correo,
                "Rol": "Administrador" if u.id_rol == 1 else "Usuario",
                "Fecha Registro": u.fecha_registro.strftime("%Y-%m-%d")
            })
            
    elif tipo == "transacciones":
        pagos = db.session.query(Pago, Reserva, Usuario).select_from(Pago).join(Reserva).join(Usuario).filter(Pago.fecha_pago.between(inicio, fin)).all()
        for p, r, u in pagos:
            data.append({
                "ID Pago": p.id_pago,
                "Fecha": p.fecha_pago.strftime("%Y-%m-%d"),
                "Usuario": f"{u.nombre} {u.apellido}",
                "Monto": f"RD$ {p.monto:,.2f}",
                "Método": p.metodo
            })

    elif tipo == "objetos":
        objetos = Objeto.query.filter(Objeto.fecha_publicacion.between(inicio, fin)).all()
        for o in objetos:
            data.append({
                "ID": o.id_objeto,
                "Nombre": o.nombre,
                "Categoría": o.categoria.nombre if o.categoria else "N/A",
                "Precio": f"RD$ {o.precio:,.2f}",
                "Estado": o.estado
            })
            
    elif tipo == "general":
        # Resumen general
        ingresos = db.session.query(func.sum(Pago.monto)).join(Reserva).filter(Pago.fecha_pago.between(inicio, fin)).scalar() or 0
        nuevos_usuarios = Usuario.query.filter(Usuario.fecha_registro.between(inicio, fin)).count()
        reservas = Reserva.query.filter(Reserva.fecha_reserva.between(inicio, fin)).count()
        
        data = [
            {"Métrica": "Ingresos Totales", "Valor": f"RD$ {ingresos:,.2f}"},
            {"Métrica": "Nuevos Usuarios", "Valor": nuevos_usuarios},
            {"Métrica": "Reservas Realizadas", "Valor": reservas},
            {"Métrica": "Periodo", "Valor": f"{inicio} al {fin}"}
        ]

    return data


# ------------------- EXPORTACIÓN -------------------
@admin_bp.route("/reportes/exportar/<string:formato>")
@login_required
@admin_required
def exportar_reporte(formato):
    import pandas as pd
    import io
    from flask import make_response

    # Obtener parámetros
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")
    tipo = request.args.get("tipo", "general")

    # Procesar fechas (igual que en vista)
    fecha_fin = date.today()
    fecha_inicio = fecha_fin - timedelta(days=30)
    try:
        if start_date_str:
            fecha_inicio = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        if end_date_str:
            fecha_fin = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except:
        pass

    # Obtener datos
    datos = obtener_datos_reporte(tipo, fecha_inicio, fecha_fin)
    
    if not datos:
        flash("No hay datos para exportar en este rango.", "warning")
        return redirect(url_for("admin.reportes"))

    # Crear DataFrame
    df = pd.DataFrame(datos)

    # Exportar según formato
    if formato == "csv":
        output = io.StringIO()
        df.to_csv(output, index=False)
        response = make_response(output.getvalue())
        response.headers["Content-Disposition"] = f"attachment; filename=reporte_{tipo}_{fecha_inicio}_{fecha_fin}.csv"
        response.headers["Content-type"] = "text/csv"
        return response

    elif formato == "excel":
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name="Reporte")
        output.seek(0)
        response = make_response(output.read())
        response.headers["Content-Disposition"] = f"attachment; filename=reporte_{tipo}_{fecha_inicio}_{fecha_fin}.xlsx"
        response.headers["Content-type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        return response

    elif formato == "pdf":
        try:
            from xhtml2pdf import pisa
            
            html_content = render_template(
                "admin/reporte_pdf.html", 
                datos=datos, 
                tipo=tipo, 
                inicio=fecha_inicio, 
                fin=fecha_fin,
                now=datetime.now()
            )
            
            output = io.BytesIO()
            pisa_status = pisa.CreatePDF(
                html_content, dest=output
            )
            
            if pisa_status.err:
                flash("Error generando PDF", "error")
                return redirect(url_for("admin.reportes"))
                
            output.seek(0)
            response = make_response(output.read())
            response.headers["Content-Disposition"] = f"attachment; filename=reporte_{tipo}_{fecha_inicio}_{fecha_fin}.pdf"
            response.headers["Content-type"] = "application/pdf"
            return response
            
        except ImportError:
            flash("Error: Librería de PDF no instalada correctamente.", "error")
            return redirect(url_for("admin.reportes"))
        except Exception as e:
            flash(f"Error generando PDF: {str(e)}", "error")
            return redirect(url_for("admin.reportes"))

    return redirect(url_for("admin.reportes"))


# ------------------- CONFIGURACIÓN -------------------
@admin_bp.route("/configuracion")
@login_required
@admin_required
def configuracion():
    return render_template("admin/configuracion.html")


@admin_bp.route("/configuracion/guardar", methods=["POST"])
@login_required
@admin_required
def guardar_configuracion():
    flash("Configuración guardada correctamente", "success")
    return redirect(url_for("admin.configuracion"))


# ------------------- API LIVE STATS -------------------
@admin_bp.route("/api/estadisticas")
@login_required
@admin_required
def api_estadisticas():
    stats = {
        "total_usuarios": Usuario.query.count(),
        "total_objetos": Objeto.query.count(),
        "total_reservas": Reserva.query.count(),
        "incidencias_pendientes": Incidencia.query.filter_by(estado="Abierta").count(),
        "nuevos_usuarios_hoy": Usuario.query.filter(Usuario.fecha_registro == date.today()).count()
    }
    return jsonify(stats)
