from flask import Flask, request, jsonify
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

app = Flask(__name__)

# Function to initialize Gemini model, ensuring API key is checked per request or on demand
def get_gemini_model():
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")
    genai.configure(api_key=api_key)
    # It's good practice to re-create the model object if settings could change,
    # or ensure it's created after configuration.
    model = genai.GenerativeModel('gemini-pro')
    return model

@app.route('/api/optimize-title', methods=['POST'])
def optimize_title():
    data = request.get_json()
    title = data.get('title')
    if not title:
        return jsonify({'error': 'Title is required'}), 400

    try:
        model = get_gemini_model() # Get model on demand
        prompt = f"Optimize the following YouTube video title: {title}"
        response = model.generate_content(prompt)
        # Ensure response.text exists, common for Gemini API
        suggestions = response.text if hasattr(response, 'text') else "No suggestion text available."
        return jsonify({'suggestions': suggestions})
    except ValueError as ve: # Catch specific API key error
        # Log the error for server-side visibility
        app.logger.error(f"Configuration error: {str(ve)}")
        return jsonify({'error': str(ve)}), 500
    except Exception as e:
        # Log the error for server-side visibility
        app.logger.error(f"Error calling Gemini API: {str(e)}")
        return jsonify({'error': f'Error calling Gemini API: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
