import random
import string
import time
import uuid
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from models import db, Alumno, Profesor
import boto3
from botocore.exceptions import NoCredentialsError
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:password-admin@spring-demo-db.c80xrbdqj9ve.us-east-1.rds.amazonaws.com/springdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


# Inicialización de AWS
AWS_CONFIG = {
    'aws_access_key_id': 'ASIARL6MTJTELW2P635M',
    'aws_secret_access_key': 'XQ/BYkQb3s0VFItxNoLMGthCvVbBG4glwevTyCHD',
    'aws_session_token': 'IQoJb3JpZ2luX2VjENz//////////wEaCXVzLXdlc3QtMiJIMEYCIQDAn/rvm0VlEGKspGUrGBLIZBirl35/TgII/J46qrdf8AIhAPK5wnFJFXeTORzN8zTVeGPocp3xyLOMqmX4MIsQJmQZKrgCCJX//////////wEQABoMMDk0MzgxNDkzNDQ4IgyPB6Jw/4u6ojDg5ocqjAKdjQ4LPBowajtk/d0g3IdjCC2/lusPg+Tu0swfvEmGbKtV5nQhVPIR4IWLlG7JNkvipurmBL/AwEyFDVqNvw5MCVctPphy7+tyq+z4Oge2cFnN2ZSRwIfay5qEGVVF1+b7UbXbiiY+vXTMK+3cW7WFgmGDHH5fPrvRm/Ye94rzt/EBulRdJvff1WGfnCNrgk8nrTm6NiY6LjqHnSIIsmgovgADLFcSoC5ViogzcpLosnT3nDj8tiRAL4QH071kY8WcxM/699RzSKfA4QT3maOGvYqwiu4DLcXSdsKzovNmvRYmHhPMNN88pyyBbFBhPkgfPfQ3VnhwOIp7fhMWHF1C3wFTBro95Wpde1QOMK694roGOpwBGZ+nW0jcMrRXrqiaKpRd8YvMbKJjFQJnBe0oiqk4/BJl93tIw9HljxSxeemwzTGJn5sW64w0bd8D28CFpRM8Ain2xYNO98mks2nxL17hdaKiNZZL+/OSLDxs1j9jTrb/RA+hHIKLTB6LgleoUTwXVK+C6VynCtZV93anCklcZLyhOeyppvJJ9yXqm9y0smzLJevG5dtE0rrFlhem',
    'region_name': 'us-east-1'
}

# Crear clientes de AWS
s3 = boto3.client('s3', **AWS_CONFIG)
sns_client = boto3.client('sns', **AWS_CONFIG)
dynamodb = boto3.resource('dynamodb', **AWS_CONFIG)

# Variables de AWS
BUCKET_NAME = 'alumnos-profile-picture'
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:094381493448:alumno-notificaciones'
table = dynamodb.Table('sesiones-alumnos')

# Crear base de datos si no existe
with app.app_context():
    db.create_all()

# --- Rutas para Alumnos ---

@app.route('/alumnos', methods=['POST'])
def add_alumno():
    data = request.get_json()
    try:
        nuevo_alumno = Alumno(
            nombres=data['nombres'],
            apellidos=data['apellidos'],
            matricula=data['matricula'],
            promedio=data['promedio'],
            password=data['password']
        )
        db.session.add(nuevo_alumno)
        db.session.commit()
        return jsonify(nuevo_alumno.to_dict()), 201
    except (KeyError, ValueError) as e:
        return jsonify({'error': str(e)}), 400

@app.route('/alumnos', methods=['GET'])
def get_alumnos():
    alumnos = Alumno.query.all()
    return jsonify([alumno.to_dict() for alumno in alumnos]), 200

@app.route('/alumnos/<int:id>', methods=['GET'])
def get_alumno_by_id(id):
    alumno = Alumno.query.get(id)
    if alumno is None:
        return jsonify({'error': 'Alumno no encontrado'}), 404
    return jsonify(alumno.to_dict()), 200

