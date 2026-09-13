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
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

from flask import Flask, request, jsonify
from flask_cors import CORS

import cv2
import numpy as np

from PIL import Image
import io


app = Flask(__name__)
CORS(app)


# =====================================================
# IMAGE LOADER
# =====================================================

def load_image(file):

    data = file.read()

    image = Image.open(
        io.BytesIO(data)
    ).convert("RGB")

    image = np.array(image)

    # RGB -> BGR for OpenCV
    image = cv2.cvtColor(
        image,
        cv2.COLOR_RGB2BGR
    )

    return image


# =====================================================
# COLOR ANALYSIS
# =====================================================

def analyze_color(image):

    hsv = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2HSV
    )

    saturation = np.mean(
        hsv[:, :, 1]
    )

    brightness = np.mean(
        hsv[:, :, 2]
    )

    # Healthy vegetables generally have
    # reasonable saturation and brightness.

    saturation_score = min(
        100,
        max(
            0,
            saturation / 2.55
        )
    )

    brightness_score = 100 - abs(
        brightness - 140
    ) / 1.4

    brightness_score = min(
        100,
        max(
            0,
            brightness_score
        )
    )

    color_score = (
        saturation_score * 0.6
        +
        brightness_score * 0.4
    )

    return round(color_score, 2)


# =====================================================
# TEXTURE ANALYSIS
# =====================================================

def analyze_texture(image):

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    # Laplacian variance measures
    # image texture/detail/sharpness.

    variance = cv2.Laplacian(
        gray,
        cv2.CV_64F
    ).var()

    texture_score = min(
        100,
        max(
            0,
            variance / 10
        )
    )

    return round(texture_score, 2)


# =====================================================
# DEFECT ANALYSIS
# =====================================================

def analyze_defects(image):

    hsv = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2HSV
    )

    # Detect dark/brown/black regions.
    #
    # These can represent bruises,
    # damaged areas or visible defects.

    lower = np.array(
        [0, 0, 0]
    )

    upper = np.array(
        [180, 255, 80]
    )

    mask = cv2.inRange(
        hsv,
        lower,
        upper
    )

    total_pixels = mask.shape[0] * mask.shape[1]

    defect_pixels = np.count_nonzero(mask)

    defect_percentage = (
        defect_pixels /
        total_pixels
    ) * 100

    defect_score = 100 - (
        defect_percentage * 4
    )

    defect_score = min(
        100,
        max(
            0,
            defect_score
        )
    )

    return round(defect_score, 2)


# =====================================================
# SIZE / SHAPE ANALYSIS
# =====================================================

