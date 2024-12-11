from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Alumno(db.Model):
    __tablename__ = 'alumnos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    matricula = db.Column(db.String(50), nullable=False, unique=True)
    promedio = db.Column(db.Float, nullable=False)
    fotoPerfilUrl = db.Column(db.String(255), nullable=True)
    password = db.Column(db.String(255), nullable=False)

    def __init__(self, nombres, apellidos, matricula, promedio, password):
        # Validaciones
        if not nombres or not isinstance(nombres, str):
            raise ValueError("Nombres debe ser una cadena de caracteres")
        if not apellidos or not isinstance(apellidos, str):
            raise ValueError("Apellidos debe ser una cadena de caracteres")
        if not matricula or not isinstance(matricula, str):
            raise ValueError("Matrícula debe ser una cadena de caracteres")
        if not isinstance(promedio, (int, float)) or promedio < 0 or promedio > 10:
            raise ValueError("Promedio debe ser un número entre 0 y 10")
        if not password or not isinstance(password, str):
            raise ValueError("Password debe ser una cadena de caracteres")

        # Asignación de valores
        self.nombres = nombres
        self.apellidos = apellidos
        self.matricula = matricula
        self.promedio = promedio
        self.password = password

    def to_dict(self):
        """Devuelve los datos del alumno en formato de diccionario"""
        return {
            "id": self.id,
            "nombres": self.nombres,
            "apellidos": self.apellidos,
            "matricula": self.matricula,
            "promedio": self.promedio,
            "fotoPerfilUrl": self.fotoPerfilUrl,
            "password": self.password
        }

class Profesor(db.Model):
    __tablename__ = 'profesores'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    numeroEmpleado = db.Column(db.Integer, nullable=False, unique=True)
    horasClase = db.Column(db.Integer, nullable=False)

    def __init__(self, nombres, apellidos, numeroEmpleado, horasClase):
        # Validaciones
        if not nombres or not isinstance(nombres, str):
            raise ValueError("Nombres debe ser una cadena de caracteres")
        if not apellidos or not isinstance(apellidos, str):
            raise ValueError("Apellidos debe ser una cadena de caracteres")
        if not isinstance(numeroEmpleado, int):
            raise ValueError("Número de Empleado debe ser un número entero")
        if not isinstance(horasClase, int) or horasClase < 0:
            raise ValueError("Horas de Clase debe ser un número positivo")

        # Asignación de valores
        self.nombres = nombres
        self.apellidos = apellidos
        self.numeroEmpleado = numeroEmpleado
        self.horasClase = horasClase

    def to_dict(self):
        """Devuelve los datos del profesor en formato de diccionario"""
        return {
            "id": self.id,
            "nombres": self.nombres,
            "apellidos": self.apellidos,
            "numeroEmpleado": self.numeroEmpleado,
            "horasClase": self.horasClase
        }
