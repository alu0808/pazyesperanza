import os
from datetime import datetime, timezone
from flask import Flask, jsonify, logging, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import func
import logging
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from functools import wraps
from urllib.parse import urlparse, urljoin
import json 

app = Flask(__name__)

# Configuración del logging
if not app.debug:
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)  # Configura el nivel de logging como INFO
    app.logger.addHandler(stream_handler)

app.config['SECRET_KEY'] = 'fhg563235453663434576377355246362463634573t32erf'

# Configuración de la conexión a la base de datos ewn heroku y en PC local

if os.getenv('DATABASE_URL'):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL').replace("postgres://", "postgresql+psycopg2://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:Qsdxc.1221@localhost/pazyesperanza'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)
# Después de la configuración de la base de datos (db = SQLAlchemy(app))
migrate = Migrate(app, db)

# Inicializar el gestor de sesiones de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirige a la vista de login si no está autenticado

# Crear las tablas en la base de datos
with app.app_context():
    db.create_all()
    

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(100), nullable=False)  # Rol: admin, editor, viewer

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)




@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Función para verificar que la URL sea segura
def is_safe_url(target):
    host_url = urlparse(request.host_url)
    redirect_url = urlparse(urljoin(request.host_url, target))
    return redirect_url.scheme in ('http', 'https') and host_url.netloc == redirect_url.netloc

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        # # NUEVO USUARIO:
        # new_user = User(username='admin', role='admin')
        # new_user.set_password('admin')  # Cambia la contraseña a algo seguro

        # # Añadir el usuario a la base de datos
        # db.session.add(new_user)
        # db.session.commit()

        if user and user.check_password(password):
            login_user(user)
            # flash('Sesión iniciada correctamente', 'success')

            # Verificar si `next` está presente y es segura
            next_page = request.args.get('next')
            if next_page and is_safe_url(next_page):
                return redirect(next_page)

            # Si `next` no es válido o no existe, redirige a la página principal
            return redirect(url_for('index'))

        else:
            flash('Nombre de usuario o contraseña incorrectos', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('login'))

def roles_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Debe iniciar sesión para acceder a esta página", "danger")
                return redirect(url_for('login', next=request.url))  # Redirige al login si no está autenticado
            # elif current_user.role not in roles:
            #     flash("No tiene permisos para acceder a esta página", "danger")
            #     return redirect(request.referrer or url_for('index')) 
            elif current_user.role not in roles:
                flash("No tiene permisos para acceder a esta página", "danger")
                return redirect(url_for('index'))  # Redirige al index si no tiene permisos
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Ruta para listar todos los usuarios
@app.route('/admin', methods=['GET'])
@login_required
@roles_required('admin')
def admin_dashboard():
    if not current_user.is_authenticated:
        return redirect(url_for('login', next=request.url))
    users = User.query.all()
    return render_template('admin_dashboard.html', users=users)