def analyze_shape(image):

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    blurred = cv2.GaussianBlur(
        gray,
        (5, 5),
        0
    )

    _, threshold = cv2.threshold(
        blurred,
        0,
        255,
        cv2.THRESH_BINARY +
        cv2.THRESH_OTSU
    )

    contours, _ = cv2.findContours(
        threshold,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if not contours:
        return 50

    largest = max(
        contours,
        key=cv2.contourArea
    )

    area = cv2.contourArea(
        largest
    )

    perimeter = cv2.arcLength(
        largest,
        True
    )

    if perimeter == 0:
        return 50

    circularity = (
        4 * np.pi * area
    ) / (
        perimeter * perimeter
    )

    # More regular shapes get a higher score.
    shape_score = min(
        100,
        circularity * 100
    )

    return round(
        shape_score,
        2
    )


# =====================================================
# FRESHNESS
# =====================================================

def calculate_freshness(
    color,
    texture,
    defects
):

    freshness = (
        color * 0.40
        +
        texture * 0.25
        +
        defects * 0.35
    )

    return round(
        min(100, max(0, freshness)),
        2
    )


# =====================================================
# OVERALL QUALITY
# =====================================================

def analyze_image(image):

    color = analyze_color(
        image
    )

    texture = analyze_texture(
        image
    )

    defects = analyze_defects(
        image
    )

    shape = analyze_shape(
        image
    )

    freshness = calculate_freshness(
        color,
        texture,
        defects
    )

    overall = (
        freshness * 0.35
        +
        color * 0.20
        +
        texture * 0.15
        +
        defects * 0.20
        +
        shape * 0.10
    )

    overall = round(
        min(100, max(0, overall)),
        2
    )

    # Dynamic grade
    if overall >= 90:
        grade = "A+"
    elif overall >= 80:
        grade = "A"
    elif overall >= 70:
        grade = "B"
    elif overall >= 60:
        grade = "C"
    elif overall >= 50:
        grade = "D"
    else:
        grade = "F"

    # Estimated shelf life
    shelf_life = max(
        1,
        round(
            overall / 14
        )
    )

    return {
        "freshness_score": freshness,
        "color_score": color,
        "texture_score": texture,
        "defect_score": defects,
        "size_score": shape,
        "overall_score": overall,
        "quality_grade": grade,
        "estimated_shelf_life_days": shelf_life
    }


# =====================================================
# COMPARE TWO IMAGES
# =====================================================

@app.route(
    "/compare",
    methods=["POST"]
)
def compare():

    try:

        if (
            "image1" not in request.files
            or
            "image2" not in request.files
        ):

            return jsonify({
                "success": False,
                "message":
                    "Please upload two images."
            }), 400


        file1 = request.files["image1"]
        file2 = request.files["image2"]


        # Load actual uploaded images

        image1 = load_image(
            file1
        )

        image2 = load_image(
            file2
        )


        # Analyze ACTUAL images

        vegetable1 = analyze_image(
            image1
        )

        vegetable2 = analyze_image(
            image2
        )


        score1 = vegetable1[
            "overall_score"
        ]

        score2 = vegetable2[
            "overall_score"
        ]


        # =================================================
        # DYNAMIC WINNER
        # =================================================

        if score1 > score2:

            winner = 1
            winner_name = "Vegetable 1"

        elif score2 > score1:

            winner = 2
            winner_name = "Vegetable 2"

        else:

            winner = 0
            winner_name = "Tie"


        margin = round(
            abs(score1 - score2),
            2
        )


        # =================================================
        # DYNAMIC RECOMMENDATION
        # =================================================

        if winner == 1:

            recommendation = (
                "Vegetable 1 is recommended because "
                "it has the higher overall quality score."
            )

        elif winner == 2:

            recommendation = (
                "Vegetable 2 is recommended because "
                "it has the higher overall quality score."
            )

        else:

            recommendation = (
                "Both vegetables have very similar "
                "quality scores."
            )


        # =================================================
        # DYNAMIC DIFFERENCES
        # =================================================

        differences = []

        if vegetable1["freshness_score"] > vegetable2["freshness_score"]:

            differences.append(
                "Vegetable 1 has better freshness."
            )

        elif vegetable2["freshness_score"] > vegetable1["freshness_score"]:

            differences.append(
                "Vegetable 2 has better freshness."
            )


        if vegetable1["color_score"] > vegetable2["color_score"]:

            differences.append(
                "Vegetable 1 has better color characteristics."
            )

        elif vegetable2["color_score"] > vegetable1["color_score"]:

            differences.append(
                "Vegetable 2 has better color characteristics."
            )


        if vegetable1["defect_score"] > vegetable2["defect_score"]:

            differences.append(
                "Vegetable 1 shows fewer visible defects."
            )

        elif vegetable2["defect_score"] > vegetable1["defect_score"]:

            differences.append(
                "Vegetable 2 shows fewer visible defects."
            )


        if vegetable1["texture_score"] > vegetable2["texture_score"]:

            differences.append(
                "Vegetable 1 has stronger texture/detail characteristics."
            )

        elif vegetable2["texture_score"] > vegetable1["texture_score"]:

            differences.append(
                "Vegetable 2 has stronger texture/detail characteristics."
            )


        # =================================================
        # RESPONSE
        # =================================================

        return jsonify({

            "success": True,

            "data": {

                "vegetable_1": vegetable1,

                "vegetable_2": vegetable2,

                "winner": winner,

                "winner_name": winner_name,

                "margin": margin,

                "recommendation":
                    recommendation,

                "market_value":
                    "Higher quality produce may receive a better market price.",

                "summary": {

                    "key_differences":
                        differences,

                    "buyer_advice":
                        recommendation
                },

                "note":
                    "Scores are computer-vision estimates based on the uploaded images."
            }

        })


    except Exception as e:

        print(
            "Comparison error:",
            str(e)
        )

        return jsonify({

            "success": False,

            "message":
                "Image analysis failed: "
                + str(e)

        }), 500


# =====================================================
# HOME / HEALTH CHECK
# =====================================================

@app.route("/")
def home():

    return jsonify({

        "success": True,

        "service":
            "MandiMart Dynamic AI Comparison API",

        "status":
            "running",

        "endpoint":
            "/compare"

    })


# =====================================================
# START SERVER
# =====================================================

if __name__ == "__main__":

    print(
        "\n🌾 MandiMart Dynamic AI API"
    )

    print(
        "🚀 http://localhost:5000"
    )

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )

