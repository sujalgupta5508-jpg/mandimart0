#!/usr/bin/env python3
# ============================================
# MANDIMART AI VEGETABLE COMPARISON API
# Flask Backend for Comparing Two Vegetable Images
# Endpoint: POST /api/compare-vegetables
# ============================================

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from PIL import Image
import numpy as np
import cv2
import os
import io
import base64
import uuid
import json
from datetime import datetime
import compare_engine  # Our comparison logic module



# Flask App Configuration
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin for PHP frontend

# Upload Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ============================================
# HELPER FUNCTIONS
# ============================================

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_base64_image(base64_string, filename):
    """Convert base64 string to image file and save"""
    try:
        # Remove data URI prefix if present
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        image_data = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary
        if image.mode in ('RGBA', 'P'):
            image = image.convert('RGB')
        
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        image.save(filepath, 'JPEG', quality=95)
        return filepath
    except Exception as e:
        return None


def analyze_image(filepath):
    """
    Analyze a single vegetable image using OpenCV
    Returns freshness score and attributes
    """
    try:
        # Read image with OpenCV
        img = cv2.imread(filepath)
        if img is None:
            return None
        
        # Convert to RGB for analysis
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Run analysis engine
        result = compare_engine.analyze_vegetable(img_rgb)
        return result
        
    except Exception as e:
        print(f"Analysis error: {str(e)}")
        return None


# ============================================
# API ROUTES
# ============================================

