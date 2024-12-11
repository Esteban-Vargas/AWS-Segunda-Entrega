class Alumno:
    def __init__(self, id, nombres, apellidos, matricula, promedio):
        # Validar que cada campo cumpla con las expectativas
        if not isinstance(id, int):
            raise ValueError("ID debe ser un número entero")
        if not nombres or not isinstance(nombres, str):
            raise ValueError("Nombres debe ser una cadena de caracteres")
        if not apellidos or not isinstance(apellidos, str):
            raise ValueError("Apellidos debe ser una cadena de caracteres")
        if not matricula or not isinstance(matricula, str):
            raise ValueError("Matrícula debe ser una cadena de caracteres")
        if not isinstance(promedio, (int, float)) or promedio < 0 or promedio > 10:
            raise ValueError("Promedio debe ser un número entre 0 y 10")

        # Inicialización de los atributos del objeto
        self.id = id
        self.nombres = nombres
        self.apellidos = apellidos
        self.matricula = matricula
        self.promedio = promedio

    def to_dict(self):
        """Devuelve los datos del estudiante en forma de diccionario"""
        return {
            "id": self.id,
            "nombres": self.nombres,
            "apellidos": self.apellidos,
            "matricula": self.matricula,
            "promedio": self.promedio
        }
