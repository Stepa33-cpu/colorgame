from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import random
import json
import os

app = Flask(__name__)

# Database configuration
# Use external URL for production and internal for local development
if os.environ.get('FLASK_ENV') == 'production':
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://bazadate_user:oLJzh7gdA2B6K0gB3iaHPUulQiwbDXaF@dpg-csea36m8ii6s738vfh1g-a.frankfurt-postgres.render.com/bazadate'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://bazadate_user:oLJzh7gdA2B6K0gB3iaHPUulQiwbDXaF@dpg-csea36m8ii6s738vfh1g-a/bazadate'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Import UserData model
from models import UserData

# Function to generate similar colors based on a base RGB color
def generate_similar_pixels(base_pixel, num_pixels=9, variation=1):
    return [
        "#%02x%02x%02x" % tuple(
            max(0, min(255, base_pixel[i] + random.randint(-variation, variation)))
            for i in range(3)
        )
        for _ in range(num_pixels)
    ]

# Homepage route
@app.route('/')
def home():
    return render_template('index.html')

# Route for starting the game level
@app.route('/start_level', methods=['POST'])
def start_level():
    data = request.get_json()
    level = data.get('level', 1)
    random_pixel = tuple(random.randint(0, 255) for _ in range(3))
    similar_pixels = generate_similar_pixels(random_pixel, num_pixels=25, variation=3)
    color_matrix = [similar_pixels[i:i + 5] for i in range(0, 25, 5)]
    return jsonify({
        "message": "Level started",
        "color_matrix": color_matrix
    })

# Route to submit user answers and save to the database
@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    data = request.get_json()
    user_info = data['user_info']
    level = data['level']
    time_spent = data['time_spent']
    answer = data.get('answer', "")
    color_matrix = json.dumps(data['color_matrix'])  # Store matrix as JSON string

    # Save data into the database
    new_entry = UserData(
        name=user_info['name'],
        surname=user_info['surname'],
        age=user_info['age'],
        gender=user_info['gender'],
        level=level,
        time_spent=time_spent,
        answer=answer,
        color_matrix=color_matrix
    )

    db.session.add(new_entry)
    db.session.commit()

    return jsonify({"message": "Answer submitted successfully"})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables if they don't exist

    # Get the port from the environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