@app.route('/')
def home():
    """API Home - Health Check"""
    return jsonify({
        "status": "online",
        "service": "MandiMart AI Vegetable Comparison API",
        "version": "1.0.0",
        "endpoints": {
            "compare": "POST /api/compare-vegetables",
            "analyze": "POST /api/analyze-single",
            "health": "GET /health"
        },
        "timestamp": datetime.now().isoformat()
    })


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/analyze-single', methods=['POST'])
def analyze_single():
    """
    Analyze a single vegetable image
    Form Data: image (file)
    Returns: freshness analysis
    """
    try:
        # Check if image was uploaded
        if 'image' not in request.files:
            return jsonify({
                "success": False,
                "message": "No image file provided"
            }), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({
                "success": False,
                "message": "Empty filename"
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                "success": False,
                "message": f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            }), 400
        
        # Save uploaded file
        unique_name = f"single_{uuid.uuid4().hex[:8]}.jpg"
        filepath = os.path.join(UPLOAD_FOLDER, secure_filename(unique_name))
        file.save(filepath)
        
        # Analyze image
        result = analyze_image(filepath)
        
        # Clean up
        if os.path.exists(filepath):
            os.remove(filepath)
        
        if result is None:
            return jsonify({
                "success": False,
                "message": "Failed to analyze image"
            }), 500
        
        return jsonify({
            "success": True,
            "data": result
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500


@app.route('/api/compare-vegetables', methods=['POST'])
def compare_vegetables():
    """
    Compare TWO vegetable images and determine which is better
    
    Expected Form Data:
        - image1: First vegetable image file
        - image2: Second vegetable image file
        OR
        - image1_base64: Base64 encoded first image
        - image2_base64: Base64 encoded second image
    
    Returns:
        - Individual scores for both vegetables
        - Winner recommendation
        - Detailed analysis
    """
    try:
        print("=" * 50)
        print("VEGETABLE COMPARISON REQUEST RECEIVED")
        print("=" * 50)
        
        # Track temporary files for cleanup
        temp_files = []
        
        # ========================================
        # GET IMAGE 1
        # ========================================
        filepath1 = None
        
        if 'image1' in request.files:
            # File upload
            file1 = request.files['image1']
            if file1.filename != '' and allowed_file(file1.filename):
                unique_name1 = f"veg1_{uuid.uuid4().hex[:8]}.jpg"
                filepath1 = os.path.join(UPLOAD_FOLDER, secure_filename(unique_name1))
                file1.save(filepath1)
                temp_files.append(filepath1)
                print(f"Image 1 saved: {filepath1}")
                
        elif 'image1_base64' in request.form:
            # Base64 upload
            base64_1 = request.form['image1_base64']
            unique_name1 = f"veg1_{uuid.uuid4().hex[:8]}.jpg"
            filepath1 = save_base64_image(base64_1, unique_name1)
            if filepath1:
                temp_files.append(filepath1)
                print(f"Image 1 (base64) saved: {filepath1}")
        
        # ========================================
        # GET IMAGE 2
        # ========================================
        filepath2 = None
        
        if 'image2' in request.files:
            file2 = request.files['image2']
            if file2.filename != '' and allowed_file(file2.filename):
                unique_name2 = f"veg2_{uuid.uuid4().hex[:8]}.jpg"
                filepath2 = os.path.join(UPLOAD_FOLDER, secure_filename(unique_name2))
                file2.save(filepath2)
                temp_files.append(filepath2)
                print(f"Image 2 saved: {filepath2}")
                
        elif 'image2_base64' in request.form:
            base64_2 = request.form['image2_base64']
            unique_name2 = f"veg2_{uuid.uuid4().hex[:8]}.jpg"
            filepath2 = save_base64_image(base64_2, unique_name2)
            if filepath2:
                temp_files.append(filepath2)
                print(f"Image 2 (base64) saved: {filepath2}")
        
        # Validate both images received
        if not filepath1 or not filepath2:
            # Clean up any saved files
            for f in temp_files:
                if os.path.exists(f):
                    os.remove(f)
            
            missing = []
            if not filepath1:
                missing.append("image1")
            if not filepath2:
                missing.append("image2")
            
            return jsonify({
                "success": False,
                "message": f"Missing images: {', '.join(missing)}. Provide as file upload or base64."
            }), 400
        
        # ========================================
        # ANALYZE BOTH IMAGES
        # ========================================
        print("\nAnalyzing Image 1...")
        result1 = analyze_image(filepath1)
        
        print("Analyzing Image 2...")
        result2 = analyze_image(filepath2)
        
        if result1 is None or result2 is None:
            for f in temp_files:
                if os.path.exists(f):
                    os.remove(f)
            return jsonify({
                "success": False,
                "message": "Failed to analyze one or both images"
            }), 500
        
        # ========================================
        # COMPARE AND DETERMINE WINNER
        # ========================================
        comparison = compare_engine.compare_two_vegetables(result1, result2)
        
        # ========================================
        # BUILD RESPONSE
        # ========================================
        response = {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "comparison": {
                "vegetable_1": {
                    "name": "Vegetable 1",
                    "image_path": filepath1,
                    "freshness_score": result1["freshness_score"],
                    "quality_grade": result1["quality_grade"],
                    "color_score": result1["color_score"],
                    "texture_score": result1["texture_score"],
                    "defect_score": result1["defect_score"],
                    "size_score": result1["size_score"],
                    "overall_score": result1["overall_score"],
                    "details": result1
                },
                "vegetable_2": {
                    "name": "Vegetable 2",
                    "image_path": filepath2,
                    "freshness_score": result2["freshness_score"],
                    "quality_grade": result2["quality_grade"],
                    "color_score": result2["color_score"],
                    "texture_score": result2["texture_score"],
                    "defect_score": result2["defect_score"],
                    "size_score": result2["size_score"],
                    "overall_score": result2["overall_score"],
                    "details": result2
                },
                "winner": comparison["winner"],
                "winner_name": comparison["winner_name"],
                "margin": comparison["margin"],
                "recommendation": comparison["recommendation"],
                "market_value": comparison["market_value"]
            },
            "analysis_summary": comparison["summary"]
        }
        
        print(f"\nWinner: {comparison['winner_name']}")
        print(f"Margin: {comparison['margin']}%")
        
        # ========================================
        # CLEAN UP TEMP FILES
        # ========================================
        for f in temp_files:
            if os.path.exists(f):
                os.remove(f)
                print(f"Cleaned up: {f}")
        
        return jsonify(response)
        
    except Exception as e:
        # Clean up on error
        for f in temp_files:
            if os.path.exists(f):
                os.remove(f)
        
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            "success": False,
            "message": f"Comparison failed: {str(e)}"
        }), 500


