from flask import Flask, request, jsonify
import mysql.connector
import pandas as pd
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

app = Flask(__name__)

# MySQL database connection details
host = "srv1814.hstgr.io"
user = "u352881525_mapt"
password = "Chathu6@ac"
database = "u352881525_mapt_web"

# Dummy data for the /get_data endpoint
dummy_data = [
    {"id": 1, "name": "Alice", "age": 25},
    {"id": 2, "name": "Bob", "age": 30},
    {"id": 3, "name": "Charlie", "age": 35}
]

# Endpoint to get dummy data
@app.route('/get_data', methods=['GET'])
def get_data():
    return jsonify(dummy_data)

# Function to get data from MySQL database
def get_destinations_from_db():
    try:
        # Connect to the database
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM destinations")
        rows = cursor.fetchall()
        
        columns = ['id', 'name', 'category', 'location', 'description', 'food_and_drink', 'culture_and_heritage', 
                   'nature_and_adventure', 'art_and_creativity', 'wellness_and_relaxation', 'sustainable_travel', 
                   'urban_exploration', 'community_and_social_experiences']
        
        destinations = pd.DataFrame(rows, columns=columns)
        
        cursor.close()
        connection.close()
        
        return destinations
    except mysql.connector.Error as err:
        return jsonify({"error": f"Database connection failed: {err}"}), 500

# Function to calculate match percentage using SVM
def calculate_match_percentage(user_preferences, destinations):
    features = ['food_and_drink', 'culture_and_heritage', 'nature_and_adventure', 
                'art_and_creativity', 'wellness_and_relaxation', 'sustainable_travel', 
                'urban_exploration', 'community_and_social_experiences']
    
    X = destinations[features]
    match_scores = []

    for _, row in X.iterrows():
        differences = [abs(user_preferences[feature] - row[feature]) for feature in features]
        match_score = 10 - (sum(differences) / len(features))
        match_scores.append(match_score)

    y = match_scores
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    svm_model = SVR(kernel='linear')
    svm_model.fit(X_train_scaled, y_train)
    
    preferences = pd.DataFrame(user_preferences, index=[0])
    preferences_scaled = scaler.transform(preferences)
    predicted_match = svm_model.predict(preferences_scaled)
    
    predicted_match_percentage = predicted_match[0] * 10
    
    destinations['match_score'] = svm_model.predict(scaler.transform(destinations[features])) * 10
    recommendations = destinations[['name', 'match_score', 'category', 'location', 'description']]
    recommendations = recommendations.sort_values(by='match_score', ascending=False)
    
    recommendations = recommendations[recommendations['match_score'] > 65]
    
    return recommendations, predicted_match_percentage

# API endpoint to get recommendations based on user preferences
@app.route('/get_recommendations', methods=['GET'])
def get_recommendations():
    try:
        user_preferences = {
            'food_and_drink': int(request.args.get('food_and_drink')),
            'culture_and_heritage': int(request.args.get('culture_and_heritage')),
            'nature_and_adventure': int(request.args.get('nature_and_adventure')),
            'art_and_creativity': int(request.args.get('art_and_creativity')),
            'wellness_and_relaxation': int(request.args.get('wellness_and_relaxation')),
            'sustainable_travel': int(request.args.get('sustainable_travel')),
            'urban_exploration': int(request.args.get('urban_exploration')),
            'community_and_social_experiences': int(request.args.get('community_and_social_experiences'))
        }

        destinations = get_destinations_from_db()
        recommendations, predicted_match = calculate_match_percentage(user_preferences, destinations)
        
        recommendation_list = recommendations.to_dict(orient='records')
        
        return jsonify({
            'predicted_match_score': f"{predicted_match:.2f}%",
            'recommendations': recommendation_list
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Hello World function for testing
@app.route('/hello', methods=['GET'])
def hello_world():
    return jsonify({"message": "Hello, World!"})

if __name__ == "__main__":
    app.run(debug=True)
