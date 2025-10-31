import os
import boto3
from flask import Flask, request, redirect, url_for, render_template, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, func
from sqlalchemy.orm import declarative_base, sessionmaker
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# === DATABASE (SQLite) ===
DATABASE_URI = 'sqlite:///recipes.db'
engine = create_engine(DATABASE_URI)
Base = declarative_base()

# === S3 (สำหรับรูป) ===
S3_BUCKET = os.environ.get('S3_BUCKET')
s3_client = boto3.client('s3') if S3_BUCKET else None

def upload_to_s3(file):
    if not s3_client or not file:
        return None
    filename = secure_filename(file.filename)
    s3_client.upload_fileobj(file, S3_BUCKET, f'images/{filename}', ExtraArgs={'ACL': 'public-read'})
    return filename

# === Models ===
class User(UserMixin, Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(200), nullable=False)
    recipes = relationship('Recipe', backref='author', lazy=True)
    favorites = relationship('Favorite', backref='user', lazy=True)

class Recipe(Base):
    __tablename__ = 'recipes'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    ingredients = Column(Text, nullable=False)
    instructions = Column(Text, nullable=False)
    image = Column(String(200), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

class Favorite(Base):
    __tablename__ = 'favorites'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    recipe_id = Column(Integer, ForeignKey('recipes.id'), nullable=False)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# === Flask-Login ===
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    session = Session()
    user = session.get(User, int(user_id))
    session.close()
    return user

# === หน้าแรก (รองรับ POST ค้นหา) ===
@app.route('/', methods=['GET', 'POST'])
def home():
    session = Session()
    recipes_with_count = session.query(
        Recipe,
        func.count(Favorite.id).label('fav_count')
    ).outerjoin(Favorite, Recipe.id == Favorite.recipe_id)\
     .group_by(Recipe.id).all()

    matching_recipes = recipes_with_count

    if request.method == 'POST':
        ingredients_input = request.form.get('ingredients', '').strip()
        if ingredients_input:
            user_ings = [ing.strip().lower() for ing in ingredients_input.split(',')]
            matching_recipes = []
            for recipe, fav_count in recipes_with_count:
                recipe_ings = [ing.strip().lower() for ing in recipe.ingredients.split(',')]
                matches = sum(1 for ing in user_ings if any(ing in r for r in recipe_ings))
                if matches >= len(user_ings) * 0.5:
                    matching_recipes.append((recipe, fav_count))

    session.close()
    return render_template('home.html', recipes=matching_recipes)

# === Register ===
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username and password:
            session = Session()
            if session.query(User).filter_by(username=username).first():
                flash('ชื่อผู้ใช้นี้มีแล้ว')
            else:
                hashed = generate_password_hash(password)
                user = User(username=username, password=hashed)
                session.add(user)
                session.commit()
                session.close()
                flash('สมัครสมาชิกสำเร็จ! กรุณาเข้าสู่ระบบ')
                return redirect(url_for('login'))
    return render_template('register.html')

# === Login ===
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        session = Session()
        user = session.query(User).filter_by(username=username).first()
        session.close()
        if user and check_password_hash(user.password, password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('home'))
        flash('ชื่อผู้ใช้หรือรหัสผ่านผิด')
    return render_template('login.html')

# === Logout ===
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# === เพิ่มสูตร (เหลือ 1 อัน) ===
@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_recipe():
    if request.method == 'POST':
        name = request.form['name']
        ingredients = request.form['ingredients']
        instructions = request.form['instructions']
        image_file = request.files.get('image')
        image_filename = upload_to_s3(image_file) if image_file else None

        session = Session()
        recipe = Recipe(name=name, ingredients=ingredients, instructions=instructions, image=image_filename, user_id=current_user.id)
        session.add(recipe)
        session.commit()
        session.close()
        return redirect(url_for('home'))
    return render_template('add.html')

# === แก้ไขสูตร (เปลี่ยนชื่อ + route) ===
@app.route('/edit/<int:recipe_id>', methods=['GET', 'POST'])
@login_required
def edit_recipe(recipe_id):
    session = Session()
    recipe = session.get(Recipe, recipe_id)
    
    if not recipe or recipe.user_id != current_user.id:
        flash('ไม่พบสูตรหรือไม่มีสิทธิ์', 'error')
        return redirect(url_for('home'))

    if request.method == 'POST':
        recipe.name = request.form['name']
        recipe.ingredients = request.form['ingredients']
        recipe.instructions = request.form['instructions']
        image_file = request.files.get('image')
        if image_file and image_file.filename:
            recipe.image = upload_to_s3(image_file)
        session.commit()
        flash('อัปเดตสูตรสำเร็จ!', 'success')
        return redirect(url_for('view_recipe', recipe_id=recipe.id))
    
    session.close()
    return render_template('edit.html', recipe=recipe)

# === ลบสูตร ===
@app.route('/delete/<int:recipe_id>')
@login_required
def delete_recipe(recipe_id):
    session = Session()
    recipe = session.get(Recipe, recipe_id)
    if recipe and recipe.user_id == current_user.id:
        session.delete(recipe)
        session.commit()
    session.close()
    return redirect(url_for('home'))

# === บันทึกสูตร ===
@app.route('/favorite/<int:recipe_id>')
@login_required
def favorite(recipe_id):
    session = Session()
    existing = session.query(Favorite).filter_by(user_id=current_user.id, recipe_id=recipe_id).first()
    if not existing:
        fav = Favorite(user_id=current_user.id, recipe_id=recipe_id)
        session.add(fav)
    session.commit()
    session.close()
    return redirect(request.referrer or url_for('home'))

# === สูตรที่บันทึก ===
@app.route('/favorites')
@login_required
def favorites():
    session = Session()
    fav_recipes = session.query(Recipe).join(Favorite).filter(Favorite.user_id == current_user.id).all()
    session.close()
    return render_template('favorites.html', recipes=fav_recipes)

# === ดูสูตร ===
@app.route('/recipe/<int:recipe_id>')
def view_recipe(recipe_id):
    session = Session()
    recipe = session.get(Recipe, recipe_id)
    session.close()
    if not recipe:
        return "ไม่พบ", 404
    return render_template('recipe.html', recipe=recipe)

# === สูตรของฉัน ===
@app.route('/my-recipes')
@login_required
def my_recipes():
    session = Session()
    recipes = session.query(Recipe)\
        .filter(Recipe.user_id == current_user.id)\
        .order_by(Recipe.id.desc())\
        .all()
    session.close()
    return render_template('my_recipes.html', recipes=recipes)

# === S3 URL ===
@app.context_processor
def inject_s3_url():
    bucket = os.environ.get('S3_BUCKET', 'recipe-app-lab-66070281')
    region = os.environ.get('AWS_REGION', 'us-east-1')
    return dict(s3_url=f"https://{bucket}.s3.{region}.amazonaws.com")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)