import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from api.main import app  # Assuming your FastAPI app is in 'main.py' inside the 'api' folder

# Create a TestClient instance for the FastAPI app
client = TestClient(app)

# Mocking external dependencies (like load_config, PyPDFLoader, FAISS, and Watsonx)
@pytest.fixture
def mock_load_config():
    with patch('api.main.load_config') as mock:
        mock.return_value = {
            'watsonx': {
                'region': 'us-south',
                'api_key': 'dummy-api-key',
                'project_id': 'dummy-project-id',
                'model_id': 'dummy-model-id'
            }
        }
        yield mock

@pytest.fixture
def mock_pypdf_loader():
    with patch('api.main.PyPDFLoader') as mock:
        mock_instance = MagicMock()
        mock_instance.load_and_split.return_value = [
            {'page': 1, 'content': 'Sample content from PDF document.'}
        ]
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_faiss_creation():
    with patch('api.main.FAISS.from_documents') as mock:
        mock.return_value = MagicMock()
        yield mock

@pytest.fixture
def mock_trained_chain():
    with patch('api.main.ConversationalRetrievalChain') as mock:
        mock_instance = MagicMock()
        mock.return_value = mock_instance
        yield mock_instance

# Test case for successful document upload and model training
def test_upload_documents_success(mock_load_config, mock_pypdf_loader, mock_faiss_creation, mock_trained_chain):
    # Sample PDF file content to simulate file upload
    pdf_file = ("test.pdf", b"%PDF-1.4 test content", "application/pdf")
    
    # Send a POST request to the /upload-documents endpoint with a mock PDF file
    response = client.post(
        "/upload-documents", 
        files={"files": pdf_file}
    )

    # Assert that the response status code is 200 and the response content is as expected
    assert response.status_code == 200
    assert response.json() == {"status": "Success", "message": "Conversational model trained successfully."}

    # Ensure that the mocked methods were called as expected
    mock_pypdf_loader.load_and_split.assert_called_once()
    mock_faiss_creation.assert_called_once()
    mock_trained_chain.assert_called_once()

# Test case for no files uploaded (Bad Request)
def test_upload_documents_no_files(mock_load_config):
    response = client.post("/upload-documents")
    
    # Assert that the response is a Bad Request (400) with the appropriate message
    assert response.status_code == 400
    assert response.json() == {"detail": "No files uploaded."}

# Test case for invalid file type (non-PDF)
def test_upload_documents_invalid_file(mock_load_config):
    # Simulate uploading a non-PDF file (e.g., a text file)
    invalid_file = ("test.txt", b"Not a PDF file.", "text/plain")
    
    response = client.post(
        "/upload-documents", 
        files={"files": invalid_file}
    )
    
    # Assert that the response status code is 200 (the PDF was skipped without failure)
    assert response.status_code == 200
    assert response.json() == {"status": "Success", "message": "Conversational model trained successfully."}

# Test case for failed PDF text extraction
def test_upload_documents_pdf_extraction_failure(mock_load_config, mock_pypdf_loader):
    # Make PyPDFLoader raise an error to simulate failure
    mock_pypdf_loader.load_and_split.side_effect = Exception("Failed to read PDF content")
    
    pdf_file = ("test.pdf", b"%PDF-1.4 test content", "application/pdf")
    
    response = client.post(
        "/upload-documents", 
        files={"files": pdf_file}
    )
    
    # Assert that the response status code is 500 (internal server error)
    assert response.status_code == 500
    assert "Failed to process test.pdf" in response.json()["detail"]

# Test case for no content extracted from PDFs
def test_upload_documents_no_valid_content(mock_load_config, mock_pypdf_loader):
    # Simulate PyPDFLoader not extracting any valid content from the PDFs
    mock_pypdf_loader.load_and_split.return_value = []
    
    pdf_file = ("test.pdf", b"%PDF-1.4 test content", "application/pdf")
    
    response = client.post(
        "/upload-documents", 
        files={"files": pdf_file}
    )
    
    # Assert that the response status code is 400 (Bad Request)
    assert response.status_code == 400
    assert response.json() == {"detail": "No valid content extracted from uploaded files."}
