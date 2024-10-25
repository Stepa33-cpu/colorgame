import tkinter as tk
import random
import sqlite3
import time
import json
from tkinter import simpledialog  # Import simpledialog for user input

# Function to generate colors that are very similar to a base color
def generate_similar_pixels(base_pixel, num_pixels=9, variation=1):
    return [
        "#%02x%02x%02x" % tuple(
            max(0, min(255, base_pixel[i] + random.randint(-variation, variation)))
            for i in range(3)
        )
        for _ in range(num_pixels)
    ]

# Initialize the game window
root = tk.Tk()
root.title("Color Game")
root.attributes('-fullscreen', True)  # Set the window to fullscreen

# Database setup
conn = sqlite3.connect('color_game_data.db')
c = conn.cursor()

# Create a table to store user data
c.execute('''
    CREATE TABLE IF NOT EXISTS UserData (
        id INTEGER PRIMARY KEY,
        name TEXT,
        surname TEXT,
        age INTEGER,
        gender TEXT,
        level INTEGER,
        time_spent REAL,
        answer TEXT,
        color_matrix TEXT  -- New column to store color matrix
    )
''')
conn.commit()

# User Information
user_info = {}
def get_user_info():
    def save_info():
        user_info['name'] = name_entry.get()
        user_info['surname'] = surname_entry.get()
        user_info['age'] = age_entry.get()
        user_info['gender'] = gender_var.get()
        user_info_window.destroy()
        start_level()

    user_info_window = tk.Toplevel(root)
    user_info_window.title("User Information")

    tk.Label(user_info_window, text="Name:").grid(row=0, column=0)
    name_entry = tk.Entry(user_info_window)
    name_entry.grid(row=0, column=1)

    tk.Label(user_info_window, text="Surname:").grid(row=1, column=0)
    surname_entry = tk.Entry(user_info_window)
    surname_entry.grid(row=1, column=1)

    tk.Label(user_info_window, text="Age:").grid(row=2, column=0)
    age_entry = tk.Entry(user_info_window)
    age_entry.grid(row=2, column=1)

    tk.Label(user_info_window, text="Gender:").grid(row=3, column=0)
    gender_var = tk.StringVar(value="Male")
    tk.Radiobutton(user_info_window, text="Male", variable=gender_var, value="Male").grid(row=3, column=1)
    tk.Radiobutton(user_info_window, text="Female", variable=gender_var, value="Female").grid(row=3, column=2)

    tk.Button(user_info_window, text="Save", command=save_info).grid(row=4, columnspan=3)

# Initialize game variables
level = 1  # Start at level 1
selected_buttons = []  # Track selected buttons
user_sees_same_color = False  # Track if the user sees all colors as the same
start_time = 0  # Track start time for the level
color_matrix = []  # Initialize color matrix

# Function to start a new level
def start_level():
    global level, similar_pixels, index, user_sees_same_color, start_time, color_matrix

    # Clear existing widgets
    for widget in root.winfo_children():
        widget.destroy()

    # Display the current level with a larger font size
    level_label = tk.Label(root, text=f"Level {level}", font=("Arial", 32))  # Increased font size
    level_label.grid(row=0, column=0, columnspan=4)

    # Generate a new base color and create similar pixels with smaller variation
    random_pixel = tuple(random.randint(0, 255) for _ in range(3))
    similar_pixels = generate_similar_pixels(random_pixel, num_pixels=25, variation=3)  # Reduced variation for more similar colors

    # Create the 5x5 grid of buttons with similar colors
    index = 0
    color_matrix = []  # Reset color matrix for the new level
    for row in range(1, 6):  # Grid starts from row 1 to leave space for level label
        row_colors = []  # Initialize a list for the current row's colors
        for col in range(5):
            color = similar_pixels[index]
            row_colors.append(color)  # Append the color to the row list
            index += 1
            # Create a button with a similar color and larger size
            btn = tk.Button(root, bg=color, width=12, height=6, borderwidth=0)  # No border
            btn.config(command=lambda b=btn: toggle_selection(b, color))  # Pass original color
            btn.grid(row=row, column=col, padx=0, pady=0)  # No padding between buttons
        color_matrix.append(row_colors)  # Append the row to the color matrix

    # Create "All the Same Color" button with larger size
    same_color_button = tk.Button(root, text="All the Same Color", command=set_same_color, font=("Arial", 16), width=20, height=3)
    same_color_button.grid(row=11, column=0, columnspan=5, pady=10)

    # Create a "Color Groups" button for user input
    color_groups_button = tk.Button(root, text="Enter Color Groups", command=enter_color_groups, font=("Arial", 16), width=20, height=3)
    color_groups_button.grid(row=12, column=0, columnspan=5, pady=10)

    # Create a "Next" button for submitting the answer
    next_button = tk.Button(root, text="Next", command=submit_answer, font=("Arial", 16), width=20, height=3)
    next_button.grid(row=13, column=0, columnspan=5, pady=10)

    start_time = time.time()  # Record the start time for this level

