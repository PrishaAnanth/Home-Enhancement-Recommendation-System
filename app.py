from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from sklearn.neighbors import NearestNeighbors
import numpy as np
import os
import json
app = Flask(__name__)

# Set secret key from environment variable, with fallback to a default value
app.secret_key = os.environ.get('SECRET_KEY', 'b74e18ce7025ce0e48ceedf67d28f07a')

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'prisha'  # Replace with your MySQL username
app.config['MYSQL_PASSWORD'] = 'mysql'  # Replace with your MySQL password
app.config['MYSQL_DB'] = 'homerenov'  # Replace with your database name

mysql = MySQL(app)
# Category data dictionaries (same as before)
hall_category_data = {
    'traditional': [ 'tradhall1.jpeg', 'tradhall2.jpeg','tradhall4.jpeg','tradhalll5.jpeg','tradhall8.jpeg','tradhall6.jpeg'],
    'western': ['weslh3.jpg', 'hall1.jpg', 'weslh.jpg', 'weslh2.jpg', 'weshall1.jpeg', 'weshall2.jpeg', 'weshall3.jpeg', 'weshall4.jpeg', 'weshall5.jpeg', 'weshall6.jpeg'],
    'classical': ['claslh4.jpg', 'clashall1.jpeg','clashall4.jpg','clashall5.jpg', 'clashall2.jpeg', 'clashall3.jpeg', 'claslh.jpg', 'claslh2.jpg'],
}

kitchen_category_data = {
    'classical': ['claskitchen2.jpg', 'claskitchen4.jpeg', 'claskitchen5.jpeg', 'claskitchen13.jpeg', 'claskitchen14.jpeg', 'claskitchen16.jpg', 'claskitchen17.jpeg', 'claskitchen19.jpg'],
    'traditional': ['tradkitchen3.jpeg', 'tradkitchen6.jpeg', 'tradkitchen7.jpeg', 'tradkitchen8.jpeg', 'tradkitchen11.jpg','tradkitchen12.jpg', 'tradkitchen20.jpg'],
    'western': ['weskitchen1.jpg', 'weskitchen9.jpg', 'weskitchen10.jpg', 'weskitchen15.jpeg', 'weskitchen18.jpeg'],
}

bathroom_category_data = {
    'classical': ['clasbathroom2.jpg', 'clasbathroom3.jpeg', 'clasbathroom6.jpeg', 'clasbathroom9.jpeg', 'clasbathroom10.jpeg'],
    'western': ['wesbathroom.jpeg', 'wesbathroom1.jpg', 'wesbathroom4.jpeg', 'wesbathroom5.jpeg', 'wesbathroom7.jpeg', 'wesbathroom8.jpeg', 'wesbathroom11.jpeg'],
}

bedroom_category_data = {
    'classical': ['clasbedroom1.jpg', 'clasbedroom2.jpg', 'clasbedroom4.jpeg', 'clasbedroom7.jpeg', 'clasbedroom8.jpeg', 'clasbedroom13.jpeg'],
    'traditional': ['tradbedroom5.jpeg', 'tradbedroom6.jpeg','tradbedroom11.jpeg','tradbedroom8.jpeg','tradbedroom9.jpeg','tradbedroom10.jpeg'],
    'western': ['wesbedroom3.jpeg', 'wesbedroom9.jpeg', 'wesbedroom10.jpeg', 'wesbedroom11.jpeg', 'wesbedroom12.jpeg'],
}

