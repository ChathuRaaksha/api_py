from flask import Flask, jsonify

app = Flask(__name__)

# Dummy data
dummy_data = [
    {"id": 1, "name": "Alice", "age": 25},
    {"id": 2, "name": "Bob", "age": 30},
    {"id": 3, "name": "Charlie", "age": 35}
]

# Define a simple GET route
@app.route('/get_data', methods=['GET'])
def get_data():
    return jsonify(dummy_data)

# Test route
@app.route('/hello', methods=['GET'])
def hello_world():
    return jsonify({"message": "Hello, World!"})

if __name__ == "__main__":
    app.run(debug=True)