# Function to toggle selection of a button
def toggle_selection(btn, original_color):
    if btn in selected_buttons:
        selected_buttons.remove(btn)
        btn.config(bg=original_color)  # Reset the background to the original color
    else:
        selected_buttons.append(btn)
        # Set a semi-transparent overlay color to indicate selection
        btn.config(bg="lightgray")  # Use a lighter color for the overlay

# Function to set all buttons to the same color and record user response
def set_same_color():
    global user_sees_same_color
    user_sees_same_color = True  # Mark that the user sees all colors as the same
    if similar_pixels:
        same_color = random.choice(similar_pixels)
        for btn in root.winfo_children():
            if isinstance(btn, tk.Button):
                btn.config(bg=same_color)

# Function to enter the number of color groups
def enter_color_groups():
    user_input = simpledialog.askinteger("Color Groups", "How many color groups do you see?", minvalue=1)
    if user_input is not None:  # Proceed if user entered a value
        answer = f"Color Groups: {user_input}, Selected Colors: {[btn.cget('bg') for btn in selected_buttons]}"
        next_level(answer)  # Advance to the next level with the answer

# Function to submit the answer and advance to next level
def submit_answer():
    answer = f"Selected Colors: {[btn.cget('bg') for btn in selected_buttons]}"
    next_level(answer)  # Advance to the next level with the answer

# Function to advance to the next level
def next_level(answer=None):
    global level, user_sees_same_color, start_time, color_matrix

    time_spent = time.time() - start_time  # Calculate time spent on this level
    user_answer = "All the Same Colors" if user_sees_same_color else answer

    # Serialize the color matrix as a JSON string
    color_matrix_str = json.dumps(color_matrix)

    # Save user data to the database
    c.execute('''
        INSERT INTO UserData (name, surname, age, gender, level, time_spent, answer, color_matrix)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_info['name'], user_info['surname'], user_info['age'], user_info['gender'], level, time_spent, user_answer, color_matrix_str))
    conn.commit()

    # Print for debugging; can remove in production
    print(f"Level: {level}, Time Spent: {time_spent:.2f}s, Answer: {user_answer}, Color Matrix: {color_matrix_str}")

    # Check if the level is less than or equal to 10
    if level < 10:
        level += 1
        selected_buttons.clear()  # Clear selected buttons for the next level
        user_sees_same_color = False  # Reset the user response for the next level
        start_level()
    else:
        end_game()  # Call end game function

# Function to display the end game message
def end_game():
    for widget in root.winfo_children():
        widget.destroy()

    completion_label = tk.Label(root, text="Congratulations! You've completed all levels!", font=("Arial", 32))
    completion_label.pack(pady=50)

    restart_button = tk.Button(root, text="Restart Game", command=restart_game, font=("Arial", 16), width=20, height=3)
    restart_button.pack(pady=10)

    exit_button = tk.Button(root, text="Exit", command=root.quit, font=("Arial", 16), width=20, height=3)
    exit_button.pack(pady=10)

# Function to restart the game
def restart_game():
    global level
    level = 1  # Reset level to 1
    start_level()  # Restart the game

# Prompt for user information
get_user_info()

# Start the Tkinter event loop
root.mainloop()

# Close the database connection when done
conn.close()