interior_category_data = {
    'ceiling': ['wallceil1.jpeg', 'wallceil2.jpeg', 'wallceil3.jpeg', 'wallceil4.jpeg', 'wallceil5.jpeg'],
    'design': ['wallint1.jpeg', 'wallint2.jpeg', 'wallint3.jpeg', 'wallint4.jpeg', 'wallint5.jpeg', 'wallint6.jpeg', 'wallint7.jpeg', 'wallint8.jpeg', 'wallint9.jpeg', 'wallint10.jpeg']
}
garden_category_data = {
    'indoor': [
        'ingarden1.jpeg', 'ingarden2.jpeg', 'ingarden3.jpeg', 'ingarden4.jpeg',
        'ingarden5.jpeg', 'ingarden6.jpeg', 'ingarden7.jpeg', 'ingarden8.jpeg',
        'ingarden9.jpeg', 'ingarden10.jpeg', 'ingarden11.jpeg'
    ],
    'outdoor': [
        'outgarden1.jpeg', 'outgarden2.jpeg', 'outgarden3.jpeg', 'outgarden4.jpeg',
        'outgarden5.jpeg', 'outgarden6.jpeg', 'outgarden7.jpeg', 'outgarden8.jpeg',
        'outgarden9.jpeg', 'outgarden10.jpeg', 'outgarden11.jpeg'
    ]
}
paint_category_data = {
    'types': ['paintsugg.jpeg'],
    'combos': ['paints2.jpeg']
}

paints_category_data = {
    "red": ["blue", "white", "black"],
    "blue": ["yellow", "white", "grey"],
    "green": ["white", "brown", "yellow"],
    "yellow": ["blue", "green", "white"],
    "purple": ["yellow", "pink", "white"],
    "pink": ["purple", "white", "grey"],
    "black": ["white", "grey", "red"],
    "white": ["black", "blue", "green"],
    "grey": ["white", "black", "blue"],
    "brown": ["green", "white", "blue"],
}
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        address = request.form['address']
        phone = request.form['phone']
        pincode = request.form['pincode']

        cursor = mysql.connection.cursor()
        
        # Check if the user already exists
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('You have already signed up. Please log in.', 'error')
            return redirect(url_for('login'))  # Redirect to login page
        else:
            # Hash the password and insert new user
            hashed_password = generate_password_hash(password)
            cursor.execute("INSERT INTO users (name, email, password, address, phone, pincode) VALUES (%s, %s, %s, %s, %s, %s)",
                           (name, email, hashed_password, address, phone, pincode))
            mysql.connection.commit()
            cursor.close()
            flash('You have successfully signed up.', 'success')
            return redirect(url_for('login'))  # Redirect to login page after successful signup

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user and check_password_hash(user[3], password):
            session['user_id'] = user[0]
            flash('You have successfully logged in.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Username or password is wrong.', 'error')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect if not logged in
    return render_template('dashboard.html')

@app.route('/renovation')
def renovation():
    return render_template('renovation.html')

@app.route('/interior')
def interior():
    return render_template('interior.html')

@app.route('/garden', methods=['GET', 'POST'])
def garden():
    images = []
    if request.method == 'POST':
        category = request.form.get('category').strip().lower()
        if category in garden_category_data:
            images = garden_category_data[category]
        else:
            flash('Category not found. Please select a valid category.', 'error')
    else:
        for category_images in garden_category_data.values():
            images.extend(category_images)
    return render_template('garden.html', images=images)

@app.route('/hall', methods=['GET', 'POST'])
def hall():
    images = []
    if request.method == 'POST':
        category = request.form.get('category').strip().lower()
        if category in hall_category_data:
            images = hall_category_data[category]
        else:
            flash('Category not found. Please select a valid category.', 'error')
    else:
        for category_images in hall_category_data.values():
            images.extend(category_images)
    return render_template('hall.html', images=images)


@app.route('/kitchen', methods=['GET', 'POST'])
def kitchen():
   images = []
   if request.method == 'POST':
    category = request.form.get('category').strip().lower()
    if category in kitchen_category_data:
        images = kitchen_category_data[category]
    else:
        flash('Category not found. Please select a valid category.', 'error')
   else:
    for category_images in kitchen_category_data.values():
        images.extend(category_images)
   return render_template('kitchen.html', images=images)
