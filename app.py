from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import random
import json
import time

app = Flask(__name__)

# Set up the database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///color_game_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Create a UserData model
class UserData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    surname = db.Column(db.String(50))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    level = db.Column(db.Integer)
    time_spent = db.Column(db.Float)
    answer = db.Column(db.String(200))
    color_matrix = db.Column(db.Text)


# Function to generate colors that are very similar to a base color
def generate_similar_pixels(base_pixel, num_pixels=9, variation=1):
    return [
        "#%02x%02x%02x" % tuple(
            max(0, min(255, base_pixel[i] + random.randint(-variation, variation)))
            for i in range(3)
        )
        for _ in range(num_pixels)
    ]


# Route for the homepage
@app.route('/')
def home():
    return render_template('index.html')


# Route for starting the game level
@app.route('/start_level', methods=['POST'])
def start_level():
    global color_matrix
    data = request.get_json()
    level = data.get('level', 1)

    # Generate a new base color and create similar pixels
    random_pixel = tuple(random.randint(0, 255) for _ in range(3))
    similar_pixels = generate_similar_pixels(random_pixel, num_pixels=25, variation=3)

    # Create the color matrix for the current level
    color_matrix = [similar_pixels[i:i + 5] for i in range(0, 25, 5)]  # 5x5 grid

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
    answer = data['answer']
    color_matrix = json.dumps(data['color_matrix'])

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
        db.create_all()
    app.run(debug=True)
