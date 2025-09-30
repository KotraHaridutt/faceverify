import React, { useState } from 'react';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// ImageUploader Component
const ImageUploader = ({ onImageUpload, imagePreviewUrl, facialArea, label }) => {
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      // Validate file type
      const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png'];
      if (!allowedTypes.includes(file.type)) {
        alert('Please upload only JPEG or PNG images');
        return;
      }
      
      // Validate file size (5MB)
      const maxSize = 5 * 1024 * 1024;
      if (file.size > maxSize) {
        alert('File size must be less than 5MB');
        return;
      }
      
      const reader = new FileReader();
      reader.onload = (e) => {
        onImageUpload(file, e.target.result);
      };
      reader.readAsDataURL(file);
    }
  };

  return (
    <div className="flex flex-col items-center space-y-4">
      <h3 className="text-lg font-semibold text-gray-700">{label}</h3>
      <div className="relative">
        <input
          type="file"
          accept="image/jpeg,image/jpg,image/png"
          onChange={handleFileChange}
          className="hidden"
          id={`image-upload-${label}`}
        />
        <label
          htmlFor={`image-upload-${label}`}
          className="cursor-pointer block"
        >
          {imagePreviewUrl ? (
            <div className="relative">
              <img
                src={imagePreviewUrl}
                alt="Preview"
                className="w-64 h-64 object-cover rounded-lg border-2 border-gray-300 hover:border-blue-500 transition-colors"
              />
              {facialArea && (
                <div
                  className="absolute border-2 border-red-500 bg-red-100 bg-opacity-30"
                  style={{
                    left: `${facialArea.x}px`,
                    top: `${facialArea.y}px`,
                    width: `${facialArea.w}px`,
                    height: `${facialArea.h}px`,
                  }}
                >
                  <div className="absolute -top-6 left-0 bg-red-500 text-white text-xs px-2 py-1 rounded">
                    Face
                  </div>
                </div>
              )}
              <div className="absolute inset-0 bg-black bg-opacity-0 hover:bg-opacity-10 transition-all rounded-lg flex items-center justify-center">
                <span className="text-white opacity-0 hover:opacity-100 transition-opacity font-medium">
                  Click to change
                </span>
              </div>
            </div>
          ) : (
            <div className="w-64 h-64 border-2 border-dashed border-gray-300 rounded-lg flex flex-col items-center justify-center hover:border-blue-500 hover:bg-blue-50 transition-colors">
              <svg className="w-12 h-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              <p className="text-gray-500 text-center">
                <span className="font-medium">Click to upload</span>
                <br />
                <span className="text-sm">PNG, JPG up to 5MB</span>
              </p>
            </div>
          )}
        </label>
      </div>
    </div>
  );
};