from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np

app = Flask(__name__)

CORS(app)


def analyze_image(file):

    # Read uploaded image
    image_bytes = file.read()

    image_array = np.frombuffer(
        image_bytes,
        np.uint8
    )

    image = cv2.imdecode(
        image_array,
        cv2.IMREAD_COLOR
    )

    if image is None:
        raise ValueError("Invalid image")

    # Resize
    image = cv2.resize(
        image,
        (500, 500)
    )

    # Convert to HSV
    hsv = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2HSV
    )

    # Average brightness
    brightness = float(
        np.mean(hsv[:, :, 2])
    )

    # Saturation
    saturation = float(
        np.mean(hsv[:, :, 1])
    )

    # ------------------------------------------------
    # BASIC DYNAMIC IMAGE QUALITY CALCULATION
    # ------------------------------------------------

    freshness_score = min(
        100,
        max(
            0,
            int(
                50
                + brightness * 0.35
                + saturation * 0.25
            )
        )
    )

    color_score = min(
        100,
        max(
            0,
            int(
                50
                + saturation * 0.5
            )
        )
    )

    # Texture using Laplacian variance
    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    texture_value = cv2.Laplacian(
        gray,
        cv2.CV_64F
    ).var()

    texture_score = min(
        100,
        max(
            0,
            int(texture_value / 10)
        )
    )

    # Simple defect estimation
    dark_pixels = np.sum(
        hsv[:, :, 2] < 40
    )

    total_pixels = (
        hsv.shape[0] *
        hsv.shape[1]
    )

    defect_ratio = (
        dark_pixels /
        total_pixels
    )

    defect_score = min(
        100,
        max(
            0,
            int(100 - defect_ratio * 100)
        )
    )

    size_score = 80

    overall_score = int(
        freshness_score * 0.30 +
        color_score * 0.20 +
        texture_score * 0.20 +
        defect_score * 0.20 +
        size_score * 0.10
    )

    if overall_score >= 85:
        grade = "A+"
    elif overall_score >= 75:
        grade = "A"
    elif overall_score >= 65:
        grade = "B"
    elif overall_score >= 50:
        grade = "C"
    else:
        grade = "D"

    shelf_life = max(
        1,
        int(overall_score / 12)
    )

    return {
        "overall_score": overall_score,
        "freshness_score": freshness_score,
        "color_score": color_score,
        "texture_score": texture_score,
        "defect_score": defect_score,
        "size_score": size_score,
        "quality_grade": grade,
        "estimated_shelf_life_days": shelf_life
    }


@app.route("/")
def home():

    return jsonify({
        "success": True,
        "message": "MandiMart AI API is running"
    })


@app.route("/compare", methods=["POST"])
def compare():

    try:

        image1 = request.files.get("image1")
        image2 = request.files.get("image2")

        if image1 is None or image2 is None:

            return jsonify({
                "success": False,
                "message": "Both images are required."
            }), 400

        result1 = analyze_image(image1)
        result2 = analyze_image(image2)

        score1 = result1["overall_score"]
        score2 = result2["overall_score"]

        if score1 > score2:

            winner = 1
            winner_name = "Vegetable 1"

        elif score2 > score1:

            winner = 2
            winner_name = "Vegetable 2"

        else:

            winner = 0
            winner_name = "Both vegetables"

        margin = abs(
            score1 - score2
        )

        if winner == 1:

            recommendation = (
                "Vegetable 1 has better overall "
                "quality and freshness."
            )

        elif winner == 2:

            recommendation = (
                "Vegetable 2 has better overall "
                "quality and freshness."
            )

        else:

            recommendation = (
                "Both vegetables have similar "
                "overall quality."
            )

        return jsonify({

            "success": True,

            "data": {

                "vegetable_1": result1,

                "vegetable_2": result2,

                "winner": winner,

                "winner_name": winner_name,

                "margin": margin,

                "recommendation": recommendation,

                "market_value":
                    f"{winner_name} is likely to "
                    "receive a better market price.",

                "summary": {

                    "key_differences": [
                        f"Vegetable 1 score: {score1}",
                        f"Vegetable 2 score: {score2}",
                        f"Quality difference: {margin} points"
                    ],

                    "buyer_advice":
                        f"Choose {winner_name} "
                        "for better quality."

                }

            }

        })

    except Exception as e:

        print("ERROR:", str(e))

        return jsonify({

            "success": False,

            "message": str(e)

        }), 500


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