@app.route('/alumnos/<int:id>', methods=['PUT'])
def update_alumno(id):
    data = request.get_json()
    alumno = Alumno.query.get(id)
    if alumno is None:
        return jsonify({'error': 'Alumno no encontrado'}), 404

    try:
        if 'nombres' in data and (not data['nombres'] or not isinstance(data['nombres'], str)):
            return jsonify({'error': 'Nombre inválido'}), 400
        if 'apellidos' in data and (not data['apellidos'] or not isinstance(data['apellidos'], str)):
            return jsonify({'error': 'Apellido inválido'}), 400
        if 'promedio' in data and (not isinstance(data['promedio'], (int, float)) or data['promedio'] < 0 or data['promedio'] > 10):
            return jsonify({'error': 'Promedio inválido'}), 400

        alumno.nombres = data.get('nombres', alumno.nombres)
        alumno.apellidos = data.get('apellidos', alumno.apellidos)
        alumno.matricula = data.get('matricula', alumno.matricula)
        alumno.promedio = data.get('promedio', alumno.promedio)
        db.session.commit()
        return jsonify(alumno.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@app.route('/alumnos/<int:id>', methods=['DELETE'])
def delete_alumno(id):
    alumno = Alumno.query.get(id)
    if alumno is None:
        return jsonify({'error': 'Alumno no encontrado'}), 404
    db.session.delete(alumno)
    db.session.commit()
    return jsonify({'message': 'Alumno eliminado'}), 200

@app.route('/alumnos/<int:id>/fotoPerfil', methods=['POST'])
def upload_profile_picture(id):
    alumno = Alumno.query.get(id)
    if not alumno:
        return jsonify({'error': 'Alumno no encontrado'}), 404

    if 'foto' not in request.files:
        return jsonify({'error': 'Archivo no proporcionado'}), 400

    file = request.files['foto']
    if file.filename == '':
        return jsonify({'error': 'El nombre del archivo está vacío'}), 400

    try:
        filename = secure_filename(file.filename)
        s3_path = f"{id}/{filename}"
        s3.upload_fileobj(file, BUCKET_NAME, s3_path, ExtraArgs={'ACL': 'public-read', 'ContentType': file.content_type})
        photo_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{s3_path}"
        alumno.fotoPerfilUrl = photo_url
        db.session.commit()

        return jsonify({'message': 'Foto de perfil subida con éxito', 'fotoPerfilUrl': photo_url}), 200
    except NoCredentialsError:
        return jsonify({'error': 'No se encontraron credenciales AWS'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/alumnos/<int:id>/email', methods=['POST'])
def send_email_notification(id):
    alumno = Alumno.query.get(id)
    if not alumno:
        return jsonify({'error': 'Alumno no encontrado'}), 404

    email_content = f"Información del alumno:\nNombre: {alumno.nombres} {alumno.apellidos}\nPromedio: {alumno.promedio}\n"
    
    try:
        sns_client.publish(TopicArn=SNS_TOPIC_ARN, Message=email_content, Subject="Calificaciones y datos del alumno")
        return jsonify({'message': 'Notificación enviada correctamente'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/alumnos/<int:id>/session/login', methods=['POST'])
def login_session(id):
    data = request.get_json()
    alumno = Alumno.query.get(id)
    if not alumno:
        return jsonify({'error': 'Alumno no encontrado'}), 404

    if not 'password' in data:
        return jsonify({'error': 'Contraseña requerida'}), 400

    if alumno.password != data['password']:
        return jsonify({'error': 'Contraseña incorrecta'}), 400

    session_id = str(uuid.uuid4())
    session_string = ''.join(random.choices(string.ascii_letters + string.digits, k=128))
    timestamp = int(time.time())

    table.put_item(Item={'id': session_id, 'fecha': timestamp, 'alumnoId': id, 'active': True, 'sessionString': session_string})

    return jsonify({'message': 'Sesión creada', 'sessionString': session_string, 'sessionId': session_id}), 200

@app.route('/alumnos/<int:id>/session/verify', methods=['POST'])
def verify_session(id):
    data = request.get_json()
    if 'sessionString' not in data:
        return jsonify({'error': 'SessionString requerido'}), 400

    response = table.scan(
        FilterExpression='alumnoId = :alumnoId AND sessionString = :sessionString',
        ExpressionAttributeValues={':alumnoId': id, ':sessionString': data['sessionString']}
    )

    items = response.get('Items', [])
    if not items:
        return jsonify({'error': 'Sesión no válida'}), 400

    session = items[0]
    if session['active']:
        return jsonify({'message': 'Sesión verificada'}), 200
    else:
        return jsonify({'error': 'Sesión no activa'}), 400


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