// ResultsDisplay Component
const ResultsDisplay = ({ result, isLoading, error }) => {
  if (isLoading) {
    return (
      <div className="flex flex-col items-center space-y-4 p-6 bg-blue-50 rounded-lg">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <p className="text-blue-700 font-medium">Analyzing faces...</p>
        <p className="text-blue-600 text-sm">This may take a few moments</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-red-50 border border-red-200 rounded-lg">
        <div className="flex items-center space-x-3">
          <svg className="w-6 h-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
          <div>
            <h3 className="text-red-800 font-semibold">Error</h3>
            <p className="text-red-700">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (result) {
    const getScoreColor = (percentage) => {
      if (percentage >= 75) return 'text-green-600 bg-green-50 border-green-200';
      if (percentage >= 40) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      return 'text-red-600 bg-red-50 border-red-200';
    };

    const getScoreIcon = (percentage) => {
      if (percentage >= 75) {
        return (
          <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
      }
      if (percentage >= 40) {
        return (
          <svg className="w-8 h-8 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        );
      }
      return (
        <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      );
    };

    return (
      <div className={`p-6 border rounded-lg ${getScoreColor(result.match_percentage)}`}>
        <div className="flex items-center justify-center space-x-4 mb-4">
          {getScoreIcon(result.match_percentage)}
          <div className="text-center">
            <h3 className="text-2xl font-bold">Match Score</h3>
            <p className="text-4xl font-bold">{result.match_percentage}%</p>
          </div>
        </div>
        
        <div className="text-center space-y-2">
          <p className="font-medium">
            {result.verified ? 'Faces Match!' : 'Faces Do Not Match'}
          </p>
          <p className="text-sm opacity-75">
            Analyzed using: {result.model_used}
          </p>
        </div>
        
        {result.match_percentage >= 75 && (
          <div className="mt-4 p-3 bg-green-100 rounded-lg">
            <p className="text-green-800 text-sm text-center font-medium">
              High confidence match - These faces likely belong to the same person
            </p>
          </div>
        )}
        
        {result.match_percentage < 40 && (
          <div className="mt-4 p-3 bg-red-100 rounded-lg">
            <p className="text-red-800 text-sm text-center font-medium">
              Low confidence - These faces likely belong to different people
            </p>
          </div>
        )}
        
        {result.match_percentage >= 40 && result.match_percentage < 75 && (
          <div className="mt-4 p-3 bg-yellow-100 rounded-lg">
            <p className="text-yellow-800 text-sm text-center font-medium">
              Moderate confidence - Results may vary
            </p>
          </div>
        )}
      </div>
    );
  }

  return null;
};

// Main App Component
function App() {
  const [image1, setImage1] = useState(null);
  const [image2, setImage2] = useState(null);
  const [imagePreview1, setImagePreview1] = useState(null);
  const [imagePreview2, setImagePreview2] = useState(null);
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleImage1Upload = (file, previewUrl) => {
    setImage1(file);
    setImagePreview1(previewUrl);
    // Clear previous results
    setResult(null);
    setError(null);
  };

  const handleImage2Upload = (file, previewUrl) => {
    setImage2(file);
    setImagePreview2(previewUrl);
    // Clear previous results
    setResult(null);
    setError(null);
  };

  const handleCompare = async () => {
    if (!image1 || !image2) {
      setError('Please upload both images before comparing');
      return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('image1', image1);
      formData.append('image2', image2);

      const response = await fetch(`${API}/verify`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Face verification failed');
      }

      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setImage1(null);
    setImage2(null);
    setImagePreview1(null);
    setImagePreview2(null);
    setResult(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">
            FaceVerify AI
          </h1>
          <p className="text-xl text-gray-600 mb-2">
            Are they the same person?
          </p>
          <p className="text-gray-500">
            Upload two images and our AI will analyze if the faces belong to the same person
          </p>
        </div>

        {/* Upload Section */}
        <div className="grid md:grid-cols-2 gap-8 mb-8">
          <ImageUploader
            onImageUpload={handleImage1Upload}
            imagePreviewUrl={imagePreview1}
            facialArea={result?.facial_areas?.img1}
            label="First Image"
          />
          <ImageUploader
            onImageUpload={handleImage2Upload}
            imagePreviewUrl={imagePreview2}
            facialArea={result?.facial_areas?.img2}
            label="Second Image"
          />
        </div>

        {/* Action Buttons */}
        <div className="flex justify-center space-x-4 mb-8">
          <button
            onClick={handleCompare}
            disabled={!image1 || !image2 || isLoading}
            className="px-8 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
          >
            {isLoading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                <span>Analyzing...</span>
              </>
            ) : (
              <>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                <span>Compare Faces</span>
              </>
            )}
          </button>
          
          <button
            onClick={handleReset}
            className="px-8 py-3 bg-gray-500 text-white font-semibold rounded-lg hover:bg-gray-600 transition-colors flex items-center space-x-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <span>Reset</span>
          </button>
        </div>

        {/* Results Section */}
        <div className="max-w-2xl mx-auto">
          <ResultsDisplay
            result={result}
            isLoading={isLoading}
            error={error}
          />
        </div>

        {/* Footer */}
        <div className="text-center mt-12 text-gray-500">
          <p className="text-sm">
            Powered by DeepFace ArcFace model for high-accuracy facial recognition
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;
