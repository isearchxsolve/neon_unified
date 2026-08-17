from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from app import db, bcrypt
from app.models import User, Habit, HabitCompletion

main_bp = Blueprint('main', __name__)

@main_bp.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': 'User registered successfully'}), 201

@main_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Missing username or password'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    access_token = create_access_token(identity=user.id)
    
    return jsonify({'access_token': access_token}), 200

@main_bp.route('/api/habits', methods=['GET'])
@jwt_required()
def get_habits():
    current_user_id = get_jwt_identity()
    habits = Habit.query.filter_by(user_id=current_user_id).all()
    
    habits_list = []
    for habit in habits:
        habits_list.append({
            'id': habit.id,
            'name': habit.name,
            'description': habit.description,
            'completed': habit.completed,
            'created_at': habit.created_at.isoformat() if habit.created_at else None
        })
    
    return jsonify(habits_list), 200

@main_bp.route('/api/habits', methods=['POST'])
@jwt_required()
def create_habit():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'error': 'Habit name is required'}), 400
    
    habit = Habit(
        name=data['name'],
        description=data.get('description'),
        user_id=current_user_id
    )
    
    db.session.add(habit)
    db.session.commit()
    
    return jsonify({
        'id': habit.id,
        'name': habit.name,
        'description': habit.description,
        'completed': habit.completed,
        'created_at': habit.created_at.isoformat() if habit.created_at else None
    }), 201

@main_bp.route('/api/habits/<int:habit_id>/complete', methods=['POST'])
@jwt_required()
def mark_habit_complete(habit_id):
    current_user_id = get_jwt_identity()
    
    habit = Habit.query.filter_by(id=habit_id, user_id=current_user_id).first()
    
    if not habit:
        return jsonify({'error': 'Habit not found'}), 404
    
    habit.mark_complete()
    
    completion = HabitCompletion(habit_id=habit.id)
    db.session.add(completion)
    db.session.commit()
    
    return jsonify({'message': 'Habit marked as complete'}), 200

@main_bp.route('/api/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    current_user_id = get_jwt_identity()
    
    total_habits = Habit.query.filter_by(user_id=current_user_id).count()
    completed_habits = Habit.query.filter_by(user_id=current_user_id, completed=True).count()
    
    habits = Habit.query.filter_by(user_id=current_user_id).all()
    habits_data = []
    for habit in habits:
        habits_data.append({
            'id': habit.id,
            'name': habit.name,
            'completed': habit.completed
        })
    
    return jsonify({
        'total_habits': total_habits,
        'completed_habits': completed_habits,
        'habits': habits_data
    }), 200