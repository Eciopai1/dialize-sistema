from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from models import db, User, Evaluation
from datetime import datetime
import os
from dotenv import load_dotenv
import jwt

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar extensões
db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# Criar admin na primeira execução
def create_admin():
    with app.app_context():
        db.create_all()
    admin = User.query.filter_by(is_admin=True).first()
    if not admin:
        admin = User(
            id='admin',
            name='Administrador',
            email=os.getenv('ADMIN_USERNAME'),
            password_hash=bcrypt.generate_password_hash(os.getenv('ADMIN_PASSWORD')).decode('utf-8'),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()

# Rotas da API
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.get(data.get('patientId'))
    
    if user and bcrypt.check_password_hash(user.password_hash, data.get('password')):
        login_user(user)
        return jsonify({
            'success': True,
            'name': user.name,
            'token': jwt.encode(
                {'user_id': user.id, 'is_admin': user.is_admin},
                app.config['SECRET_KEY'],
                algorithm='HS256'
            )
        })
    
    return jsonify({'success': False, 'message': 'Credenciais inválidas'}), 401

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if User.query.get(data.get('patientId')):
        return jsonify({'success': False, 'message': 'Paciente já cadastrado'}), 400
    
    new_user = User(
        id=data.get('patientId'),
        name=data.get('name'),
        email=data.get('email'),
        phone=data.get('phone'),
        password_hash=bcrypt.generate_password_hash(data.get('password')).decode('utf-8')
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Cadastro realizado com sucesso'})

@app.route('/api/evaluation', methods=['POST'])
@login_required
def submit_evaluation():
    data = request.get_json()
    
    evaluation = Evaluation(
        patient_id=current_user.id,
        session_date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
        session_rating=data['ratings']['session'],
        doctor_rating=data['ratings']['doctor'],
        nurse_rating=data['ratings']['nurse'],
        technician_rating=data['ratings']['technician'],
        food_rating=data['ratings']['food'],
        cleaning_rating=data['ratings']['cleaning'],
        transport_rating=data['ratings']['transport'],
        doctor_name=data['professionals'].get('doctor'),
        nurse_name=data['professionals'].get('nurse'),
        technician_name=data['professionals'].get('technician'),
        comments=data.get('comments')
    )
    
    db.session.add(evaluation)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Avaliação registrada com sucesso'})

@app.route('/api/evaluations', methods=['GET'])
@login_required
def get_evaluations():
    if current_user.is_admin:
        evaluations = Evaluation.query.all()
    else:
        evaluations = current_user.evaluations
    
    return jsonify([eval.to_dict() for eval in evaluations])

# Rotas do Admin
@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return jsonify({'error': 'Acesso não autorizado'}), 403
    
    evaluations = Evaluation.query.all()
    users = User.query.filter_by(is_admin=False).all()
    
    return render_template('admin.html', 
                         evaluations=evaluations,
                         users=users,
                         current_user=current_user)

@app.route('/')
def serve_app():
    return send_from_directory('templates', 'index.html')

if __name__ == '__main__':
    app.run(debug=True)
