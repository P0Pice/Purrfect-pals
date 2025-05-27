import pytest
import os
import json
from unittest.mock import patch, MagicMock

# Import the Flask app instance.
# This needs to be done carefully to allow monkeypatching environment variables *before* the app and its configurations are fully loaded.
# We will import it within fixtures or tests where os.environ is appropriately patched.

@pytest.fixture
def app_instance():
    # Ensure app is imported after environment variables are potentially patched by tests
    from backend.app import app
    app.config.update({
        "TESTING": True,
    })
    return app

@pytest.fixture
def client(app_instance):
    return app_instance.test_client()

@pytest.fixture(autouse=True)
def manage_gemini_api_key(monkeypatch):
    """Ensure GEMINI_API_KEY is set for most tests, can be overridden."""
    monkeypatch.setenv('GEMINI_API_KEY', 'test_api_key')

def test_optimize_title_success(client, mocker):
    """Test successful API call to /api/optimize-title."""
    # Mock the get_gemini_model function to control model behavior
    mock_model_instance = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Suggested Title 1\nSuggested Title 2"
    mock_model_instance.generate_content.return_value = mock_response
    
    # Patch the get_gemini_model within the app module
    mocker.patch('backend.app.get_gemini_model', return_value=mock_model_instance)

    response = client.post('/api/optimize-title', json={'title': 'Original Title'})
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'suggestions' in data
    assert data['suggestions'] == "Suggested Title 1\nSuggested Title 2"
    mock_model_instance.generate_content.assert_called_once_with("Optimize the following YouTube video title: Original Title")

def test_optimize_title_gemini_api_error(client, mocker):
    """Test API call when Gemini API throws an error."""
    mock_model_instance = MagicMock()
    mock_model_instance.generate_content.side_effect = Exception("Gemini Internal Error")
    
    mocker.patch('backend.app.get_gemini_model', return_value=mock_model_instance)

    response = client.post('/api/optimize-title', json={'title': 'Another Title'})
    
    assert response.status_code == 500
    data = json.loads(response.data)
    assert 'error' in data
    assert 'Error calling Gemini API: Gemini Internal Error' in data['error']

def test_optimize_title_missing_title(client):
    """Test API call when 'title' is missing from the request."""
    response = client.post('/api/optimize-title', json={})
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Title is required'

def test_optimize_title_missing_gemini_api_key(client, monkeypatch, mocker):
    """Test API call when GEMINI_API_KEY is not set."""
    # Unset the API key for this specific test
    monkeypatch.delenv('GEMINI_API_KEY', raising=False)

    # Since get_gemini_model now raises ValueError if key is missing,
    # we don't need to mock genai.GenerativeModel itself for this test.
    # The error should be caught by the try-except block calling get_gemini_model.
    
    # We need to ensure that app.get_gemini_model is the one from the app instance being tested.
    # No, get_gemini_model is a global function in backend.app, so patching os.environ is enough.
    # The app will call it, and it will try to read the (now missing) env var.

    response = client.post('/api/optimize-title', json={'title': 'Title With Missing Key'})
    
    assert response.status_code == 500
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'GEMINI_API_KEY environment variable not set.'

def test_optimize_title_gemini_no_text_in_response(client, mocker):
    """Test successful API call but Gemini response has no text attribute."""
    mock_model_instance = MagicMock()
    # Simulate a response object that does not have a 'text' attribute
    mock_response = MagicMock(spec=[]) # spec=[] means it has no attributes unless added
    mock_model_instance.generate_content.return_value = mock_response
    
    mocker.patch('backend.app.get_gemini_model', return_value=mock_model_instance)

    response = client.post('/api/optimize-title', json={'title': 'Title leading to no text'})
    
    assert response.status_code == 200 # The API call itself is successful
    data = json.loads(response.data)
    assert 'suggestions' in data
    assert data['suggestions'] == "No suggestion text available."
    mock_model_instance.generate_content.assert_called_once_with("Optimize the following YouTube video title: Title leading to no text")
