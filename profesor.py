class Profesor:
    def __init__(self, id, nombres, apellidos, numeroEmpleado, horasClase):
        # Validar que cada campo cumpla con las expectativas
        if not isinstance(id, int):
            raise ValueError("ID debe ser un número entero")
        if not nombres or not isinstance(nombres, str):
            raise ValueError("Nombres debe ser una cadena de caracteres")
        if not apellidos or not isinstance(apellidos, str):
            raise ValueError("Apellidos debe ser una cadena de caracteres")
        if not numeroEmpleado or not isinstance(numeroEmpleado, int):
            raise ValueError("Número de Empleado debe ser un número entero")
        if not isinstance(horasClase, (int, float)) or horasClase < 0:
            raise ValueError("Horas de Clase debe ser un número positivo")

        # Inicialización de los atributos del objeto
        self.id = id
        self.nombres = nombres
        self.apellidos = apellidos
        self.numeroEmpleado = numeroEmpleado
        self.horasClase = horasClase

    def to_dict(self):
        """Devuelve los datos del profesor en forma de diccionario"""
        return {
            "id": self.id,
            "nombres": self.nombres,
            "apellidos": self.apellidos,
            "numeroEmpleado": self.numeroEmpleado,
            "horasClase": self.horasClase
        }
