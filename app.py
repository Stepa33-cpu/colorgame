from flask import Flask, request, jsonify, render_template
import random
import json
import os

app = Flask(__name__)

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

# Route to submit user answers (no database interaction)
@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    data = request.get_json()
    user_info = data['user_info']
    level = data['level']
    time_spent = data['time_spent']
    answer = data.get('answer', "")
    color_matrix = json.dumps(data['color_matrix'])  # Store matrix as JSON string

    # Here you can print the data to the console instead of saving it to a database
    print("User Info:", user_info)
    print("Level:", level)
    print("Time Spent:", time_spent)
    print("Answer:", answer)
    print("Color Matrix:", color_matrix)

    return jsonify({"message": "Answer submitted successfully"})

if __name__ == '__main__':
    # Get the port from the environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