# Ruta para crear un nuevo usuario
@app.route('/create_user', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def create_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        new_user = User(username=username, role=role)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()
        flash('Usuario creado exitosamente.', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('create_user.html')

# Ruta para editar un usuario
@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def edit_user(user_id):
    user = User.query.get(user_id)
    if not user:
        flash('Usuario no encontrado.', 'danger')
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        user.username = request.form['username']
        user.role = request.form['role']
        if request.form['password']:
            user.set_password(request.form['password'])

        db.session.commit()
        flash('Usuario actualizado exitosamente.', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('edit_user.html', user=user)

# Ruta para eliminar un usuario
@app.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
@roles_required('admin')
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        flash('Usuario no encontrado.', 'danger')
        return redirect(url_for('admin_dashboard'))

    db.session.delete(user)
    db.session.commit()
    flash('Usuario eliminado exitosamente.', 'success')
    return redirect(url_for('admin_dashboard'))


########################################################################################################################################
########################################################################################################################################
##########                 INDEX BASE DE MENU                ###########################################################################
########################################################################################################################################
########################################################################################################################################
@app.route('/', methods=['GET'])
@login_required
@roles_required('admin', 'editor', 'viewer')  # Solo los usuarios con rol 'admin' pueden acceder
def index():
    return render_template('index.html')  # Nuevo index.html con opciones para navegar

def validar_longitud(campo, valor, max_length):
    if len(valor.strip()) > max_length:
        flash(f'El campo "{campo}" no debe exceder los {max_length} caracteres.', 'danger')
        return False
    return True


########################################################################################################################################
########################################################################################################################################
##########                 REGISTRO INICIAL PARTICIPANTES              #################################################################
########################################################################################################################################
########################################################################################################################################
# TABLA RELACION ENTRE REGISTRO E INICIATIVAS
iniciativa_registro = db.Table(
    'iniciativa_registro',
    db.Column('iniciativa_nombre', db.String(150), db.ForeignKey('iniciativa.nombre_iniciativa'), primary_key=True),
    db.Column('registro_dni', db.String(20), db.ForeignKey('registro.dni'), primary_key=True)
)
import pytz
PERU_TZ = pytz.timezone("America/Lima")

def obtener_hora_peru():
    # Obtener la hora actual en UTC y luego convertir a la zona horaria de Perú
    return datetime.now(timezone.utc).astimezone(PERU_TZ)

# Definición del modelo de datos
class Registro(db.Model):
    dni = db.Column(db.String(20), primary_key=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False) 
    edad = db.Column(db.Integer, nullable=True)  # Permitir NULL
    sexo = db.Column(db.String(10), nullable=True)
    lugar_nacimiento = db.Column(db.String(60), nullable=True)
    calle = db.Column(db.String(60), nullable=True)
    comunidad = db.Column(db.String(60), nullable=True)
    distrito = db.Column(db.String(100), nullable=True)
    provincia = db.Column(db.String(60), nullable=True)
    departamento = db.Column(db.String(60), nullable=True)
    estado = db.Column(db.String(3), nullable=True, default='ACT')  # Valor predeterminado "ACT"
    fecha_registro = db.Column(db.DateTime, default=obtener_hora_peru, nullable=True)

@app.route('/form_registro_inicial', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def form_registro_inicial():
    if request.method == 'POST':
        # Validación del DNI y eliminación de espacios en blanco
        dni = request.form['dni'].strip()

        # Verificar si el DNI ya existe
        if Registro.query.filter_by(dni=dni).first():
            flash('Este DNI ya ha sido registrado.', 'danger')
            return redirect(url_for('listar_registros'))
        
        # Crear una nueva instancia de Registro con los datos del formulario
        nuevo_registro = Registro(
            dni=dni,
            nombre=request.form['nombre'],
            edad=request.form.get('edad', None) or None,  # Aplica solo para enteros
            sexo=request.form.get('sexo', ''),
            lugar_nacimiento=request.form.get('lugar_nacimiento', ''),
            calle=request.form.get('calle', ''),
            comunidad=request.form.get('comunidad', ''),
            distrito=request.form.get('distrito', ''),
            provincia=request.form.get('provincia', ''),
            departamento=request.form.get('departamento', ''),
            estado=request.form.get('estado', 'ACT')
            # poblacion_titular=", ".join(request.form.getlist('poblacion_titular')),
            # otro_poblacion=request.form.get('otro_poblacion', ''),
            # derecho_prioritario=", ".join(request.form.getlist('derecho_prioritario')),
            # otro_derecho=request.form.get('otro_derecho', ''),
            # oficina_regional=request.form.get('oficina_regional', ''),
            # proyectos=request.form.get('proyectos', ''),
            # tipo_servicios=", ".join(request.form.getlist('tipo_servicios')),
            # servicio_actividad=request.form.get('servicio_actividad', ''),
            # fecha_participacion=request.form.get('fecha_participacion', '') or None,  # Aplica solo para fechas
            # propuesta_agenda=request.form.get('propuesta_agenda', ''),
            # agenda_detalle=request.form.get('agenda_detalle', ''),
            # red_colectivo=request.form.get('red_colectivo', ''),
            # red_detalle=request.form.get('red_detalle', ''),
            # comunidad_fe=request.form.get('comunidad_fe', ''),
            # fe_detalle=request.form.get('fe_detalle', ''),
            # tipo_participacion_fe=request.form.get('tipo_participacion_fe', '')
        )
        # Guardar el nuevo registro en la base de datos
        db.session.add(nuevo_registro)
        db.session.commit()

        flash('Registro exitoso.', 'success')
        return redirect(url_for('listar_registros'))

    return render_template('form_registro_inicial.html')

# LISTAR REGISTROS
@app.route('/listar_registros', methods=['GET'])
@login_required
@roles_required('admin', 'editor', 'viewer')
def listar_registros():
    registros = Registro.query.order_by(Registro.fecha_registro.desc()).all()  # Ordenar por fecha de registro (descendente)
    return render_template('listar_registros.html', registros=registros)


################################################################################################################################
################################################################################################################################
#EDITAR REGISTROS INICIALES
@app.route('/editar_registro/<dni>', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'editor')
def editar_registro(dni):
    # Obtener el registro existente usando el DNI
    registro = Registro.query.filter_by(dni=dni).first()

    if not registro:
        flash('El registro no existe.', 'danger')
        return redirect(url_for('listar_registros'))

    if request.method == 'POST':
        # Actualizar los campos del registro con los datos enviados desde el formulario
        registro.nombre = request.form['nombre']
        registro.edad = request.form.get('edad', None) or None
        registro.sexo = request.form.get('sexo', '')
        registro.lugar_nacimiento = request.form.get('lugar_nacimiento', '')
        registro.calle = request.form.get('calle', '')
        registro.comunidad = request.form.get('comunidad', '')
        registro.distrito = request.form.get('distrito', '')
        registro.provincia = request.form.get('provincia', '')
        registro.departamento = request.form.get('departamento', '')
        registro.estado = request.form.get('estado', 'ACT')
        # registro.poblacion_titular = ", ".join(request.form.getlist('poblacion_titular'))
        # registro.otro_poblacion = request.form.get('otro_poblacion', '')
        # registro.derecho_prioritario = ", ".join(request.form.getlist('derecho_prioritario'))
        # registro.otro_derecho = request.form.get('otro_derecho', '')
        # registro.oficina_regional = request.form.get('oficina_regional', '')
        # registro.proyectos = request.form.get('proyectos', '')
        # registro.tipo_servicios = ", ".join(request.form.getlist('tipo_servicios'))
        # registro.servicio_actividad = request.form.get('servicio_actividad', '')
        # registro.fecha_participacion = request.form.get('fecha_participacion', '') or None
        # registro.propuesta_agenda = request.form.get('propuesta_agenda', '')
        # registro.agenda_detalle = request.form.get('agenda_detalle', '')
        # registro.red_colectivo = request.form.get('red_colectivo', '')
        # registro.red_detalle = request.form.get('red_detalle', '')
        # registro.comunidad_fe = request.form.get('comunidad_fe', '')
        # registro.fe_detalle = request.form.get('fe_detalle', '')
        # registro.tipo_participacion_fe = request.form.get('tipo_participacion_fe', '')
        # registro.capacidad_1 = request.form.get('capacidad_1', None) or None
        # registro.capacidad_2 = request.form.get('capacidad_2', None) or None
        # registro.capacidad_3 = request.form.get('capacidad_3', None) or None
        # registro.capacidad_4 = request.form.get('capacidad_4', None) or None
        # registro.capacidad_5 = request.form.get('capacidad_5', None) or None
        # registro.otra_capacidad = request.form.get('otra_capacidad', '')
        # registro.calificacion_otra_capacidad = request.form.get('calificacion_otra_capacidad', None) or None

        # Guardar los cambios en la base de datos
        db.session.commit()

        flash('El registro ha sido actualizado con éxito.', 'success')
        return redirect(url_for('listar_registros'))

    # Renderizar el formulario con los datos del registro existente
    return render_template('editar_registro.html', registro=registro)

#ELIMINAR REGISTROS INICIALES
@app.route('/eliminar_registro/<dni>', methods=['POST'])
@login_required
@roles_required('admin')
def eliminar_registro(dni):
    # Buscar el registro por DNI
    registro = Registro.query.filter_by(dni=dni).first()

    if not registro:
        flash('El registro no existe.', 'danger')
        return redirect(url_for('listar_registros'))
    
    
    # # Validar si el participante está asociado a alguna iniciativa
    # if registro.iniciativas:
    #     flash("El participante no puede ser eliminado porque está asociado a una o más iniciativas.", "danger")
    #     return redirect(url_for('listar_registros'))
    
    # # Verificar si el participante tiene capacidades relacionadas
    # if registro.capacidades:  # Asegúrate de que la relación esté configurada como backref
    #     flash('No se puede eliminar el participante porque tiene capacidades relacionadas.', 'danger')
    #     return redirect(url_for('listar_registros'))

    try:
        # Marcar el registro como inactivo
        registro.estado = 'INA'  # INA = Inactivo
        db.session.commit()
        flash("El participante ha sido marcado como inactivo.", "success")
        # Eliminar el registro de la base de datos
        # db.session.delete(registro)
        # db.session.commit()
        # flash('El registro ha sido eliminado con éxito.', 'success')
    except Exception as e:
        # Si ocurre un error, lo gestionamos
        db.session.rollback()
        flash(f'Ocurrió un error al eliminar el registro: {e}', 'danger')

    return redirect(url_for('listar_registros'))

########################################################################################################################################
########################################################################################################################################
##########              REGISTRO INICIATIVAS            ################################################################################
########################################################################################################################################
########################################################################################################################################
# Definición del modelo de datos para Iniciativa
class Iniciativa(db.Model):
    nombre_iniciativa = db.Column(db.String(150), primary_key=True)
    derecho_generico = db.Column(db.String(80), nullable=True)
    otro_derecho_detalle = db.Column(db.String(60), nullable=True)
    colectivo_organizacion = db.Column(db.String(80), nullable=True)
    poblacion = db.Column(db.String(300), nullable=True)
    total_hombres_ninos = db.Column(db.Integer, nullable=True)
    total_mujeres_ninos = db.Column(db.Integer, nullable=True)
    total_hombres_adolescentes = db.Column(db.Integer, nullable=True)
    total_mujeres_adolescentes = db.Column(db.Integer, nullable=True)
    total_hombres_jovenes = db.Column(db.Integer, nullable=True)
    total_mujeres_jovenes = db.Column(db.Integer, nullable=True)
    total_hombres_mujeres = db.Column(db.Integer, nullable=True)  # Para mujeres, se puede dejar en blanco para hombres
    total_mujeres_mujeres = db.Column(db.Integer, nullable=True)
    total_hombres_discapacidad = db.Column(db.Integer, nullable=True)
    total_mujeres_discapacidad = db.Column(db.Integer, nullable=True)
    total_hombres_migrantes = db.Column(db.Integer, nullable=True)
    total_mujeres_migrantes = db.Column(db.Integer, nullable=True)
    total_hombres_amazonicas = db.Column(db.Integer, nullable=True)
    total_mujeres_amazonicas = db.Column(db.Integer, nullable=True)
    total_hombres_periurbanas = db.Column(db.Integer, nullable=True)
    total_mujeres_periurbanas = db.Column(db.Integer, nullable=True)
    total_hombres_conflicto = db.Column(db.Integer, nullable=True)
    total_mujeres_conflicto = db.Column(db.Integer, nullable=True)
    otra_poblacion_detalle = db.Column(db.String(80), nullable=True)
    total_hombres_otra = db.Column(db.Integer, nullable=True)
    total_mujeres_otra = db.Column(db.Integer, nullable=True)
    tipo_naturaleza = db.Column(db.String(350), nullable=True)
    cambio_politica_detalle = db.Column(db.String(100), nullable=True)  # Detalles del cambio en política pública
    cambio_marcos_detalle = db.Column(db.String(100), nullable=True)  # Detalles del cambio en marcos normativos
    cambio_practicas_detalle = db.Column(db.String(100), nullable=True)  # Detalles del cambio en prácticas de entidades privadas
    cambio_sensibilidad_detalle = db.Column(db.String(100), nullable=True)  # Detalles del cambio en prácticas sociales
    otro_naturaleza_detalle = db.Column(db.String(100), nullable=True)
    otro_naturaleza_particular = db.Column(db.String(100), nullable=True)
    sector_publico_competente_1 = db.Column(db.String(70), nullable=True)
    dependencia_instancia_1 = db.Column(db.String(70), nullable=True)
    alcance_escala_1 = db.Column(db.String(50), nullable=True)
    sector_publico_competente_2 = db.Column(db.String(70), nullable=True)
    dependencia_instancia_2 = db.Column(db.String(70), nullable=True)
    alcance_escala_2 = db.Column(db.String(50), nullable=True)
    localidad_1 = db.Column(db.String(60), nullable=True)
    localidad_2 = db.Column(db.String(60), nullable=True)
    localidad_3 = db.Column(db.String(60), nullable=True)
    descripcion_situacion = db.Column(db.String(255), nullable=True)
    objetivo_especifico = db.Column(db.String(255), nullable=True)
    campos = db.Column(db.String(500), nullable=True)
    campo_otro_detalle = db.Column(db.String(80), nullable=True)
    componente_1 = db.Column(db.String(100), nullable=True)
    componente_2 = db.Column(db.String(100), nullable=True)
    componente_3 = db.Column(db.String(100), nullable=True)
    oficina_regional = db.Column(db.String(60), nullable=True)
    proyectos = db.Column(db.String(100), nullable=True)
    tipo_participacion_fe = db.Column(db.String(80), nullable=True)
    contenido_1 = db.Column(db.Integer, nullable=True)
    contenido_2 = db.Column(db.Integer, nullable=True)
    contenido_3 = db.Column(db.Integer, nullable=True)
    contenido_4 = db.Column(db.Integer, nullable=True)
    contenido_5 = db.Column(db.Integer, nullable=True)
    contenido_6 = db.Column(db.Integer, nullable=True)
    contenido_7 = db.Column(db.Integer, nullable=True)
    contenido_otro = db.Column(db.String(80), nullable=True)
    calificacion_otro_contenido = db.Column(db.Integer, nullable=True)
    fase_implementacion = db.Column(db.Integer)  # Representa el valor 0-9 según la selección
    fase_normas_detalle = db.Column(db.String(100), nullable=True)
    fase_institucionalizacion_detalle = db.Column(db.String(100), nullable=True)
    fase_otro_detalle = db.Column(db.String(100), nullable=True)
    actividad_1 = db.Column(db.String(150), nullable=True)
    actividad_2 = db.Column(db.String(150), nullable=True)
    actividad_3 = db.Column(db.String(150), nullable=True)
    actividad_4 = db.Column(db.String(150), nullable=True)
    actividad_5 = db.Column(db.String(150), nullable=True)
    proyecto_1 = db.Column(db.String(150), nullable=True)
    fuente_financiamiento_1 = db.Column(db.String(100), nullable=True)
    financiamiento_1 = db.Column(db.Integer, nullable=True)
    periodo_financiamiento_1 = db.Column(db.String(100), nullable=True)
    proyecto_2 = db.Column(db.String(150), nullable=True)
    fuente_financiamiento_2 = db.Column(db.String(100), nullable=True)
    financiamiento_2 = db.Column(db.Integer, nullable=True)
    periodo_financiamiento_2 = db.Column(db.String(100), nullable=True)
    observaciones = db.Column(db.String(255), nullable=True)
    responsable_registro = db.Column(db.String(100), nullable=True)
    tipo_participacion_fe = db.Column(db.String(80), nullable=True)
    fecha_registro = db.Column(db.DateTime, default=obtener_hora_peru, nullable=True)
    # Relación con múltiples registros mediante tabla intermedia
    registros = db.relationship(
        'Registro',
        secondary='iniciativa_registro',  # Nombre de la tabla intermedia
        backref=db.backref('iniciativas', lazy=True),
        lazy=True
    )
    # Relación con ProcesoIniciativa
    procesos = db.relationship('ProcesoIniciativa', backref='iniciativa', lazy=True, cascade="all, delete-orphan")

@app.route('/form_iniciativas', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def form_iniciativas():
    if request.method == 'POST':
        nombre_iniciativa = request.form['nombre_iniciativa'].strip().lower()
        # Obtener los DNIs seleccionados
        registros_seleccionados = request.form.get('registros', '')  # Lista de DNIs seleccionados

        if Iniciativa.query.filter(func.lower(Iniciativa.nombre_iniciativa) == nombre_iniciativa).first():
            flash('Esta Iniciativa ya ha sido registrada.', 'danger')
            return redirect(url_for('listar_iniciativas'))
        
        # Procesar la fase de implementación seleccionada
        fase_implementacion = request.form.get('fase_implementacion', None)  # Valor de 0-9 o "otro"
        if fase_implementacion == "":
            fase_implementacion = None  # O usa un valor por defecto como 0

        if not fase_implementacion:
            flash('Debe seleccionar una fase de implementación.', 'danger')
            return redirect(url_for('form_iniciativas'))

        nueva_iniciativa = Iniciativa(
            nombre_iniciativa=nombre_iniciativa,
            derecho_generico=request.form.get('derecho_generico', ''),
            otro_derecho_detalle=request.form.get('otro_derecho_detalle', ''),
            colectivo_organizacion=request.form.get('colectivo_organizacion', ''),
            poblacion=request.form.get('poblacion', ''),
            total_hombres_ninos=request.form.get('total_hombres_ninos', None) or None,
            total_mujeres_ninos=request.form.get('total_mujeres_ninos', None) or None,
            total_hombres_adolescentes=request.form.get('total_hombres_adolescentes', None) or None,
            total_mujeres_adolescentes=request.form.get('total_mujeres_adolescentes', None) or None,
            total_hombres_jovenes=request.form.get('total_hombres_jovenes', None) or None,
            total_mujeres_jovenes=request.form.get('total_mujeres_jovenes', None) or None,
            total_hombres_mujeres=request.form.get('total_hombres_mujeres', None) or None,
            total_mujeres_mujeres=request.form.get('total_mujeres_mujeres', None) or None,
            total_hombres_discapacidad=request.form.get('total_hombres_discapacidad', None) or None,
            total_mujeres_discapacidad=request.form.get('total_mujeres_discapacidad', None) or None,
            total_hombres_migrantes=request.form.get('total_hombres_migrantes', None) or None,
            total_mujeres_migrantes=request.form.get('total_mujeres_migrantes', None) or None,
            total_hombres_amazonicas=request.form.get('total_hombres_amazonicas', None) or None,
            total_mujeres_amazonicas=request.form.get('total_mujeres_amazonicas', None) or None,
            total_hombres_periurbanas=request.form.get('total_hombres_periurbanas', None) or None,
            total_mujeres_periurbanas=request.form.get('total_mujeres_periurbanas', None) or None,
            total_hombres_conflicto=request.form.get('total_hombres_conflicto', None) or None,
            total_mujeres_conflicto=request.form.get('total_mujeres_conflicto', None) or None,
            otra_poblacion_detalle=request.form.get('otra_poblacion_detalle', ''),
            total_hombres_otra=request.form.get('total_hombres_otra', None) or None,
            total_mujeres_otra=request.form.get('total_mujeres_otra', None) or None,
            tipo_naturaleza="|".join(request.form.getlist('tipo_naturaleza[]')),
            cambio_politica_detalle=request.form.get('cambio_politica_detalle', ''),
            cambio_marcos_detalle=request.form.get('cambio_marcos_detalle', ''),
            cambio_practicas_detalle=request.form.get('cambio_practicas_detalle', ''),
            cambio_sensibilidad_detalle=request.form.get('cambio_sensibilidad_detalle', ''),
            otro_naturaleza_detalle=request.form.get('otro_naturaleza_detalle', ''),
            otro_naturaleza_particular=request.form.get('otro_naturaleza_particular', ''),
            sector_publico_competente_1=request.form.get('sector_publico_competente_1', ''),
            dependencia_instancia_1=request.form.get('dependencia_instancia_1', ''),
            alcance_escala_1=request.form.get('alcance_escala_1', ''),
            sector_publico_competente_2=request.form.get('sector_publico_competente_2', ''),
            dependencia_instancia_2=request.form.get('dependencia_instancia_2', ''),
            alcance_escala_2=request.form.get('alcance_escala_2', ''),
            localidad_1=request.form.get('localidad_1', ''),
            localidad_2=request.form.get('localidad_2', ''),
            localidad_3=request.form.get('localidad_3', ''),
            descripcion_situacion=request.form.get('descripcion_situacion', ''),
            objetivo_especifico=request.form.get('objetivo_especifico', ''),
            campos="|".join(request.form.getlist('campos[]')),
            campo_otro_detalle=request.form.get('campo_otro_detalle', ''),
            componente_1=request.form.get('componente_1', ''),
            componente_2=request.form.get('componente_2', ''),
            componente_3=request.form.get('componente_3', ''),
            contenido_1=request.form.get('contenido_1', None) or None,
            contenido_2=request.form.get('contenido_2', None) or None,
            contenido_3=request.form.get('contenido_3', None) or None,
            contenido_4=request.form.get('contenido_4', None) or None,
            contenido_5=request.form.get('contenido_5', None) or None,
            contenido_6=request.form.get('contenido_6', None) or None,
            contenido_7=request.form.get('contenido_7', None) or None,
            contenido_otro=request.form.get('contenido_otro', ''),
            calificacion_otro_contenido=request.form.get('calificacion_otro_contenido', None) or None,
            fase_implementacion=int(fase_implementacion) if fase_implementacion.isdigit() else None,
            fase_normas_detalle=request.form.get('fase_normas_detalle', ''),
            fase_institucionalizacion_detalle=request.form.get('fase_institucionalizacion_detalle', ''),
            fase_otro_detalle=request.form.get('fase_otro_detalle', ''),
            actividad_1=request.form.get('actividad_1', ''),
            actividad_2=request.form.get('actividad_2', ''),
            actividad_3=request.form.get('actividad_3', ''),
            actividad_4=request.form.get('actividad_4', ''),
            actividad_5=request.form.get('actividad_5', ''),
            proyecto_1=request.form.get('proyecto_1', ''),
            fuente_financiamiento_1=request.form.get('fuente_financiamiento_1', ''),
            financiamiento_1=request.form.get('financiamiento_1', None) or None,
            periodo_financiamiento_1=request.form.get('periodo_financiamiento_1', ''),
            proyecto_2=request.form.get('proyecto_2', ''),
            fuente_financiamiento_2=request.form.get('fuente_financiamiento_2', ''),
            financiamiento_2=request.form.get('financiamiento_2', None) or None,
            periodo_financiamiento_2=request.form.get('periodo_financiamiento_2', ''),
            observaciones=request.form.get('observaciones', ''),
            oficina_regional=request.form.get('oficina_regional', ''),
            proyectos=request.form.get('proyectos', ''),
            tipo_participacion_fe=request.form.get('tipo_participacion_fe', ''),                
            responsable_registro=request.form.get('responsable_registro', '')
        )

        # Asignar registros seleccionados
       

        db.session.add(nueva_iniciativa)
        db.session.flush()  # Realizar un flush para obtener el ID de la nueva iniciativa

        # Asociar los registros seleccionados a la iniciativa usando la tabla intermedia
        if registros_seleccionados:
            dnis = registros_seleccionados.split(',')  # Los DNIs llegan como una lista separada por comas
            for dni in dnis:
                registro = Registro.query.filter_by(dni=dni).first()
                if registro:
                    # Usar la tabla intermedia para crear la relación
                    conn = iniciativa_registro.insert().values(
                        iniciativa_nombre=nueva_iniciativa.nombre_iniciativa,
                        registro_dni=registro.dni
                    )
                    db.session.execute(conn)

        # Guardar cambios en la base de datos
        db.session.commit()

        flash('Iniciativa registrada exitosamente.', 'success')
        return redirect(url_for('listar_iniciativas'))
    
    # Si es GET, pasar los registros disponibles al frontend
    registros_disponibles = Registro.query.filter(
        ~Registro.iniciativas.any()  # Registros que no están asociados a ninguna iniciativa
    ).all()

    return render_template('form_iniciativas.html', registros_disponibles=registros_disponibles)

@app.route('/get_seleccionados/<nombre_iniciativa>', methods=['GET'])
@login_required
def get_seleccionados(nombre_iniciativa):
    iniciativa = Iniciativa.query.filter_by(nombre_iniciativa=nombre_iniciativa).first()

    if not iniciativa:
        return jsonify([]), 404

    registros = [
        {
            "dni": registro.dni,
            "nombre": registro.nombre,
            "estado": registro.estado  # Incluir el estado
        }
        for registro in iniciativa.registros
    ]
    return jsonify(registros)


@app.route('/get_registros', methods=['GET'])
@login_required
def get_registros():
    # registros_disponibles = Registro.query.filter(Registro.estado == "ACT").all()
    registros_disponibles = Registro.query.filter(Registro.estado == "ACT").all()
    registros_json = [
        {
            "dni": registro.dni,
            "nombre": registro.nombre,
            "estado": registro.estado  # Incluir el estado
        }
        for registro in registros_disponibles
    ]
    return jsonify(registros_json)

# LISTAR INICIATIVAS
@app.route('/listado_iniciativas', methods=['GET'])
@login_required
@roles_required('admin', 'editor', 'viewer')
def listar_iniciativas():
    iniciativas = Iniciativa.query.all()  # Obtener todas las iniciativas de la base de datos
    return render_template('listar_iniciativas.html', iniciativas=iniciativas)

# EDITAR INICIATIVAS
@app.route('/editar_iniciativa/<nombre_iniciativa>', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'editor')
def editar_iniciativa(nombre_iniciativa):
    iniciativa = Iniciativa.query.filter_by(nombre_iniciativa=nombre_iniciativa).first()

    if not iniciativa:
        flash('La iniciativa no existe.', 'danger')
        return redirect(url_for('listar_iniciativas'))
    

    if request.method == 'POST':
        fase_implementacion = request.form.get('fase_implementacion')
        if fase_implementacion == "otro":
            iniciativa.fase_implementacion = None  # No almacenar "otro", solo el detalle
            iniciativa.fase_otro_detalle = request.form.get('fase_otro_detalle', '').strip()
        else:
            iniciativa.fase_implementacion = int(fase_implementacion) if fase_implementacion.isdigit() else None
            iniciativa.fase_otro_detalle = ''  # Resetear si no es "otro"
        iniciativa.derecho_generico = request.form.get('derecho_generico', '')
        iniciativa.otro_derecho_detalle = request.form.get('otro_derecho_detalle', '')
        iniciativa.colectivo_organizacion = request.form.get('colectivo_organizacion', '')
        iniciativa.poblacion = request.form.get('poblacion', '')
        iniciativa.total_hombres_ninos = request.form.get('total_hombres_ninos', None) or None
        iniciativa.total_mujeres_ninos = request.form.get('total_mujeres_ninos', None) or None
        iniciativa.total_hombres_adolescentes = request.form.get('total_hombres_adolescentes', None) or None
        iniciativa.total_mujeres_adolescentes = request.form.get('total_mujeres_adolescentes', None) or None
        iniciativa.total_hombres_jovenes = request.form.get('total_hombres_jovenes', None) or None
        iniciativa.total_mujeres_jovenes = request.form.get('total_mujeres_jovenes', None) or None
        iniciativa.total_hombres_mujeres = request.form.get('total_hombres_mujeres', None) or None
        iniciativa.total_mujeres_mujeres = request.form.get('total_mujeres_mujeres', None) or None
        iniciativa.total_hombres_discapacidad = request.form.get('total_hombres_discapacidad', None) or None
        iniciativa.total_mujeres_discapacidad = request.form.get('total_mujeres_discapacidad', None) or None
        iniciativa.total_hombres_migrantes = request.form.get('total_hombres_migrantes', None) or None
        iniciativa.total_mujeres_migrantes = request.form.get('total_mujeres_migrantes', None) or None
        iniciativa.total_hombres_amazonicas = request.form.get('total_hombres_amazonicas', None) or None
        iniciativa.total_mujeres_amazonicas = request.form.get('total_mujeres_amazonicas', None) or None
        iniciativa.total_hombres_periurbanas = request.form.get('total_hombres_periurbanas', None) or None
        iniciativa.total_mujeres_periurbanas = request.form.get('total_mujeres_periurbanas', None) or None
        iniciativa.total_hombres_conflicto = request.form.get('total_hombres_conflicto', None) or None
        iniciativa.total_mujeres_conflicto = request.form.get('total_mujeres_conflicto', None) or None
        iniciativa.otra_poblacion_detalle = request.form.get('otra_poblacion_detalle', '')
        iniciativa.total_hombres_otra = request.form.get('total_hombres_otra', None) or None
        iniciativa.total_mujeres_otra = request.form.get('total_mujeres_otra', None) or None
        iniciativa.tipo_naturaleza = "|".join(request.form.getlist('tipo_naturaleza[]'))
        iniciativa.cambio_politica_detalle = request.form.get('cambio_politica_detalle', '')
        iniciativa.cambio_marcos_detalle = request.form.get('cambio_marcos_detalle', '')
        iniciativa.cambio_practicas_detalle = request.form.get('cambio_practicas_detalle', '')
        iniciativa.cambio_sensibilidad_detalle = request.form.get('cambio_sensibilidad_detalle', '')
        iniciativa.otro_naturaleza_detalle = request.form.get('otro_naturaleza_detalle', '')
        iniciativa.otro_naturaleza_particular = request.form.get('otro_naturaleza_particular', '')
        iniciativa.sector_publico_competente_1 = request.form.get('sector_publico_competente_1', '')
        iniciativa.dependencia_instancia_1 = request.form.get('dependencia_instancia_1', '')
        iniciativa.alcance_escala_1 = request.form.get('alcance_escala_1', '')
        iniciativa.sector_publico_competente_2 = request.form.get('sector_publico_competente_2', '')
        iniciativa.dependencia_instancia_2 = request.form.get('dependencia_instancia_2', '')
        iniciativa.alcance_escala_2 = request.form.get('alcance_escala_2', '')
        iniciativa.localidad_1 = request.form.get('localidad_1', '')
        iniciativa.localidad_2 = request.form.get('localidad_2', '')
        iniciativa.localidad_3 = request.form.get('localidad_3', '')
        iniciativa.descripcion_situacion = request.form.get('descripcion_situacion', '')
        iniciativa.objetivo_especifico = request.form.get('objetivo_especifico', '')
        iniciativa.campos = "|".join(request.form.getlist('campos[]'))
        iniciativa.campo_otro_detalle = request.form.get('campo_otro_detalle', '')
        iniciativa.componente_1 = request.form.get('componente_1', '')
        iniciativa.componente_2 = request.form.get('componente_2', '')
        iniciativa.componente_3 = request.form.get('componente_3', '')
        iniciativa.contenido_1 = request.form.get('contenido_1', None) or None
        iniciativa.contenido_2 = request.form.get('contenido_2', None) or None
        iniciativa.contenido_3 = request.form.get('contenido_3', None) or None
        iniciativa.contenido_4 = request.form.get('contenido_4', None) or None
        iniciativa.contenido_5 = request.form.get('contenido_5', None) or None
        iniciativa.contenido_6 = request.form.get('contenido_6', None) or None
        iniciativa.contenido_7 = request.form.get('contenido_7', None) or None
        iniciativa.contenido_otro = request.form.get('contenido_otro', '')
        iniciativa.calificacion_otro_contenido = request.form.get('calificacion_otro_contenido', None) or None
        iniciativa.fase_normas_detalle = request.form.get('fase_normas_detalle', '')
        iniciativa.fase_institucionalizacion_detalle = request.form.get('fase_institucionalizacion_detalle', '')
        iniciativa.actividad_1 = request.form.get('actividad_1', '')
        iniciativa.actividad_2 = request.form.get('actividad_2', '')
        iniciativa.actividad_3 = request.form.get('actividad_3', '')
        iniciativa.actividad_4 = request.form.get('actividad_4', '')
        iniciativa.actividad_5 = request.form.get('actividad_5', '')
        iniciativa.proyecto_1 = request.form.get('proyecto_1', '')
        iniciativa.fuente_financiamiento_1 = request.form.get('fuente_financiamiento_1', '')
        iniciativa.financiamiento_1 = request.form.get('financiamiento_1', None) or None
        iniciativa.periodo_financiamiento_1 = request.form.get('periodo_financiamiento_1', '')
        iniciativa.proyecto_2 = request.form.get('proyecto_2', '')
        iniciativa.fuente_financiamiento_2 = request.form.get('fuente_financiamiento_2', '')
        iniciativa.financiamiento_2 = request.form.get('financiamiento_2', None) or None
        iniciativa.periodo_financiamiento_2 = request.form.get('periodo_financiamiento_2', '')
        iniciativa.observaciones = request.form.get('observaciones', '')
        iniciativa.responsable_registro = request.form.get('responsable_registro', '')
        iniciativa.oficina_regional=request.form.get('oficina_regional', '')
        iniciativa.proyectos=request.form.get('proyectos', '')
        iniciativa.tipo_participacion_fe=request.form.get('tipo_participacion_fe', '')
        
        # Actualizar participantes
        nuevos_dnis = request.form.get('registros', '').split(',')
        nuevos_dnis = [dni.strip() for dni in nuevos_dnis if dni]
        actuales_dnis = [registro.dni for registro in iniciativa.registros]
                
                
        # Agregar nuevos participantes
        for dni in nuevos_dnis:
            if dni not in actuales_dnis:
                registro = Registro.query.filter_by(dni=dni).first()
                if registro:
                    iniciativa.registros.append(registro)

        # Eliminar participantes no seleccionados
        for registro in iniciativa.registros[:]:
            if registro.dni not in nuevos_dnis:
                iniciativa.registros.remove(registro)

        db.session.commit()

        flash('La iniciativa ha sido actualizada con éxito.', 'success')
        return redirect(url_for('listar_iniciativas'))

    # Registros disponibles para ser seleccionados
    registros_disponibles = Registro.query.filter(Registro.estado == "ACT").all()

    # Registros ya asociados a la iniciativa
    registros_seleccionados = [
        {
            "dni": registro.dni,
            "nombre": registro.nombre,
            "estado": registro.estado  # Incluye el estado del participante
        }
        for registro in iniciativa.registros
    ]

    return render_template(
        'editar_iniciativa.html',
        iniciativa=iniciativa,
        registros_disponibles=registros_disponibles,
        registros_seleccionados=registros_seleccionados,
        iniciativa_nombre=nombre_iniciativa
    )

# ELIMINAR INICIATIVA
@app.route('/eliminar_iniciativa/<nombre_iniciativa>', methods=['POST'])
@login_required
@roles_required('admin')
def eliminar_iniciativa(nombre_iniciativa):
    # Obtener la iniciativa usando el nombre_iniciativa
    iniciativa = Iniciativa.query.filter_by(nombre_iniciativa=nombre_iniciativa).first()

    if not iniciativa:
        flash('La iniciativa no existe.', 'danger')
        return redirect(url_for('listar_iniciativas'))
    
    # Verificar si la iniciativa tiene capacidades relacionadas
    if iniciativa.capacidades:  # Asegúrate de que la relación esté configurada correctamente
        flash('No se puede eliminar la iniciativa porque tiene capacidades relacionadas.', 'danger')
        return redirect(url_for('listar_iniciativas'))

    try:
        # Eliminar la iniciativa
        db.session.delete(iniciativa)
        db.session.commit()

        flash('La iniciativa ha sido eliminada con éxito.', 'success')
    except Exception as e:
        db.session.rollback()  # Hacer rollback en caso de error
        flash(f'Error al eliminar la iniciativa: {str(e)}', 'danger')

    return redirect(url_for('listar_iniciativas'))

########################################################################################################################################
########################################################################################################################################
##########                        REGISTRO PROCESO DE INICIATIVAS                     ##################################################
########################################################################################################################################
########################################################################################################################################
class ProcesoIniciativa(db.Model):
    __tablename__ = 'proceso_iniciativa'
    id = db.Column(db.Integer, primary_key=True)
    nombre_iniciativa = db.Column(db.String(150), db.ForeignKey('iniciativa.nombre_iniciativa'), nullable=False)
    objetivo_especifico = db.Column(db.String(255), nullable=False)
    
    # Logros
    logros = db.Column(db.String(80), nullable=True)
    sustento_logros = db.Column(db.String(255), nullable=True)

    # Contenidos
    contenido_1 = db.Column(db.Integer, nullable=True)  # 0 - 4 calificaciones
    contenido_2 = db.Column(db.Integer, nullable=True)
    contenido_3 = db.Column(db.Integer, nullable=True)
    contenido_4 = db.Column(db.Integer, nullable=True)
    contenido_5 = db.Column(db.Integer, nullable=True)
    contenido_6 = db.Column(db.Integer, nullable=True)
    contenido_7 = db.Column(db.Integer, nullable=True)
    contenido_otro = db.Column(db.String(80), nullable=True)
    calificacion_otro_contenido = db.Column(db.Integer, nullable=True)

    # Fase de implementación
    fase_implementacion = db.Column(db.Integer)  # Representa el valor 0-9 según la selección
    fase_normas_detalle = db.Column(db.String(100), nullable=True)
    fase_institucionalizacion_detalle = db.Column(db.String(100), nullable=True)
    fase_otro_detalle = db.Column(db.String(100), nullable=True)

    # Nivel de avance de implementación
    nivel_avance_comentarios = db.Column(db.String(255), nullable=True)

    # Componentes
    componente_1 = db.Column(db.String(100), nullable=True)
    calificacion_componente_1 = db.Column(db.Integer, nullable=True)
    componente_2 = db.Column(db.String(100), nullable=True)
    calificacion_componente_2 = db.Column(db.Integer, nullable=True)
    componente_3 = db.Column(db.String(100), nullable=True)
    calificacion_componente_3 = db.Column(db.Integer, nullable=True)
    sustento_valoracion = db.Column(db.String(255), nullable=True)

    # Competencias y participación
    reforzar_competencias = db.Column(db.String(255), nullable=True)
    participacion_comportamiento = db.Column(db.Integer, nullable=True)
    comentario_valoracion = db.Column(db.String(255), nullable=True)

    # Factores clave
    factores_favorecido = db.Column(db.String(255), nullable=True)
    factores_obstaculizado = db.Column(db.String(255), nullable=True)

    # Actividades implementadas
    actividad_1 = db.Column(db.String(100), nullable=True)
    aporte_1 = db.Column(db.String(255), nullable=True)
    actividad_2 = db.Column(db.String(100), nullable=True)
    aporte_2 = db.Column(db.String(255), nullable=True)
    actividad_3 = db.Column(db.String(100), nullable=True)
    aporte_3 = db.Column(db.String(255), nullable=True)
    actividad_4 = db.Column(db.String(100), nullable=True)
    aporte_4 = db.Column(db.String(255), nullable=True)
    actividad_5 = db.Column(db.String(100), nullable=True)
    aporte_5 = db.Column(db.String(255), nullable=True)

    # Cambios en la estrategia
    cambios_estrategia = db.Column(db.String(400), nullable=True)
    comentario_relevante = db.Column(db.String(255), nullable=True)
    responsable_registro = db.Column(db.String(100), nullable=True)

    # Timestamp
    fecha_registro = db.Column(db.DateTime, default=obtener_hora_peru, nullable=True)
    
    # Relación con registros a través de Iniciativa
    @property
    def registros(self):
        return db.session.query(Registro).join(
            iniciativa_registro, Registro.dni == iniciativa_registro.c.registro_dni
        ).filter(
            iniciativa_registro.c.iniciativa_nombre == self.nombre_iniciativa
        ).all()

@app.route('/form_registro_proceso_iniciativa', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def form_registro_proceso_iniciativa():
    if request.method == 'POST':
        nombre_iniciativa = request.form['nombre_iniciativa'].strip().lower()

        # Obtener el número de registros existentes para esta iniciativa
        numero_registros = ProcesoIniciativa.query.filter_by(
            nombre_iniciativa=nombre_iniciativa
        ).count()
        
        # Procesar la fase de implementación seleccionada
        fase_implementacion = request.form.get('fase_implementacion', None)  # Valor de 0-9 o "otro"
        if fase_implementacion == "":
            fase_implementacion = None  # O usa un valor por defecto como 0

        if not fase_implementacion:
            flash('Debe seleccionar una fase de implementación.', 'danger')
            return redirect(url_for('form_registro_proceso_iniciativa'))
        
        # Crear un nuevo ProcesoIniciativa
        nuevo_proceso = ProcesoIniciativa(
            # Capturar los datos del formulario
            nombre_iniciativa = nombre_iniciativa,
            objetivo_especifico = request.form.get('objetivo_especifico', ''),
            logros = request.form.get('logros', ''),
            sustento_logros = request.form.get('sustento_logros', ''),
            contenido_1 = request.form.get('contenido_1', None) or None,
            contenido_2 = request.form.get('contenido_2', None) or None,
            contenido_3 = request.form.get('contenido_3', None) or None,
            contenido_4 = request.form.get('contenido_4', None) or None,
            contenido_5 = request.form.get('contenido_5', None) or None,
            contenido_6 = request.form.get('contenido_6', None) or None,
            contenido_7 = request.form.get('contenido_7', None) or None,
            contenido_otro = request.form.get('contenido_otro', ''),
            calificacion_otro_contenido = request.form.get('calificacion_otro_contenido', None) or None,
            fase_implementacion=int(fase_implementacion) if fase_implementacion.isdigit() else None,
            fase_normas_detalle = request.form.get('fase_normas_detalle', ''),
            fase_institucionalizacion_detalle = request.form.get('fase_institucionalizacion_detalle', ''),
            fase_otro_detalle = request.form.get('fase_otro_detalle', ''),
            nivel_avance_comentarios = request.form.get('nivel_avance_comentarios', ''),
            componente_1 = request.form.get('componente_1', ''),
            calificacion_componente_1 = request.form.get('calificacion_componente_1', None) or None,
            componente_2 = request.form.get('componente_2', ''),
            calificacion_componente_2 = request.form.get('calificacion_componente_2', None) or None,
            componente_3 = request.form.get('componente_3', ''),
            calificacion_componente_3 = request.form.get('calificacion_componente_3', None) or None,
            sustento_valoracion = request.form.get('sustento_valoracion', ''),
            reforzar_competencias = request.form.get('reforzar_competencias', ''),
            participacion_comportamiento = request.form.get('participacion_comportamiento', None) or None,
            comentario_valoracion = request.form.get('comentario_valoracion', ''),
            factores_favorecido = request.form.get('factores_favorecido', ''),
            factores_obstaculizado = request.form.get('factores_obstaculizado', ''),
            actividad_1 = request.form.get('actividad_1', ''),
            aporte_1 = request.form.get('aporte_1', ''),
            actividad_2 = request.form.get('actividad_2', ''),
            aporte_2 = request.form.get('aporte_2', ''),
            actividad_3 = request.form.get('actividad_3', ''),
            aporte_3 = request.form.get('aporte_3', ''),
            actividad_4 = request.form.get('actividad_4', ''),
            aporte_4 = request.form.get('aporte_4', ''),
            actividad_5 = request.form.get('actividad_5', ''),
            aporte_5 = request.form.get('aporte_5', ''),
            cambios_estrategia = request.form.get('cambios_estrategia', ''),
            comentario_relevante = request.form.get('comentario_relevante', ''),
            responsable_registro = request.form.get('responsable_registro', '')
        )

        # Guardar el nuevo proceso en la base de datos
        db.session.add(nuevo_proceso)
        db.session.flush()  # Hacer flush para asegurar el ID del proceso

        # Relacionar los registros seleccionados (participantes)
        iniciativa = Iniciativa.query.filter_by(nombre_iniciativa=nuevo_proceso.nombre_iniciativa).first()
        if iniciativa:
            participantes = iniciativa.registros  # Relación indirecta ya configurada
            print(f"Participantes asociados: {[p.nombre for p in participantes]}")  # Debug opcional

        db.session.commit()
        flash('Proceso de Iniciativa registrado exitosamente.', 'success')
        return redirect(url_for('listar_proceso_iniciativa'))

    # Obtener todas las iniciativas para el formulario
    iniciativas = Iniciativa.query.all()
    return render_template('form_registro_proceso_iniciativa.html', iniciativas=iniciativas)

# LISTAR PROCESO INICIATIVAS
@app.route('/listar_proceso_iniciativa', methods=['GET'])
@login_required
@roles_required('admin', 'editor', 'viewer')
def listar_proceso_iniciativa():
    # Consultar procesos ordenados correctamente
    procesos = ProcesoIniciativa.query.join(Iniciativa).order_by(
        Iniciativa.nombre_iniciativa.asc(),  # Ordenar alfabéticamente por nombre de iniciativa
        ProcesoIniciativa.fecha_registro.asc()  # Ordenar cronológicamente
    ).all()

    # Asignar número de registro dentro de cada iniciativa
    registros_por_iniciativa = {}
    
    for proceso in procesos:
        nombre_iniciativa = proceso.nombre_iniciativa
        
        # Si es la primera vez que encontramos esta iniciativa, inicializar el contador
        if nombre_iniciativa not in registros_por_iniciativa:
            registros_por_iniciativa[nombre_iniciativa] = 1
        else:
            registros_por_iniciativa[nombre_iniciativa] += 1

        # Asignar el número de registro
        proceso.numero_registro = registros_por_iniciativa[nombre_iniciativa]

    return render_template(
        'listar_proceso_iniciativa.html',
        procesos=procesos
    )


# EDITAR PROCESO DE INICIATIVA
@app.route('/editar_proceso_iniciativa/<int:id>', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'editor')
def editar_proceso_iniciativa(id):
    # Buscar el proceso de iniciativa por id usando filter_by y first()
    proceso_iniciativas = ProcesoIniciativa.query.filter_by(id=id).first()

    if not proceso_iniciativas:
        flash('El proceso de iniciativa no existe.', 'danger')
        return redirect(url_for('listar_proceso_iniciativa'))  # Redirigir si no se encuentra

    if request.method == 'POST':
        
        fase_implementacion = request.form.get('fase_implementacion')
        if fase_implementacion == "otro":
            proceso_iniciativas.fase_implementacion = None  # No almacenar "otro", solo el detalle
            proceso_iniciativas.fase_otro_detalle = request.form.get('fase_otro_detalle', '').strip()
        else:
            proceso_iniciativas.fase_implementacion = int(fase_implementacion) if fase_implementacion.isdigit() else None
            proceso_iniciativas.fase_otro_detalle = ''  # Resetear si no es "otro"
            
        # Asignar los valores recibidos desde el formulario
        proceso_iniciativas.nombre_iniciativa = request.form['nombre_iniciativa'].strip().lower()
        proceso_iniciativas.objetivo_especifico = request.form.get('objetivo_especifico', '')
        proceso_iniciativas.logros = request.form.get('logros', '')
        proceso_iniciativas.sustento_logros = request.form.get('sustento_logros', '')

        # Contenido de la iniciativa o propuesta
        proceso_iniciativas.contenido_1 = request.form.get('contenido_1', None) or None
        proceso_iniciativas.contenido_2 = request.form.get('contenido_2', None) or None
        proceso_iniciativas.contenido_3 = request.form.get('contenido_3', None) or None
        proceso_iniciativas.contenido_4 = request.form.get('contenido_4', None) or None
        proceso_iniciativas.contenido_5 = request.form.get('contenido_5', None) or None
        proceso_iniciativas.contenido_6 = request.form.get('contenido_6', None) or None
        proceso_iniciativas.contenido_7 = request.form.get('contenido_7', None) or None
        proceso_iniciativas.contenido_otro = request.form.get('contenido_otro', '')
        proceso_iniciativas.calificacion_otro_contenido = request.form.get('calificacion_otro_contenido', None) or None

        # Fase de Implementación
        proceso_iniciativas.fase_normas_detalle = request.form.get('fase_normas_detalle', '')
        proceso_iniciativas.fase_institucionalizacion_detalle = request.form.get('fase_institucionalizacion_detalle', '')

        # Nivel de avance y calificaciones
        proceso_iniciativas.nivel_avance_comentarios = request.form.get('nivel_avance_comentarios', '')
        proceso_iniciativas.componente_1 = request.form.get('componente_1', '') # Corregido
        proceso_iniciativas.calificacion_componente_1 = request.form.get('calificacion_componente_1', None) or None
        proceso_iniciativas.componente_2 = request.form.get('componente_2', '') # Corregido
        proceso_iniciativas.calificacion_componente_2 = request.form.get('calificacion_componente_2', None) or None
        proceso_iniciativas.componente_3 = request.form.get('componente_3', '') # Corregido
        proceso_iniciativas.calificacion_componente_3 = request.form.get('calificacion_componente_3', None) or None
        proceso_iniciativas.sustento_valoracion = request.form.get('sustento_valoracion', '')

        # Reforzamiento de competencias
        proceso_iniciativas.reforzar_competencias = request.form.get('reforzar_competencias', '')

        # Participación de la organización
        proceso_iniciativas.participacion_comportamiento = request.form.get('participacion_comportamiento', None) or None
        proceso_iniciativas.comentario_valoracion = request.form.get('comentario_valoracion', '')

        # Factores claves
        proceso_iniciativas.factores_favorecido = request.form.get('factores_favorecido', '')
        proceso_iniciativas.factores_obstaculizado = request.form.get('factores_obstaculizado', '')

        # Actividades
        proceso_iniciativas.actividad_1 = request.form.get('actividad_1', '')
        proceso_iniciativas.aporte_1 = request.form.get('aporte_1', '')
        proceso_iniciativas.actividad_2 = request.form.get('actividad_2', '')
        proceso_iniciativas.aporte_2 = request.form.get('aporte_2', '')
        proceso_iniciativas.actividad_3 = request.form.get('actividad_3', '')
        proceso_iniciativas.aporte_3 = request.form.get('aporte_3', '')
        proceso_iniciativas.actividad_4 = request.form.get('actividad_4', '')
        proceso_iniciativas.aporte_4 = request.form.get('aporte_4', '')
        proceso_iniciativas.actividad_5 = request.form.get('actividad_5', '')
        proceso_iniciativas.aporte_5 = request.form.get('aporte_5', '')

        # Cambios en la estrategia institucional
        proceso_iniciativas.cambios_estrategia = request.form.get('cambios_estrategia', '')
        proceso_iniciativas.comentario_relevante = request.form.get('comentario_relevante', '')
        proceso_iniciativas.responsable_registro = request.form.get('responsable_registro', '')

        # Validar y acceder a los participantes
        participantes = proceso_iniciativas.registros  # Relación indirecta ya configurada
        print(f"Participantes asociados al proceso: {[p.nombre for p in participantes]}")  # Debug opcional

        # Guardar cambios en la base de datos
        try:
            db.session.commit()
            flash('El proceso de iniciativa ha sido actualizado exitosamente.', 'success')
            return redirect(url_for('listar_proceso_iniciativa'))
        except:
            db.session.rollback()
            flash('Hubo un error al actualizar el proceso de iniciativa.', 'danger')

    # Renderizar el formulario con los datos existentes
    iniciativas = Iniciativa.query.all()  # Asumiendo que hay un modelo de Iniciativas
    participantes = proceso_iniciativas.registros  # Participantes relacionados
    return render_template('editar_proceso_iniciativa.html', proceso_iniciativas=proceso_iniciativas, iniciativas=iniciativas, participantes=participantes)

# ELIMINAR PROCESO INICIATIVAS
@app.route('/eliminar_proceso_iniciativa/<int:id>', methods=['POST'])
@login_required
@roles_required('admin')
def eliminar_proceso_iniciativa(id):
    # Buscar el proceso de iniciativa por su id
    proceso_iniciativa = ProcesoIniciativa.query.filter_by(id=id).first()

    if not proceso_iniciativa:
        flash('La iniciativa no existe.', 'danger')
        return redirect(url_for('listar_proceso_iniciativa'))
    
    try:
        # Eliminar el proceso de la base de datos
        db.session.delete(proceso_iniciativa)
        db.session.commit()
        flash('El proceso de iniciativa ha sido eliminado correctamente.', 'success')
    except:
        # En caso de error, hacer rollback
        db.session.rollback()
        flash('Hubo un error al intentar eliminar el proceso de iniciativa.', 'danger')

    # Redirigir a la lista de procesos de iniciativas
    return redirect(url_for('listar_proceso_iniciativa'))

########################################################################################################################################
########################################################################################################################################
############                      CAPACIDAD INCIDENCIA                   ###############################################################
########################################################################################################################################
########################################################################################################################################
class CapacidadIncidencia(db.Model):
    __tablename__ = 'capacidad_incidencia'
    id = db.Column(db.Integer, primary_key=True)
    registro_dni = db.Column(db.String(20), db.ForeignKey('registro.dni', ondelete='CASCADE'), nullable=False)
    nombre_iniciativa = db.Column(db.String(150), db.ForeignKey('iniciativa.nombre_iniciativa', ondelete='CASCADE'), nullable=False)
    capacidad_1 = db.Column(db.Integer, nullable=True)
    capacidad_2 = db.Column(db.Integer, nullable=True)
    capacidad_3 = db.Column(db.Integer, nullable=True)
    capacidad_4 = db.Column(db.Integer, nullable=True)
    capacidad_5 = db.Column(db.Integer, nullable=True)
    otra_capacidad = db.Column(db.String(100), nullable=True)
    calificacion_otra_capacidad = db.Column(db.Integer, nullable=True)
    fecha_registro = db.Column(db.DateTime, default=obtener_hora_peru, nullable=True)

    # Relación con Registro
    registro = db.relationship('Registro', backref='capacidades')

    # Relación con Iniciativa
    iniciativa = db.relationship('Iniciativa', backref='capacidades')
    
    avances = db.relationship('AvanceCapacidadIncidencia', backref='capacidad_incidencia', lazy=True, cascade="all, delete-orphan")
    
@app.route('/obtener_datos_iniciativa', methods=['GET'])
@login_required
def obtener_datos_iniciativa():
    nombre_iniciativa = request.args.get('nombre_iniciativa', '').strip()
    if not nombre_iniciativa:
        return jsonify({'error': 'Debe proporcionar el nombre de la iniciativa.'}), 400

    iniciativa = Iniciativa.query.filter_by(nombre_iniciativa=nombre_iniciativa).first()
    if not iniciativa:
        return jsonify({'error': 'Iniciativa no encontrada.'}), 404

    return jsonify({
        'poblacion': iniciativa.poblacion or iniciativa.otra_poblacion_detalle,
        'derecho_generico': iniciativa.derecho_generico or iniciativa.otro_derecho_detalle
    })


# BUSCAR PARTICIPANTE
@app.route('/buscar_participante', methods=['GET'])
@login_required
def buscar_participante():
    search = request.args.get('q', '').strip().lower()  # Captura el término de búsqueda
    if not search:
        return jsonify([])  # Retorna una lista vacía si no hay término de búsqueda

    # Buscar coincidencias por DNI o nombre, asegurarse de que tengan iniciativas relacionadas y estén activos
    registros = Registro.query.filter(
        ((Registro.dni.ilike(f'%{search}%')) | (Registro.nombre.ilike(f'%{search}%'))) &  # Coincidencia en búsqueda
        (Registro.iniciativas.any()) &  # Tengan al menos una iniciativa relacionada
        (Registro.estado == 'ACT')  # El estado del participante sea ACT
    ).all()

    # Construir el resultado con lógica robusta para campos opcionales
    resultado = []
    for registro in registros:
        iniciativa = registro.iniciativas[0] if registro.iniciativas else None  # Tomar la primera iniciativa relacionada, si existe
        resultado.append({
            "dni": registro.dni or "",
            "nombre": registro.nombre or "",
            "poblacion": iniciativa.poblacion or iniciativa.otra_poblacion_detalle if iniciativa else "No especificado",
            "derecho_generico": iniciativa.derecho_generico or iniciativa.otro_derecho_detalle if iniciativa else "No especificado",
            "iniciativa": iniciativa.nombre_iniciativa if iniciativa else "No especificado",
            "capacidad_id": registro.capacidades[0].id if registro.capacidades else None
        })

    return jsonify(resultado)

@app.route('/buscar_iniciativas_participante', methods=['GET'])
@login_required
def buscar_iniciativas_participante():
    dni = request.args.get('dni', '').strip()
    if not dni:
        return jsonify([])

    # Buscar las iniciativas asociadas al participante por su DNI
    participante = Registro.query.filter_by(dni=dni).first()
    if not participante:
        return jsonify([])

    iniciativas = [
        {"nombre_iniciativa": iniciativa.nombre_iniciativa}
        for iniciativa in participante.iniciativas
    ]
    return jsonify(iniciativas)


@app.route('/form_capacidades_incidencia', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def form_capacidades_incidencia():
    if request.method == 'POST':
        registro_dni = request.form['registro_dni']
        nombre_iniciativa = request.form['nombre_iniciativa']
        
        if not registro_dni:
            flash('El participante buscado no está en el listado de Registro inicial.', 'danger')
            return redirect(url_for('form_capacidades_incidencia'))
        
        if not Iniciativa.query.filter_by(nombre_iniciativa=nombre_iniciativa).first():
            flash('La iniciativa seleccionada no existe o no está asociada al participante.', 'danger')
            return redirect(url_for('form_capacidades_incidencia'))

        
        if not nombre_iniciativa:
            flash('El participante debe pertenecer a una iniciativa. Debe crear la iniciativa y asignar al usuario.', 'danger')
            return redirect(url_for('form_capacidades_incidencia'))
        
        # Verificar si ya existe una capacidad registrada para el participante en esa iniciativa
        capacidad_existente = CapacidadIncidencia.query.filter_by(
            registro_dni=registro_dni,
            nombre_iniciativa=nombre_iniciativa
        ).first()

        if capacidad_existente:
            flash('Ya existe un registro inicial de capacidades para este participante en esta iniciativa.', 'danger')
            return redirect(url_for('listar_capacidades_incidencia'))
        

        nueva_capacidad = CapacidadIncidencia(
            registro_dni=registro_dni,
            nombre_iniciativa=nombre_iniciativa,
            capacidad_1=request.form.get('capacidad_1', None) or None,
            capacidad_2=request.form.get('capacidad_2', None) or None,
            capacidad_3=request.form.get('capacidad_3', None) or None,
            capacidad_4=request.form.get('capacidad_4', None) or None,
            capacidad_5=request.form.get('capacidad_5', None) or None,
            otra_capacidad=request.form.get('otra_capacidad', ''),
            calificacion_otra_capacidad=request.form.get('calificacion_otra_capacidad', None) or None,
        )

        db.session.add(nueva_capacidad)
        db.session.commit()
        flash('Capacidades registradas exitosamente.', 'success')
        return redirect(url_for('listar_capacidades_incidencia'))

    # Si es GET
    return render_template('capacidades_incidencia/form_capacidades_incidencia.html')

@app.route('/listar_capacidades_incidencia', methods=['GET'])
@login_required
@roles_required('admin', 'editor', 'viewer')
def listar_capacidades_incidencia():
    capacidades = CapacidadIncidencia.query.order_by(CapacidadIncidencia.fecha_registro.desc()).all()
    return render_template('capacidades_incidencia/listar_capacidades_incidencia.html', capacidades=capacidades)

@app.route('/editar_capacidades_incidencia/<int:id>', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'editor')
def editar_capacidades_incidencia(id):
    # Buscar la capacidad en la base de datos por ID
    capacidad = CapacidadIncidencia.query.filter_by(id=id).first()
    
    if not capacidad:
        flash('El registro de capacidad de incidencia no existe.', 'danger')
        return redirect(url_for('listar_capacidades_incidencia'))  # Redirigir si no se encuentra

    if request.method == 'POST':
        try:
            # Actualizar los valores de las capacidades
            capacidad.capacidad_1 = request.form.get('capacidad_1', None) or None
            capacidad.capacidad_2 = request.form.get('capacidad_2', None) or None
            capacidad.capacidad_3 = request.form.get('capacidad_3', None) or None
            capacidad.capacidad_4 = request.form.get('capacidad_4', None) or None
            capacidad.capacidad_5 = request.form.get('capacidad_5', None) or None
            capacidad.otra_capacidad = request.form.get('otra_capacidad', '').strip()
            capacidad.calificacion_otra_capacidad = request.form.get('calificacion_otra_capacidad', None) or None

            # Guardar los cambios en la base de datos
            db.session.commit()
            flash('Capacidades actualizadas exitosamente.', 'success')
            return redirect(url_for('listar_capacidades_incidencia'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar las capacidades: {str(e)}', 'danger')
            return redirect(url_for('listar_capacidades_incidencia'))

    # Si es GET, renderizar la página con los datos actuales
    return render_template('capacidades_incidencia/editar_capacidades_incidencia.html', capacidad=capacidad)

# ELIMINAR PROCESO INICIATIVAS
@app.route('/eliminar_capacidades_incidencia/<int:id>', methods=['POST'])
@login_required
@roles_required('admin')
def eliminar_capacidades_incidencia(id):
    # Buscar el proceso de iniciativa por su id
    capacidad = CapacidadIncidencia.query.filter_by(id=id).first()

    if not capacidad:
        flash('La capacidad no existe.', 'danger')
        return redirect(url_for('listar_capacidades_incidencia'))
    
    try:
        # Eliminar el proceso de la base de datos
        db.session.delete(capacidad)
        db.session.commit()
        flash('La Capacidad ha sido eliminado correctamente.', 'success')
    except:
        # En caso de error, hacer rollback
        db.session.rollback()
        flash('Hubo un error al intentar eliminar la capacidad.', 'danger')

    # Redirigir a la lista de procesos de iniciativas
    return redirect(url_for('listar_capacidades_incidencia'))

#######################################################################################################################################
#######################################################################################################################################
############################################ AVANCES CAPACIDAD INCIDENCIA #############################################################
class AvanceCapacidadIncidencia(db.Model):
    __tablename__ = 'avance_capacidad_incidencia'
    id = db.Column(db.Integer, primary_key=True)
    capacidad_id = db.Column(db.Integer, db.ForeignKey('capacidad_incidencia.id', ondelete='CASCADE'), nullable=False)  # Relación con CapacidadIncidencia
    capacidad_1 = db.Column(db.Integer, nullable=True)
    capacidad_2 = db.Column(db.Integer, nullable=True)
    capacidad_3 = db.Column(db.Integer, nullable=True)
    capacidad_4 = db.Column(db.Integer, nullable=True)
    capacidad_5 = db.Column(db.Integer, nullable=True)
    otra_capacidad = db.Column(db.String(100), nullable=True)
    calificacion_otra_capacidad = db.Column(db.Integer, nullable=True)
    fecha_registro = db.Column(db.DateTime, default=obtener_hora_peru, nullable=True)

    # Relación con CapacidadIncidencia
    # capacidad_incidencia = db.relationship('CapacidadIncidencia', backref=db.backref('avances', lazy=True))

@app.route('/get_iniciativas_por_participante', methods=['GET'])
@login_required
def get_iniciativas_por_participante():
    dni = request.args.get('dni')
    if not dni:
        return jsonify([])

    # Obtener todas las iniciativas asociadas al participante
    iniciativas = Iniciativa.query.join(iniciativa_registro).filter_by(registro_dni=dni).all()

    return jsonify([{'nombre_iniciativa': iniciativa.nombre_iniciativa} for iniciativa in iniciativas])


@app.route('/get_numero_avances_por_iniciativa', methods=['GET'])
@login_required
def get_numero_avances_por_iniciativa():
    dni = request.args.get('dni')
    nombre_iniciativa = request.args.get('iniciativa')

    if not dni or not nombre_iniciativa:
        return jsonify({'error': 'DNI o iniciativa no especificados.'})

    # Buscar la capacidad específica para el participante y la iniciativa
    capacidad = CapacidadIncidencia.query.filter_by(registro_dni=dni, nombre_iniciativa=nombre_iniciativa).first()
    if not capacidad:
        return jsonify({'error': 'No existe capacidad para esta combinación de participante e iniciativa.'})

    # Contar los avances asociados a esta capacidad
    numero_avances = AvanceCapacidadIncidencia.query.filter_by(capacidad_id=capacidad.id).count()

    # El próximo registro será el actual número de avances + 1
    proximo_registro = numero_avances + 1
    return jsonify({'proximo_registro': proximo_registro})







@app.route('/buscar_iniciativas_participante_avances', methods=['GET'])
@login_required
def buscar_iniciativas_participante_avances():
    dni = request.args.get('dni', '').strip()
    if not dni:
        return jsonify([])

    # Buscar las iniciativas asociadas al participante por su DNI
    participante = Registro.query.filter_by(dni=dni).first()
    if not participante:
        return jsonify([])

    iniciativas = [
        {"nombre_iniciativa": iniciativa.nombre_iniciativa}
        for iniciativa in participante.iniciativas
    ]
    return jsonify(iniciativas)


@app.route('/form_avances_capacidades_incidencia', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def form_avances_capacidades_incidencia():
    if request.method == 'POST':
        # Obtener datos del formulario
        capacidad_id = request.form.get('capacidad_id')  # ID de la capacidad seleccionada
        nombre_iniciativa = request.form.get('nombre_iniciativa')  # Nombre de la iniciativa
        registro_dni = request.form.get('registro_dni')  # DNI del participante seleccionado
        print(f"Registro DNI: {registro_dni}, Nombre Iniciativa: {nombre_iniciativa}")  # Verifica estos valores en el terminal/log
        # Verificar que los datos esenciales existan
        if not registro_dni or not nombre_iniciativa:
            flash('El participante o la iniciativa no son válidos.', 'danger')
            return redirect(url_for('form_avances_capacidades_incidencia'))
        
        # Buscar la capacidad en la base de datos usando el DNI y la iniciativa
        capacidad = CapacidadIncidencia.query.filter_by(
            registro_dni=registro_dni,
            nombre_iniciativa=nombre_iniciativa
        ).first()
        
        if not capacidad:
            flash('La iniciativa seleccionada no está asociada a este participante.', 'danger')
            return redirect(url_for('form_avances_capacidades_incidencia'))
                
        # Calificaciones y datos específicos del avance
        capacidad_1 = request.form.get('capacidad_1', None) or None
        capacidad_2 = request.form.get('capacidad_2', None) or None
        capacidad_3 = request.form.get('capacidad_3', None) or None
        capacidad_4 = request.form.get('capacidad_4', None) or None
        capacidad_5 = request.form.get('capacidad_5', None) or None
        otra_capacidad = request.form.get('otra_capacidad', '').strip()
        calificacion_otra_capacidad = request.form.get('calificacion_otra_capacidad', None) or None

        # Crear un nuevo avance para la capacidad seleccionada
        nuevo_avance = AvanceCapacidadIncidencia(
            capacidad_id=capacidad.id,
            # registro_dni=registro_dni,  # Relación del DNI
            # nombre_iniciativa=nombre_iniciativa,  # Relación de la iniciativa
            capacidad_1=capacidad_1,
            capacidad_2=capacidad_2,
            capacidad_3=capacidad_3,
            capacidad_4=capacidad_4,
            capacidad_5=capacidad_5,
            otra_capacidad=otra_capacidad,
            calificacion_otra_capacidad=calificacion_otra_capacidad,
        )

        try:
            # Guardar el avance en la base de datos
            db.session.add(nuevo_avance)
            db.session.commit()
            flash('El avance de capacidades se registró exitosamente.', 'success')
            return redirect(url_for('listar_avances_capacidades_incidencia')) #listar_avances_capacidades_incidencia
        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar el avance: {str(e)}', 'danger')
            return redirect(url_for('listar_avances_capacidades_incidencia'))

    # Si es GET, renderizar el formulario vacío
    return render_template('capacidades_incidencia/form_avances_capacidades_incidencia.html')

@app.route('/get_capacidad_avances/<participant_dni>', methods=['GET'])
@login_required
def get_capacidad_avances(participant_dni):
    # Buscar la capacidad asociada al participante
    capacidad = CapacidadIncidencia.query.filter_by(registro_dni=participant_dni).first()
    if not capacidad:
        return jsonify({"error": "No se encontró una capacidad para este participante."})

    # Contar los avances asociados a esta capacidad
    numero_registros = len(capacidad.avances)

    return jsonify({
        "capacidad_id": capacidad.id,
        "numero_registros": numero_registros
    })

@app.route('/listar_avances_capacidades_incidencia', methods=['GET'])
@login_required
@roles_required('admin', 'editor', 'viewer')
def listar_avances_capacidades_incidencia():
    # Obtener todos los avances ordenados por capacidad y fecha de registro
    avances = db.session.query(AvanceCapacidadIncidencia).join(CapacidadIncidencia).order_by(
        CapacidadIncidencia.registro_dni,  # Ordenar por DNI del participante
        AvanceCapacidadIncidencia.capacidad_id,  # Asegurar orden dentro de la capacidad
        AvanceCapacidadIncidencia.fecha_registro  # Ordenar por fecha dentro de la capacidad
    ).all()

    # Añadir el número de registro (índice) para cada avance en su capacidad
    avances_con_numero = []
    capacidad_actual = None
    numero_registro = 0

    for avance in avances:
        if capacidad_actual != avance.capacidad_id:
            capacidad_actual = avance.capacidad_id
            numero_registro = 1  # Reiniciar el conteo para cada nueva capacidad
        else:
            numero_registro += 1

        # Añadir el número de registro como un atributo dinámico
        avance.numero_registro = numero_registro
        avances_con_numero.append(avance)

    # Pasar los avances con el número de registro al template
    return render_template(
        'capacidades_incidencia/listar_avances_capacidades_incidencia.html',
        avances=avances_con_numero
    )


@app.route('/editar_avances_capacidades_incidencia/<int:avance_id>', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'editor')
def editar_avances_capacidades_incidencia(avance_id):
    # Buscar el avance por ID
    avance = AvanceCapacidadIncidencia.query.filter_by(id=avance_id).first()

    # Validar si el avance existe
    if not avance:
        flash('El avance no existe.', 'danger')
        return redirect(url_for('listar_avances_capacidades_incidencia'))

    if request.method == 'POST':
        # Actualizar los valores de las capacidades desde el formulario
        avance.capacidad_1 = request.form.get('capacidad_1', None) or None
        avance.capacidad_2 = request.form.get('capacidad_2', None) or None
        avance.capacidad_3 = request.form.get('capacidad_3', None) or None
        avance.capacidad_4 = request.form.get('capacidad_4', None) or None
        avance.capacidad_5 = request.form.get('capacidad_5', None) or None
        avance.otra_capacidad = request.form.get('otra_capacidad', '').strip()
        avance.calificacion_otra_capacidad = request.form.get('calificacion_otra_capacidad', None) or None

        try:
            # Guardar los cambios en la base de datos
            db.session.commit()
            flash('El avance se actualizó exitosamente.', 'success')
            return redirect(url_for('listar_avances_capacidades_incidencia'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el avance: {str(e)}', 'danger')
            return redirect(url_for('editar_avances_capacidades_incidencia', avance_id=avance_id))

    # Si es GET, renderizar el formulario con los valores actuales del avance
    return render_template(
        'capacidades_incidencia/editar_avances_capacidades_incidencia.html',
        avance=avance,
        capacidad=avance.capacidad_incidencia  # Acceso a la capacidad relacionada
    )

@app.route('/eliminar_avances_capacidades_incidencia/<int:avance_id>', methods=['POST'])
@login_required
@roles_required('admin')
def eliminar_avances_capacidades_incidencia(avance_id):
    # Buscar el avance por ID
    avance = AvanceCapacidadIncidencia.query.filter_by(id=avance_id).first()

    # Validar si el avance existe
    if not avance:
        flash('El avance no existe.', 'danger')
        return redirect(url_for('listar_avances_capacidades_incidencia'))

    try:
        # Eliminar el avance de la base de datos
        db.session.delete(avance)
        db.session.commit()
        flash('El avance se eliminó exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el avance: {str(e)}', 'danger')

    # Redirigir al listado de avances
    return redirect(url_for('listar_avances_capacidades_incidencia'))

########################################################################################################################################
########################################################################################################################################
##########                        CASOS EMBLEMATICOS                     ###############################################################
########################################################################################################################################
########################################################################################################################################
class CasoEmblematico(db.Model):
    nombre_caso = db.Column(db.String(200), primary_key=True)
    numero_expediente = db.Column(db.String(100), nullable=False)
    sala = db.Column(db.String(100), nullable=True)
    antecedentes = db.Column(db.String(300), nullable=True)
    descripcion_caso = db.Column(db.String(300), nullable=True)
    numero_afectados = db.Column(db.Integer, nullable=True)
    objetivo_defensa = db.Column(db.String(300), nullable=True)
    situacion_caso = db.Column(db.String(300), nullable=True)
    otro_dato = db.Column(db.String(300), nullable=True)
    fecha_registro = db.Column(db.DateTime, default=obtener_hora_peru, nullable=True)
    # Relación con AvanceCasoEmblematico
    avances = db.relationship('AvanceCasoEmblematico', backref='caso', lazy=True, cascade="all, delete-orphan")


@app.route('/form_registro_casos_emblematicos', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def form_registro_casos_emblematicos():
    if request.method == 'POST':
        # Validar que el nombre genérico del caso no exista
        nombre_caso = request.form['nombre_caso'].strip().lower(),

        # Verificar si ya existe un caso con el mismo nombre
        # filter(func.lower(CasoEmblematico.nombre_caso) == nombre_caso).first():
        if CasoEmblematico.query.filter(func.lower(CasoEmblematico.nombre_caso) == nombre_caso).first():
            flash('Este Caso Emblematico ya ha sido registrado.', 'danger')
            return redirect(url_for('listar_casos_emblematicos'))

        # Capturar los demás datos del formulario siguiendo el formato solicitado
        nuevo_caso = CasoEmblematico(
            nombre_caso=nombre_caso,
            numero_expediente=request.form.get('numero_expediente', ''),
            sala=request.form.get('sala', ''),
            antecedentes=request.form.get('antecedentes', ''),
            descripcion_caso=request.form.get('descripcion_caso', ''),
            numero_afectados=request.form.get('numero_afectados', None) or None,  # Valor predeterminado None si no es proporcionado
            objetivo_defensa=request.form.get('objetivo_defensa', ''),
            situacion_caso=request.form.get('situacion_caso', ''),
            otro_dato=request.form.get('otro_dato', '')
        )

        # Guardar en la base de datos
        db.session.add(nuevo_caso)
        db.session.commit()

        flash('Caso Emblemático registrado exitosamente.', 'success')
        return redirect(url_for('listar_casos_emblematicos'))

    return render_template('form_registro_casos_emblematicos.html')

# LISTAR CASOS EMBLEMÁTICOS
@app.route('/listar_casos_emblematicos')
@login_required
@roles_required('admin', 'editor', 'viewer')
def listar_casos_emblematicos():
    casos = CasoEmblematico.query.order_by(CasoEmblematico.fecha_registro.desc()).all()
    return render_template('listar_casos_emblematicos.html', casos=casos)

# EDITAR CASO EMBLEMATICO
@app.route('/editar_caso_emblematico/<nombre_caso>', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'editor')
def editar_caso_emblematico(nombre_caso):
    caso = CasoEmblematico.query.filter_by(nombre_caso=nombre_caso).first()

    if not caso:
        flash('El caso emblematico no existe.', 'danger')
        return redirect(url_for('listar_casos_emblematicos'))
    
    if request.method == 'POST':
        # Actualizar solo los campos que no son llave primaria, verificando si están vacíos o nulos
        caso.numero_expediente = request.form.get('numero_expediente', '') 
        caso.sala = request.form.get('sala', '')
        caso.antecedentes = request.form.get('antecedentes', '')  # Si no se proporciona, por defecto será un string vacío
        caso.descripcion_caso = request.form.get('descripcion_caso', '')  # Si no se proporciona, por defecto será un string vacío
        caso.numero_afectados = request.form.get('numero_afectados', None) or None  # Si está vacío, será None
        caso.objetivo_defensa = request.form.get('objetivo_defensa', '')  # Si no se proporciona, por defecto será un string vacío
        caso.situacion_caso = request.form.get('situacion_caso', '')  # Si no se proporciona, por defecto será un string vacío
        caso.otro_dato = request.form.get('otro_dato', '')  # Si no se proporciona, por defecto será un string vacío
        
        # Guardar los cambios en la base de datos
        try:
            db.session.commit()
            flash('El caso ha sido actualizado con éxito.', 'success')
            return redirect(url_for('listar_casos_emblematicos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el caso: {str(e)}', 'danger')
    
    # Renderizar la plantilla con los datos del caso cargados
    return render_template('editar_caso_emblematico.html', caso=caso)

# ELIMINAR CASO EMBLEMATICO
@app.route('/eliminar_caso_emblematico/<nombre_caso>', methods=['POST'])
@login_required
@roles_required('admin')
def eliminar_caso_emblematico(nombre_caso):
    # Buscar el caso emblemático por nombre_caso
    caso = CasoEmblematico.query.filter_by(nombre_caso=nombre_caso).first()

    if not caso:
        flash('El caso emblemático no existe.', 'danger')
        return redirect(url_for('listar_casos_emblematicos'))

    try:
        # Eliminar el caso de la base de datos
        db.session.delete(caso)
        db.session.commit()

        flash('El caso emblemático ha sido eliminado con éxito.', 'success')
    except Exception as e:
        db.session.rollback()  # Revertir la operación en caso de error
        flash(f'Error al eliminar el caso: {str(e)}', 'danger')

    return redirect(url_for('listar_casos_emblematicos'))


########################################################################################################################################
########################################################################################################################################
##########                        AVANCE DE LOS CASOS EMBLEMATICOS                     #################################################
########################################################################################################################################
########################################################################################################################################
# Modelo para Avances de Caso Emblemático
class AvanceCasoEmblematico(db.Model):
    __tablename__ = 'avance_caso_emblematico'
    id = db.Column(db.Integer, primary_key=True)
    nombre_caso = db.Column(db.String(200), db.ForeignKey('caso_emblematico.nombre_caso'), nullable=False)
    ocurrencias_periodo = db.Column(db.String(350), nullable=True)
    actividades_realizadas = db.Column(db.String(350), nullable=True)
    presencia_participacion = db.Column(db.String(350), nullable=True)
    estado_actual = db.Column(db.String(350), nullable=True)
    recomendaciones = db.Column(db.String(350), nullable=True)
    otro_asunto = db.Column(db.String(350), nullable=True)
    responsable_registro = db.Column(db.String(100), nullable=True)
    fecha_registro = db.Column(db.DateTime, default=obtener_hora_peru, nullable=True)

@app.route('/form_avances_caso_emblematico', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def form_avances_caso_emblematico():
    if request.method == 'POST':
        # Crear un nuevo registro de avance del caso emblemático con todos los datos
        nuevo_avance_caso_emblematico = AvanceCasoEmblematico(
            nombre_caso=request.form['nombre_caso'].strip().lower(),
            ocurrencias_periodo=request.form.get('ocurrencias_periodo', ''),
            actividades_realizadas=request.form.get('actividades_realizadas', ''),
            presencia_participacion=request.form.get('presencia_participacion', ''),
            estado_actual=request.form.get('estado_actual', ''),
            recomendaciones=request.form.get('recomendaciones', ''),
            otro_asunto=request.form.get('otro_asunto', ''),
            responsable_registro=request.form.get('responsable_registro', '')
        )

        # Guardar en la base de datos
        db.session.add(nuevo_avance_caso_emblematico)
        db.session.commit()

        flash('Avance del Caso Emblemático registrado exitosamente.', 'success')
        return redirect(url_for('listar_avances_caso_emblematico'))

    # Obtener la lista de todos los casos emblemáticos
    casos = CasoEmblematico.query.all()
    return render_template('form_avances_caso_emblematico.html', casos=casos)

# LISTAR AVANCES CASO EMBLEMATICO
@app.route('/listar_avances_caso_emblematico')
@login_required
@roles_required('admin', 'editor', 'viewer')
def listar_avances_caso_emblematico():
    # Obtener los registros en orden descendente por la fecha de registro
    avances_caso_emblematico = AvanceCasoEmblematico.query.order_by(AvanceCasoEmblematico.fecha_registro.desc()).all()
    return render_template('listar_avances_caso_emblematico.html', avances_caso_emblematico=avances_caso_emblematico)

# EDITAR AVANCES CASO EMBLEMATICO
@app.route('/editar_avances_caso_emblematico/<int:id>', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'editor')
def editar_avances_caso_emblematico(id):
    # Buscar el proceso de iniciativa por id usando filter_by y first()
    avance_caso_emblematico = AvanceCasoEmblematico.query.filter_by(id=id).first()

    if not avance_caso_emblematico:
        flash('El avance del caso emblematico no existe.', 'danger')
        return redirect(url_for('listar_avances_caso_emblematico'))  # Redirigir si no se encuentra

    if request.method == 'POST':
        # Asignar los valores recibidos desde el formulario
        avance_caso_emblematico.nombre_caso = request.form['nombre_caso'].strip().lower()
        avance_caso_emblematico.ocurrencias_periodo = request.form.get('ocurrencias_periodo', '')
        avance_caso_emblematico.actividades_realizadas = request.form.get('actividades_realizadas', '')
        avance_caso_emblematico.presencia_participacion = request.form.get('presencia_participacion', '')
        avance_caso_emblematico.estado_actual = request.form.get('estado_actual', '')
        avance_caso_emblematico.recomendaciones = request.form.get('recomendaciones', '')
        avance_caso_emblematico.otro_asunto = request.form.get('otro_asunto', '')
        avance_caso_emblematico.responsable_registro = request.form.get('responsable_registro', '')

        # Guardar cambios en la base de datos
        try:
            db.session.commit()
            flash('El avance de caso emblematico ha sido actualizado exitosamente.', 'success')
            return redirect(url_for('listar_avances_caso_emblematico'))
        except:
            db.session.rollback()
            flash('Hubo un error al actualizar el avance de caso emblematico.', 'danger')
            return redirect(url_for('listar_avances_caso_emblematico'))  # Redirigir si no hay error

    # Renderizar el formulario con los datos existentes
    caso_emblematico = CasoEmblematico.query.all()  # Asumiendo que hay un modelo de Iniciativas
    return render_template('editar_avances_caso_emblematico.html', avance_caso_emblematico=avance_caso_emblematico, caso_emblematico=caso_emblematico)

# ELIMINAR AVANCES CASO EMBLEMATICO
@app.route('/eliminar_avance_caso_emblematico/<int:id>', methods=['POST'])
@login_required
@roles_required('admin')
def eliminar_avance_caso_emblematico(id):
    # Buscar el proceso de iniciativa por su id
    avances_caso_emblematico = AvanceCasoEmblematico.query.filter_by(id=id).first()

    if not avances_caso_emblematico:
        flash('El avance de caso emblematico no existe.', 'danger')
        return redirect(url_for('listar_avances_caso_emblematico'))
    
    try:
        # Eliminar el proceso de la base de datos
        db.session.delete(avances_caso_emblematico)
        db.session.commit()
        flash('El avance de caso emblematico ha sido eliminado correctamente.', 'success')
    except:
        # En caso de error, hacer rollback
        db.session.rollback()
        flash('Hubo un error al intentar eliminar el avance de caso emblematico.', 'danger')

    # Redirigir a la lista de procesos de iniciativas
    return redirect(url_for('listar_avances_caso_emblematico'))


########################################################################################################################################
########################################################################################################################################
##########                          POLITICA NACIONAL Y MEMORIA                          ###############################################
########################################################################################################################################
########################################################################################################################################

class PoliticaNacionalMemoria(db.Model):
    __tablename__ = 'politica_nacional_memoria'
    nombre_politica_memoria = db.Column(db.String(200), primary_key=True)  # Nombre como PK
    localizacion = db.Column(db.String(200), nullable=True)
    descripcion_propuesta = db.Column(db.String(300), nullable=True)
    institucion_1 = db.Column(db.String(200), nullable=True)
    asunto_1 = db.Column(db.String(255), nullable=True)
    institucion_2 = db.Column(db.String(200), nullable=True)
    asunto_2 = db.Column(db.String(255), nullable=True)
    institucion_3 = db.Column(db.String(200), nullable=True)
    asunto_3 = db.Column(db.String(255), nullable=True)
    organizaciones_aliadas = db.Column(db.String(300), nullable=True)
    otro_dato = db.Column(db.String(255), nullable=True)
    fecha_registro = db.Column(db.DateTime, default=obtener_hora_peru, nullable=True)
    # Relación con AvancePoliticaMemoria
    avances = db.relationship('AvancePoliticaMemoria', backref='politica', lazy=True, cascade="all, delete-orphan")

@app.route('/form_registro_politica_nacional_memoria', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def form_registro_politica_nacional_memoria():
    if request.method == 'POST':
        # Validar que el nombre de la política o sitio de memoria no exista
        nombre_politica_memoria = request.form['nombre_politica_memoria'].strip().lower()

        # Verificar si ya existe una política o sitio de memoria con el mismo nombre
        if PoliticaNacionalMemoria.query.filter(func.lower(PoliticaNacionalMemoria.nombre_politica_memoria) == nombre_politica_memoria).first():
            flash('Esta Política Nacional y/o Sitio de Memoria ya ha sido registrado.', 'danger')
            return redirect(url_for('form_registro_politica_nacional_memoria'))

        # Capturar los demás datos del formulario
        nueva_politica_nacional_memoria = PoliticaNacionalMemoria(
            nombre_politica_memoria=nombre_politica_memoria,
            localizacion=request.form.get('localizacion', ''),
            descripcion_propuesta=request.form.get('descripcion_propuesta', ''),
            institucion_1=request.form.get('institucion_1', ''),
            asunto_1=request.form.get('asunto_1', ''),
            institucion_2=request.form.get('institucion_2', ''),
            asunto_2=request.form.get('asunto_2', ''),
            institucion_3=request.form.get('institucion_3', ''),
            asunto_3=request.form.get('asunto_3', ''),
            organizaciones_aliadas=request.form.get('organizaciones_aliadas', ''),
            otro_dato=request.form.get('otro_dato', '')
        )

        # Guardar en la base de datos
        db.session.add(nueva_politica_nacional_memoria)
        db.session.commit()

        flash('Política Nacional y/o Sitio de Memoria registrado exitosamente.', 'success')
        return redirect(url_for('listar_politica_nacional_memoria'))

    return render_template('form_registro_politica_nacional_memoria.html')

# LISTAR Politica nacional Memoria
@app.route('/listar_politica_nacional_memoria')
@login_required
@roles_required('admin', 'editor', 'viewer')
def listar_politica_nacional_memoria():
    politica_memoria = PoliticaNacionalMemoria.query.order_by(PoliticaNacionalMemoria.fecha_registro.desc()).all()
    return render_template('listar_politica_nacional_memoria.html', politica_memoria=politica_memoria)

# EDITAR Politica nacional Memoria
@app.route('/editar_politica_nacional_memoria/<nombre_politica_memoria>', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'editor')
def editar_politica_nacional_memoria(nombre_politica_memoria):
    politica_memoria = PoliticaNacionalMemoria.query.filter_by(nombre_politica_memoria=nombre_politica_memoria).first()

    if not politica_memoria:
        flash('La politica nacional y memoria no existe.', 'danger')
        return redirect(url_for('listar_politica_nacional_memoria'))
    
    if request.method == 'POST':
        # Actualizar solo los campos que no son llave primaria, verificando si están vacíos o nulos
        politica_memoria.localizacion = request.form.get('localizacion', '') 
        politica_memoria.descripcion_propuesta = request.form.get('descripcion_propuesta', '')
        politica_memoria.institucion_1 = request.form.get('institucion_1', '') 
        politica_memoria.asunto_1 = request.form.get('asunto_1', '') 
        politica_memoria.institucion_2 = request.form.get('institucion_2', '') 
        politica_memoria.asunto_2 = request.form.get('asunto_2', '') 
        politica_memoria.institucion_3 = request.form.get('institucion_3', '') 
        politica_memoria.asunto_3 = request.form.get('asunto_3', '') 
        politica_memoria.organizaciones_aliadas = request.form.get('organizaciones_aliadas', '')  # Si no se proporciona, por defecto será un string vacío
        politica_memoria.otro_dato = request.form.get('otro_dato', '')
        
        # Guardar los cambios en la base de datos
        try:
            db.session.commit()
            flash('La politica nacional y memoria ha sido actualizado con éxito.', 'success')
            return redirect(url_for('listar_politica_nacional_memoria'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar la politica nacional y memoria: {str(e)}', 'danger')
    
    # Renderizar la plantilla con los datos del caso cargados
    return render_template('editar_politica_nacional_memoria.html', politica_memoria=politica_memoria)

# ELIMINAR Politica nacional Memoria
@app.route('/eliminar_politica_nacional_memoria/<nombre_politica_memoria>', methods=['POST'])
@login_required
@roles_required('admin')
def eliminar_politica_nacional_memoria(nombre_politica_memoria):
    # Buscar el caso emblemático por nombre_politica_memoria
    politica_memoria = PoliticaNacionalMemoria.query.filter_by(nombre_politica_memoria=nombre_politica_memoria).first()

    if not politica_memoria:
        flash('La politica nacional y memoria no existe.', 'danger')
        return redirect(url_for('listar_politica_nacional_memoria'))

    try:
        # Eliminar el caso de la base de datos
        db.session.delete(politica_memoria)
        db.session.commit()

        flash('La politica nacional y memoria ha sido eliminado con éxito.', 'success')
    except Exception as e:
        db.session.rollback()  # Revertir la operación en caso de error
        flash(f'Error al eliminar la politica nacional y memoria: {str(e)}', 'danger')

    return redirect(url_for('listar_politica_nacional_memoria'))


######################################################################################################################################
########################################################################################################################################
##########                         AVANCES POLITICA NACIONAL Y MEMORIA                          ########################################
########################################################################################################################################
########################################################################################################################################

# Modelo para Avances de Política Nacional y/o Sitio de Memoria
class AvancePoliticaMemoria(db.Model):
    __tablename__ = 'avance_politica_memoria'
    id = db.Column(db.Integer, primary_key=True)
    nombre_politica_memoria = db.Column(db.String(200), db.ForeignKey('politica_nacional_memoria.nombre_politica_memoria'), nullable=False)
    ocurrencias_periodo = db.Column(db.String(401), nullable=True)
    actividades_realizadas = db.Column(db.String(400), nullable=True)
    estado_actual_gestion = db.Column(db.String(400), nullable=True)
    recomendaciones = db.Column(db.String(350), nullable=True)
    otro_asunto = db.Column(db.String(255), nullable=True)
    responsable_registro = db.Column(db.String(100), nullable=True)
    fecha_registro = db.Column(db.DateTime, default=obtener_hora_peru, nullable=True)

@app.route('/form_avances_politica_nacional_memoria', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def form_avances_politica_nacional_memoria():
    if request.method == 'POST':
        # Crear un nuevo avance
        nuevo_avance_politica_memoria = AvancePoliticaMemoria(
            nombre_politica_memoria=request.form['nombre_politica_memoria'].strip().lower(),
            ocurrencias_periodo=request.form.get('ocurrencias_periodo', ''),
            actividades_realizadas=request.form.get('actividades_realizadas', ''),
            estado_actual_gestion=request.form.get('estado_actual_gestion', ''),
            recomendaciones=request.form.get('recomendaciones', ''),
            otro_asunto=request.form.get('otro_asunto', ''),
            responsable_registro=request.form.get('responsable_registro', '')
        )
        db.session.add(nuevo_avance_politica_memoria)
        db.session.commit()

        flash('Avance de la Política Nacional y/o Sitio de Memoria registrado exitosamente.', 'success')
        return redirect(url_for('listar_avances_politica_nacional_memoria'))

    # Obtener la lista de todas las políticas nacionales o sitios de memoria
    politicas = PoliticaNacionalMemoria.query.all()
    return render_template('form_avances_politica_nacional_memoria.html', politicas=politicas)


# LISTAR AVANCES POLITICA Y MEMORIA
@app.route('/listar_avances_politica_nacional_memoria')
@login_required
@roles_required('admin', 'editor', 'viewer')
def listar_avances_politica_nacional_memoria():
    # Obtener los registros en orden descendente por la fecha de registro
    avances_politica_memoria = AvancePoliticaMemoria.query.order_by(AvancePoliticaMemoria.fecha_registro.desc()).all()
    return render_template('listar_avances_politica_nacional_memoria.html', avances_politica_memoria=avances_politica_memoria)

# EDITAR AVANCES POLITICA Y MEMORIA
@app.route('/editar_avances_politica_nacional_memoria/<int:id>', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'editor')
def editar_avances_politica_nacional_memoria(id):
    # Buscar el proceso de iniciativa por id usando filter_by y first()
    avances_politica_memoria = AvancePoliticaMemoria.query.filter_by(id=id).first()

    if not avances_politica_memoria:
        flash('El avance de politica nacional y/o memoria no existe.', 'danger')
        return redirect(url_for('listar_avances_politica_nacional_memoria'))  # Redirigir si no se encuentra

    if request.method == 'POST':
        # Asignar los valores recibidos desde el formulario
        avances_politica_memoria.nombre_politica_memoria = request.form['nombre_politica_memoria'].strip().lower()
        avances_politica_memoria.ocurrencias_periodo = request.form.get('ocurrencias_periodo', '')
        avances_politica_memoria.actividades_realizadas = request.form.get('actividades_realizadas', '')
        avances_politica_memoria.estado_actual_gestion = request.form.get('estado_actual_gestion', '')
        avances_politica_memoria.recomendaciones = request.form.get('recomendaciones', '')
        avances_politica_memoria.otro_asunto = request.form.get('otro_asunto', '')
        avances_politica_memoria.responsable_registro = request.form.get('responsable_registro', '')

        # Guardar cambios en la base de datos
        try:
            db.session.commit()
            flash('El avance de politica nacional y/o memoria ha sido actualizado exitosamente.', 'success')
            return redirect(url_for('listar_avances_politica_nacional_memoria'))
        except:
            db.session.rollback()
            flash('Hubo un error al actualizar el avance de politica nacional y/o memoria.', 'danger')
            return redirect(url_for('listar_avances_politica_nacional_memoria'))  # Redirigir si no hay error

    # Renderizar el formulario con los datos existentes
    politica_memoria = PoliticaNacionalMemoria.query.all()  # Asumiendo que hay un modelo de Iniciativas
    return render_template('editar_avances_politica_nacional_memoria.html', avances_politica_memoria=avances_politica_memoria, politica_memoria=politica_memoria)

# ELIMINAR AVANCES POLITICA Y MEMORIA
@app.route('/eliminar_avances_politica_nacional_memoria/<int:id>', methods=['POST'])
@login_required
@roles_required('admin')
def eliminar_avances_politica_nacional_memoria(id):
    # Buscar el proceso de iniciativa por su id
    avances_caso_emblematico = AvancePoliticaMemoria.query.filter_by(id=id).first()

    if not avances_caso_emblematico:
        flash('El avance de politica nacional y/o memoria no existe.', 'danger')
        return redirect(url_for('listar_avances_politica_nacional_memoria'))
    
    try:
        # Eliminar el proceso de la base de datos
        db.session.delete(avances_caso_emblematico)
        db.session.commit()
        flash('El avance de politica nacional y/o memoria ha sido eliminado correctamente.', 'success')
    except:
        # En caso de error, hacer rollback
        db.session.rollback()
        flash('Hubo un error al intentar eliminar el avance de politica nacional y/o memoria.', 'danger')

    # Redirigir a la lista de procesos de iniciativas
    return redirect(url_for('listar_avances_politica_nacional_memoria'))









########################################################################################################################################
########################################################################################################################################
##########                        CONSULTA AJAX PARA OBTENER OBJETIVO ESPECIFICO y numero de forms                    ##################
########################################################################################################################################
########################################################################################################################################

@app.route('/get_objetivo_especifico/<nombre_iniciativa>', methods=['GET'])
@login_required
@roles_required('admin', 'editor')
def get_objetivo_especifico(nombre_iniciativa):
    iniciativa = Iniciativa.query.filter_by(nombre_iniciativa=nombre_iniciativa).first()
    if not iniciativa:
        return jsonify({'error': 'Iniciativa no encontrada'}), 404
    
    # Contar registros existentes y sumar 1 para el próximo número
    numero_registros = ProcesoIniciativa.query.filter_by(
        nombre_iniciativa=nombre_iniciativa
    ).count()
    
    return jsonify({
        'objetivo_especifico': iniciativa.objetivo_especifico,
        'numero_formularios': numero_registros + 1  # +1 para el nuevo registro
    })


########################################################################################################################################
########################################################################################################################################
##########                        CONSULTA AJAX PARA OBTENER COMPONENTES                     ###########################################
########################################################################################################################################
########################################################################################################################################
@app.route('/get_componentes/<nombre_iniciativa>', methods=['GET'])
@login_required
@roles_required('admin', 'editor')
def get_componentes(nombre_iniciativa):
    iniciativa = Iniciativa.query.filter_by(nombre_iniciativa=nombre_iniciativa).first()
    if iniciativa:
        return {
            'componente_1': iniciativa.componente_1,
            'componente_2': iniciativa.componente_2,
            'componente_3': iniciativa.componente_3
        }
    else:
        return {'error': 'Iniciativa no encontrada'}, 404


########################################################################################################################################
########################################################################################################################################
##########         CONSULTA AJAX PARA OBTENER NUM FORMULARIOS EN CASOS EMBLEMATICOS            #########################################
########################################################################################################################################
########################################################################################################################################
@app.route('/get_numero_formulario/<nombre_caso>', methods=['GET'])
@login_required
@roles_required('admin', 'editor')
def get_numero_formulario(nombre_caso):
    # Buscar el caso emblemático en la base de datos
    caso = CasoEmblematico.query.filter_by(nombre_caso=nombre_caso).first()

    if caso:
        # Contar cuántos formularios de AvanceCasoEmblematico ya están asociados a este caso
        numero_formularios = AvanceCasoEmblematico.query.filter_by(nombre_caso=nombre_caso).count()

        # Devolver el número de formulario de monitoreo
        return jsonify({
            'numero_formularios': numero_formularios + 1  # El siguiente formulario será el siguiente número
        })
    else:
        # Si no se encuentra el caso, devolver un error 404
        return jsonify({'error': 'Caso Emblemático no encontrado'}), 404


########################################################################################################################################
########################################################################################################################################
##########         CONSULTA AJAX PARA OBTENER NUM FORMULARIOS EN AvancePoliticaMemoria         #########################################
########################################################################################################################################
########################################################################################################################################
@app.route('/get_numero_formulario_politica/<nombre_politica_memoria>', methods=['GET'])
@login_required
@roles_required('admin', 'editor')
def get_numero_formulario_politica(nombre_politica_memoria):
    politica = PoliticaNacionalMemoria.query.filter_by(nombre_politica_memoria=nombre_politica_memoria).first()

    if politica:
        # Contar cuántos formularios de avances ya están asociados a esta política
        numero_formularios = AvancePoliticaMemoria.query.filter_by(nombre_politica_memoria=nombre_politica_memoria).count()

        # Devolver el número del siguiente formulario
        return jsonify({
            'numero_formulario': numero_formularios + 1  # El siguiente formulario será el siguiente número
        })
    else:
        return jsonify({'error': 'Política y/o memoria no encontrada'}), 404


if __name__ == '__main__':
    app.run(debug=True)