@app.route('/bathroom', methods=['GET', 'POST'])
def bathroom():
    images = []
    if request.method == 'POST':
        category = request.form.get('category').strip().lower()
        if category in bathroom_category_data:
            images = bathroom_category_data[category]
        else:
            flash('Category not found. Please select a valid category.', 'error')
    else:
        for category_images in bathroom_category_data.values():
            images.extend(category_images)
    return render_template('bathroom.html', images=images)

@app.route('/bedroom', methods=['GET', 'POST'])
def bedroom():
    images = []
    if request.method == 'POST':
        category = request.form.get('category').strip().lower()
        if category in bedroom_category_data:
            images = bedroom_category_data[category]
        else:
            flash('Category not found. Please select a valid category.', 'error')
    else:
        for category_images in bedroom_category_data.values():
            images.extend(category_images)
    return render_template('bedroom.html', images=images)

@app.route('/wall', methods=['GET', 'POST'])
def wall():
    images = []
    if request.method == 'POST':
        category = request.form.get('category').strip().lower()
        if category in interior_category_data:
            images = interior_category_data[category]
        else:
            flash('Category not found. Please select a valid category.', 'error')
    else:
        for category_images in interior_category_data.values():
            images.extend(category_images)
    return render_template('wall.html', images=images)

@app.route('/floor', methods=['GET'])
def floor():
    tile_images = [
        'tileconcrete.jpeg', 'tilenaturalstone.jpeg', 'tilemosaic.jpeg', 
        'tileporcelain.jpeg', 'tileteracotta.jpeg', 'tilequarry.jpeg', 
        'tileZellige.jpeg', 'tilelimestone.jpeg', 'tileceramic.jpeg'
    ]
    return render_template('floor.html', images=tile_images)

@app.route('/window', methods=['GET'])
def window():
    window_images = [
        'windoriel.jpeg', 'windcottage.jpeg', 'windcasement.jpeg', 
        'windbay.jpeg', 'windbow.jpeg', 'windsinglehung.jpeg', 
        'winddoublehung.jpeg', 'windslide.jpeg', 'windslidethree.jpeg', 
        'windmetal.jpeg', 'windsash.jpeg'
    ]
    return render_template('window.html', images=window_images)
@app.route('/indoor', endpoint='indoor')
def indoor():
    return render_template('indoor.html')

@app.route('/outdoor', endpoint='outdoor')
def outdoor():
    return render_template('outdoor.html')

@app.route('/suggestions')
def suggestions():
    return render_template('suggestion.html')

@app.route('/furniture')
def furniture():
    return render_template('furniture.html')

@app.route('/paint', methods=['GET'])
def paint():
    return render_template('paint.html')

@app.route('/paint/types')
def paint_types():
    return render_template('painttypes.html')

@app.route('/paintcombos', methods=['GET', 'POST'])
def paint_combos():
    recommendations = []  # Initialize an empty list for recommendations
    if request.method == 'POST':
        color = request.form.get('color').strip().lower()
        if color in paints_category_data:
            recommendations = paints_category_data[color]
        else:
            flash('Color not found. Please enter a valid color.', 'error')
    return render_template('paintcombos.html', recommendations=recommendations)

@app.route('/plants')
def plants():
    return render_template('plants.html')
# Load color combinations data
with open('color_combinations.json', 'r') as f:
    color_combinations = json.load(f)

# Flatten the dataset for nearest neighbor search
colors = list(color_combinations.keys())
color_vectors = np.array([colors.index(color) for color in colors]).reshape(-1, 1)

# Train the NearestNeighbors model
model = NearestNeighbors(n_neighbors=3, algorithm='auto').fit(color_vectors)

with open('color_combinations.json') as f:
    color_combinations = json.load(f)

@app.route('/recommend_colors')
def recommend_colors():
    color = request.args.get('color', '').lower()
    recommendations = color_combinations.get(color, [])
    return jsonify({'recommendations': recommendations})

if __name__ == '__main__':
    app.run(debug=True)
