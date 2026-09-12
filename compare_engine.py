#!/usr/bin/env python3
# ============================================
# VEGETABLE IMAGE ANALYSIS ENGINE
# Computer Vision + Image Processing for Quality Scoring
# Uses: OpenCV, NumPy, scikit-image
# ============================================

import cv2
import numpy as np
from skimage import feature, measure, color, filters
from skimage.measure import shannon_entropy
import colorsys
from collections import Counter


def analyze_vegetable(img_rgb):
    """
    Analyze a vegetable image and return comprehensive quality metrics
    
    Parameters:
        img_rgb: numpy array (RGB image)
    
    Returns:
        dict with all analysis scores
    """
    
    # Ensure image is in correct format
    if img_rgb is None or img_rgb.size == 0:
        return None
    
    # Resize for consistent analysis (but keep aspect ratio info)
    height, width = img_rgb.shape[:2]
    analysis_img = cv2.resize(img_rgb, (400, 400))
    
    # Convert to different color spaces for analysis
    img_hsv = cv2.cvtColor(analysis_img, cv2.COLOR_RGB2HSV)
    img_lab = cv2.cvtColor(analysis_img, cv2.COLOR_RGB2LAB)
    img_gray = cv2.cvtColor(analysis_img, cv2.COLOR_RGB2GRAY)
    
    # ========================================
    # 1. COLOR ANALYSIS (Freshness indicator)
    # ========================================
    color_score = analyze_color(img_rgb, img_hsv)
    
    # ========================================
    # 2. TEXTURE ANALYSIS (Surface quality)
    # ========================================
    texture_score = analyze_texture(img_gray)
    
    # ========================================
    # 3. DEFECT DETECTION (Spots, bruises, mold)
    # ========================================
    defect_score = analyze_defects(img_rgb, img_hsv, img_gray)
    
    # ========================================
    # 4. SIZE & SHAPE ANALYSIS
    # ========================================
    size_score = analyze_size_shape(img_rgb, img_gray)
    
    # ========================================
    # 5. EDGE SHARPNESS (Focus/quality of image)
    # ========================================
    sharpness_score = analyze_sharpness(img_gray)
    
    # ========================================
    # 6. BRIGHTNESS & CONTRAST
    # ========================================
    brightness_score = analyze_brightness_contrast(img_gray)
    
    # ========================================
    # 7. ENTROPY (Information content / complexity)
    # ========================================
    entropy_score = analyze_entropy(img_gray)
    
    # ========================================
    # CALCULATE OVERALL SCORES
    # ========================================
    
    # Freshness: Higher is fresher (color + texture + low defects)
    freshness_score = round(
        (color_score * 0.35) +
        (texture_score * 0.25) +
        (defect_score * 0.30) +
        (sharpness_score * 0.10)
    , 1)
    
    # Overall quality composite
    overall_score = round(
        (freshness_score * 0.40) +
        (color_score * 0.20) +
        (texture_score * 0.15) +
        (defect_score * 0.15) +
        (size_score * 0.10)
    , 1)
    
    # Determine grade
    quality_grade = get_quality_grade(overall_score)
    
    # Estimate days until spoilage (rough estimate)
    estimated_shelf_life = estimate_shelf_life(freshness_score, defect_score)
    
    return {
        # Core scores
        "freshness_score": min(100, max(0, freshness_score)),
        "overall_score": min(100, max(0, overall_score)),
        "quality_grade": quality_grade,
        
        # Component scores
        "color_score": round(color_score, 1),
        "texture_score": round(texture_score, 1),
        "defect_score": round(defect_score, 1),
        "size_score": round(size_score, 1),
        "sharpness_score": round(sharpness_score, 1),
        "brightness_score": round(brightness_score, 1),
        "entropy_score": round(entropy_score, 1),
        
        # Derived metrics
        "estimated_shelf_life_days": estimated_shelf_life,
        
        # Image metadata
        "image_dimensions": {"width": width, "height": height},
        
        # Analysis flags
        "has_defects": defect_score < 70,
        "is_fresh": freshness_score >= 75,
        "is_recommended": overall_score >= 70
    }


def analyze_color(img_rgb, img_hsv):
    """
    Analyze color vibrancy and health indicators
    """
    # Calculate mean saturation (vibrancy)
    mean_saturation = np.mean(img_hsv[:, :, 1])
    
    # Calculate color variance (uniformity)
    std_hue = np.std(img_hsv[:, :, 0])
    
    # Green health indicator (for leafy vegetables)
    # Count green-ish pixels
    lower_green = np.array([35, 40, 40])
    upper_green = np.array([85, 255, 255])
    green_mask = cv2.inRange(img_hsv, lower_green, upper_green)
    green_ratio = np.sum(green_mask > 0) / green_mask.size * 100
    
    # Yellowing/Browning detection (bad sign)
    lower_yellow = np.array([20, 100, 100])
    upper_yellow = np.array([35, 255, 255])
    yellow_mask = cv2.inRange(img_hsv, lower_yellow, upper_yellow)
    yellow_ratio = np.sum(yellow_mask > 0) / yellow_mask.size * 100
    
    # Browning (very bad)
    lower_brown = np.array([10, 50, 50])
    upper_brown = np.array([20, 150, 150])
    brown_mask = cv2.inRange(img_hsv, lower_brown, upper_brown)
    brown_ratio = np.sum(brown_mask > 0) / brown_mask.size * 100
    
    # Color score calculation
    # High saturation = good, low yellow/brown = good
    saturation_score = min(100, mean_saturation * 2)
    color_health = max(0, 100 - yellow_ratio * 3 - brown_ratio * 10)
    
    # Boost for healthy green
    green_bonus = min(20, green_ratio / 3)
    
    color_score = (saturation_score * 0.5) + (color_health * 0.4) + green_bonus
    return min(100, color_score)