@app.route('/api/compare-vegetables-base64', methods=['POST'])
def compare_vegetables_base64():
    """
    Alternative endpoint that accepts JSON with base64 images
    JSON Body:
    {
        "image1_base64": "data:image/jpeg;base64,/9j/4AAQ...",
        "image2_base64": "data:image/jpeg;base64,/9j/4AAQ..."
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'image1_base64' not in data or 'image2_base64' not in data:
            return jsonify({
                "success": False,
                "message": "JSON body must contain image1_base64 and image2_base64"
            }), 400
        
        # Process as form data internally
        request.form = data
        
        # Reuse main comparison logic
        return compare_vegetables()
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Base64 comparison failed: {str(e)}"
        }), 500


# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(413)
def too_large(e):
    return jsonify({
        "success": False,
        "message": "File too large. Maximum size is 16MB."
    }), 413


@app.errorhandler(500)
def server_error(e):
    return jsonify({
        "success": False,
        "message": "Internal server error"
    }), 500


# ============================================
# MAIN ENTRY POINT
# ============================================

if __name__ == '__main__':
    print("=" * 50)
    print("MANDIMART AI VEGETABLE COMPARISON API")
    print("Starting Flask server...")
    print("=" * 50)
    print(f"Upload folder: {os.path.abspath(UPLOAD_FOLDER)}")
    print(f"Max file size: {MAX_CONTENT_LENGTH / 1024 / 1024}MB")
    print("\nEndpoints:")
    print("  GET  /           - API info")
    print("  GET  /health     - Health check")
    print("  POST /api/analyze-single        - Analyze single image")
    print("  POST /api/compare-vegetables    - Compare two images (multipart/form-data)")
    print("  POST /api/compare-vegetables-base64 - Compare two images (JSON base64)")
    print("\nPress Ctrl+C to stop")
    print("=" * 50)
    
    # Run on port 5000 (or change as needed)
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )

from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import os

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "success": True,
        "message": "MandiMart AI API is running",
        "port": 5000
    })


@app.route("/compare", methods=["POST"])
def compare():

    if "image1" not in request.files or "image2" not in request.files:
        return jsonify({
            "success": False,
            "message": "Both images are required"
        }), 400

    image1 = request.files["image1"]
    image2 = request.files["image2"]

    try:

        # Open images
        img1 = Image.open(image1)
        img2 = Image.open(image2)

        print("Image 1:", img1.size)
        print("Image 2:", img2.size)

        # ==========================================
        # YOUR AI / OPENCV MODEL GOES HERE
        # ==========================================

        # Temporary test values
        vegetable_1 = {
            "freshness_score": 92,
            "color_score": 90,
            "texture_score": 88,
            "defect_score": 94,
            "size_score": 91,
            "overall_score": 91,
            "quality_grade": "A",
            "estimated_shelf_life_days": 7
        }

        vegetable_2 = {
            "freshness_score": 78,
            "color_score": 80,
            "texture_score": 75,
            "defect_score": 72,
            "size_score": 82,
            "overall_score": 77,
            "quality_grade": "B",
            "estimated_shelf_life_days": 4
        }

        score1 = vegetable_1["overall_score"]
        score2 = vegetable_2["overall_score"]

        if score1 >= score2:
            winner = 1
            winner_name = "Vegetable 1"
            margin = score1 - score2
        else:
            winner = 2
            winner_name = "Vegetable 2"
            margin = score2 - score1

        return jsonify({
            "success": True,

            "data": {
                "vegetable_1": vegetable_1,
                "vegetable_2": vegetable_2,

                "winner": winner,
                "winner_name": winner_name,
                "margin": margin,

                "recommendation":
                    f"{winner_name} is recommended because it has a higher overall quality score.",

                "market_value":
                    "Higher-quality vegetables may receive a better market price.",

                "summary": {
                    "key_differences": [
                        f"Vegetable 1 overall score: {score1}/100",
                        f"Vegetable 2 overall score: {score2}/100",
                        f"{winner_name} has the higher quality score."
                    ],
                    "buyer_advice":
                        f"Choose {winner_name} for better overall quality."
                },

                "note":
                    "AI analysis is an automated estimate and should be verified visually."
            }
        })

    except Exception as e:

        print("ERROR:", str(e))

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


if __name__ == "__main__":
    print("===================================")
    print(" MandiMart AI API")
    print("===================================")
    print("Running at:")
    print("http://localhost:5000")
    print("===================================")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
