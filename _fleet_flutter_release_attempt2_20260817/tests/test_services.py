import pytest
from app import create_app, db
from app.models import User, Habit, HabitCompletion

@pytest.fixture
def app():
    app = create_app({
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'JWT_SECRET_KEY': 'test-secret-key',
        'TESTING': True
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client):
    def register_and_login(username, email, password):
        client.post('/api/register', json={
            'username': username,
            'email': email,
            'password': password
        })
        response = client.post('/api/login', json={
            'username': username,
            'password': password
        })
        return response
    return register_and_login

class TestAuth:
    def test_register_user(self, client):
        response = client.post('/api/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'User registered successfully'
    
    def test_register_duplicate_username(self, client):
        client.post('/api/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        })
        response = client.post('/api/register', json={
            'username': 'testuser',
            'email': 'test2@example.com',
            'password': 'password123'
        })
        assert response.status_code == 400
    
    def test_login_success(self, client, auth_client):
        auth_client('testuser', 'test@example.com', 'password123')
        response = client.post('/api/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
    
    def test_login_invalid_credentials(self, client):
        client.post('/api/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        })
        response = client.post('/api/login', json={
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        assert response.status_code == 401

class TestHabits:
    def test_create_habit(self, client, auth_client):
        auth_client('testuser', 'test@example.com', 'password123')
        response = client.post('/api/habits', json={
            'name': 'Drink water',
            'description': 'Drink 8 glasses of water daily'
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['name'] == 'Drink water'
        assert data['description'] == 'Drink 8 glasses of water daily'
        assert data['completed'] == False
    
    def test_get_habits(self, client, auth_client):
        auth_client('testuser', 'test@example.com', 'password123')
        client.post('/api/habits', json={'name': 'Drink water'})
        client.post('/api/habits', json={'name': 'Exercise'})
        
        response = client.get('/api/habits')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 2
        assert data[0]['name'] == 'Drink water'
        assert data[1]['name'] == 'Exercise'
    
    def test_mark_habit_complete(self, client, auth_client):
        auth_client('testuser', 'test@example.com', 'password123')
        response = client.post('/api/habits', json={'name': 'Drink water'})
        habit_id = response.get_json()['id']
        
        response = client.post(f'/api/habits/{habit_id}/complete')
        assert response.status_code == 200
        
        response = client.get('/api/habits')
        data = response.get_json()
        assert data[0]['completed'] == True

class TestDashboard:
    def test_get_dashboard(self, client, auth_client):
        auth_client('testuser', 'test@example.com', 'password123')
        client.post('/api/habits', json={'name': 'Drink water'})
        client.post('/api/habits', json={'name': 'Exercise'})
        
        response = client.get('/api/dashboard')
        assert response.status_code == 200
        data = response.get_json()
        assert data['total_habits'] == 2
        assert data['completed_habits'] == 0
        assert len(data['habits']) == 2