def analyze_texture(img_gray):
    """
    Analyze surface texture using GLCM (Gray Level Co-occurrence Matrix)
    """
    # Resize for faster processing
    small_gray = cv2.resize(img_gray, (128, 128))
    
    # Calculate GLCM features
    try:
        glcm = feature.graycomatrix(small_gray, distances=[1], angles=[0], levels=256, symmetric=True, normed=True)
        
        contrast = feature.graycoprops(glcm, 'contrast')[0, 0]
        dissimilarity = feature.graycoprops(glcm, 'dissimilarity')[0, 0]
        homogeneity = feature.graycoprops(glcm, 'homogeneity')[0, 0]
        energy = feature.graycoprops(glcm, 'energy')[0, 0]
        correlation = feature.graycoprops(glcm, 'correlation')[0, 0]
        
        # Smooth texture (high homogeneity, low contrast) = fresh
        # Rough/uneven texture = aging or damaged
        
        texture_quality = (
            homogeneity * 40 +           # Smoothness is good
            energy * 30 +                 # Uniformity
            (1 - min(1, contrast / 100)) * 20 +  # Low contrast is good
            max(0, correlation) * 10     # Correlation
        )
        
        return min(100, texture_quality * 100)
        
    except Exception as e:
        # Fallback: use simple gradient analysis
        sobelx = cv2.Sobel(img_gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(img_gray, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(sobelx**2 + sobely**2)
        mean_gradient = np.mean(gradient_magnitude)
        
        # Lower gradient = smoother = fresher
        return max(0, 100 - min(100, mean_gradient / 10))


def analyze_defects(img_rgb, img_hsv, img_gray):
    """
    Detect spots, bruises, mold, and other defects
    """
    # Method 1: Dark spot detection
    _, dark_thresh = cv2.threshold(img_gray, 60, 255, cv2.THRESH_BINARY_INV)
    dark_spots = np.sum(dark_thresh > 0) / dark_thresh.size * 100
    
    # Method 2: Unusual color detection (LAB color space)
    img_lab = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(img_lab)
    
    # High b value (yellow/blue) anomalies
    _, b_thresh = cv2.threshold(b, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    b_anomaly = np.sum(b_thresh > 0) / b_thresh.size * 100
    
    # Method 3: Edge density in center (soft rot detection)
    edges = cv2.Canny(img_gray, 50, 150)
    edge_density = np.sum(edges > 0) / edges.size * 100
    
    # Calculate defect score (inverse: higher = fewer defects)
    # Dark spots are bad
    spot_penalty = min(50, dark_spots * 2)
    
    # Color anomalies
    color_penalty = min(30, b_anomaly * 1.5)
    
    # Excessive edges (wrinkling, damage)
    edge_penalty = min(20, edge_density * 2)
    
    defect_score = max(0, 100 - spot_penalty - color_penalty - edge_penalty)
    return defect_score


def analyze_size_shape(img_rgb, img_gray):
    """
    Analyze size and shape regularity
    """
    # Find contours
    _, thresh = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return 50  # Neutral score if no clear object
    
    # Get largest contour (main vegetable)
    largest = max(contours, key=cv2.contourArea)
    
    # Calculate shape metrics
    area = cv2.contourArea(largest)
    perimeter = cv2.arcLength(largest, True)
    
    if perimeter == 0:
        return 50
    
    # Circularity: 1 = perfect circle, lower = irregular
    circularity = 4 * np.pi * area / (perimeter ** 2)
    
    # Aspect ratio
    x, y, w, h = cv2.boundingRect(largest)
    aspect_ratio = min(w, h) / max(w, h) if max(w, h) > 0 else 1
    
    # Size score (larger = better for most vegetables, up to a point)
    # Normalize by image area
    img_area = img_rgb.shape[0] * img_rgb.shape[1]
    size_ratio = area / img_area
    
    # Optimal size is 20-60% of image
    if 0.2 <= size_ratio <= 0.6:
        size_score = 100
    elif size_ratio < 0.2:
        size_score = size_ratio / 0.2 * 100
    else:
        size_score = max(0, 100 - (size_ratio - 0.6) * 200)
    
    # Shape regularity (closer to circle/oval = better)
    shape_score = (circularity * 50) + (aspect_ratio * 50)
    
    return (size_score * 0.6) + (shape_score * 0.4)


def analyze_sharpness(img_gray):
    """
    Measure image sharpness using Laplacian variance
    """
    laplacian_var = cv2.Laplacian(img_gray, cv2.CV_64F).var()
    
    # Higher variance = sharper image
    # Normalize to 0-100 scale
    # Typical range: 0-1000
    sharpness = min(100, laplacian_var / 10)
    return sharpness


def analyze_brightness_contrast(img_gray):
    """
    Analyze overall brightness and contrast
    """
    mean_brightness = np.mean(img_gray)
    std_brightness = np.std(img_gray)
    
    # Normalize to 0-100
    brightness = mean_brightness / 2.55  # 255 -> 100
    contrast = min(100, std_brightness / 2.55)
    
    # Optimal brightness is 40-70%
    brightness_score = 100 - abs(brightness - 55) * 2
    
    return (brightness_score * 0.5) + (min(100, contrast * 2) * 0.5)


def analyze_entropy(img_gray):
    """
    Calculate Shannon entropy (image information content)
    """
    try:
        entropy = shannon_entropy(img_gray)
        # Normalize: typical range 0-8
        return min(100, entropy * 12.5)
    except:
        return 50


def get_quality_grade(score):
    """
    Convert numeric score to letter grade
    """
    if score >= 90:
        return "A+"
    elif score >= 80:
        return "A"
    elif score >= 70:
        return "B"
    elif score >= 60:
        return "C"
    elif score >= 50:
        return "D"
    else:
        return "F"


def estimate_shelf_life(freshness, defect_score):
    """
    Estimate remaining shelf life in days
    """
    base_life = 14  # days for fresh vegetable
    
    # Adjust based on freshness
    freshness_factor = freshness / 100
    
    # Defects reduce life
    defect_penalty = (100 - defect_score) / 100 * 7
    
    estimated = (base_life * freshness_factor) - defect_penalty
    return max(0, round(estimated, 1))


def compare_two_vegetables(result1, result2):
    """
    Compare two vegetable analysis results and determine winner
    """
    score1 = result1["overall_score"]
    score2 = result2["overall_score"]
    
    # Calculate margin
    margin = abs(score1 - score2)
    margin_percent = round(margin, 1)
    
    # Determine winner
    if score1 > score2:
        winner = 1
        winner_name = "Vegetable 1"
        winner_score = score1
        loser_score = score2
    elif score2 > score1:
        winner = 2
        winner_name = "Vegetable 2"
        winner_score = score2
        loser_score = score1
    else:
        winner = 0
        winner_name = "Tie"
        winner_score = score1
        loser_score = score2
    
    # Generate recommendation
    if winner == 0:
        recommendation = "Both vegetables are of equal quality. Either is a good choice."
        market_value = "Both have similar market value"
    elif margin < 5:
        recommendation = f"{winner_name} is slightly better, but both are acceptable choices."
        market_value = "Marginal price difference expected"
    elif margin < 15:
        recommendation = f"{winner_name} is noticeably better quality. Recommended for purchase."
        market_value = f"Expect 10-15% premium for {winner_name}"
    else:
        recommendation = f"{winner_name} is significantly superior in quality. Strongly recommended."
        market_value = f"Expect 20-30% premium for {winner_name}"
    
    # Detailed comparison points
    comparison_points = []
    
    if result1["freshness_score"] > result2["freshness_score"] + 5:
        comparison_points.append("Vegetable 1 has better freshness")
    elif result2["freshness_score"] > result1["freshness_score"] + 5:
        comparison_points.append("Vegetable 2 has better freshness")
    
    if result1["color_score"] > result2["color_score"] + 5:
        comparison_points.append("Vegetable 1 has more vibrant color")
    elif result2["color_score"] > result1["color_score"] + 5:
        comparison_points.append("Vegetable 2 has more vibrant color")
    
    if result1["defect_score"] > result2["defect_score"] + 5:
        comparison_points.append("Vegetable 1 has fewer visible defects")
    elif result2["defect_score"] > result1["defect_score"] + 5:
        comparison_points.append("Vegetable 2 has fewer visible defects")
    
    # Build summary
    summary = {
        "score_difference": margin_percent,
        "freshness_comparison": {
            "veg1": result1["freshness_score"],
            "veg2": result2["freshness_score"],
            "better": 1 if result1["freshness_score"] > result2["freshness_score"] else 2
        },
        "color_comparison": {
            "veg1": result1["color_score"],
            "veg2": result2["color_score"],
            "better": 1 if result1["color_score"] > result2["color_score"] else 2
        },
        "defect_comparison": {
            "veg1": result1["defect_score"],
            "veg2": result2["defect_score"],
            "better": 1 if result1["defect_score"] > result2["defect_score"] else 2
        },
        "key_differences": comparison_points,
        "buyer_advice": recommendation
    }
    
    return {
        "winner": winner,
        "winner_name": winner_name,
        "winner_score": winner_score,
        "loser_score": loser_score,
        "margin": margin_percent,
        "recommendation": recommendation,
        "market_value": market_value,
        "summary": summary
    }


# Test function
if __name__ == "__main__":
    print("Compare Engine loaded successfully")
    print("Run app.py to start the API server")