<?php
// ============================================
// MANDIMART - AI VEGETABLE COMPARISON PROXY
// PHP bridge to Python Flask API
// Receives images from frontend, forwards to AI API
// ============================================

require_once 'db.php';

// AI API Configuration
define('AI_API_URL', 'http://localhost:5000');  // Change if Python runs on different port/host

// Only accept POST requests
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    jsonResponse(false, 'Only POST requests allowed');
}

// Check if user is logged in (optional - remove if public)
// requireLogin();

// ============================================
// HANDLE FILE UPLOADS
// ============================================

// Check for uploaded files
$hasFile1 = isset($_FILES['image1']) && $_FILES['image1']['error'] === UPLOAD_ERR_OK;
$hasFile2 = isset($_FILES['image2']) && $_FILES['image2']['error'] === UPLOAD_ERR_OK;

if (!$hasFile1 || !$hasFile2) {
    jsonResponse(false, 'Both vegetable images are required');
}

$file1 = $_FILES['image1'];
$file2 = $_FILES['image2'];

// Validate file types
$allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
if (!in_array($file1['type'], $allowedTypes) || !in_array($file2['type'], $allowedTypes)) {
    jsonResponse(false, 'Only JPG, PNG, GIF, WEBP images allowed');
}

// Validate file size (max 5MB each)
$maxSize = 5 * 1024 * 1024;
if ($file1['size'] > $maxSize || $file2['size'] > $maxSize) {
    jsonResponse(false, 'Each image must be less than 5MB');
}

// ============================================
// FORWARD TO PYTHON AI API
// ============================================

// Build multipart form data
$boundary = uniqid();
$delimiter = '-------------' . $boundary;

$postData = buildMultipartData($file1, 'image1', $delimiter);
$postData .= buildMultipartData($file2, 'image2', $delimiter);
$postData .= "--" . $delimiter . "--\r\n";

// Send request to Python API
$ch = curl_init();
curl_setopt_array($ch, [
    CURLOPT_URL => AI_API_URL . '/api/compare-vegetables',
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_POST => true,
    CURLOPT_POSTFIELDS => $postData,
    CURLOPT_HTTPHEADER => [
        'Content-Type: multipart/form-data; boundary=' . $delimiter,
        'Accept: application/json'
    ],
    CURLOPT_TIMEOUT => 30,  // 30 second timeout for AI processing
    CURLOPT_CONNECTTIMEOUT => 10
]);

$response = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$error = curl_error($ch);
curl_close($ch);

// Check for cURL errors
if ($error) {
    // Fallback: Return simulated response if AI API is offline
    $fallback = generateFallbackResponse($file1, $file2);
    jsonResponse(true, 'AI API offline - using simulated analysis (demo mode)', $fallback);
}

// Check HTTP status
if ($httpCode !== 200) {
    jsonResponse(false, 'AI service returned error: HTTP ' . $httpCode);
}

// Parse and return AI response
$aiResult = json_decode($response, true);
if (!$aiResult || !isset($aiResult['success'])) {
    jsonResponse(false, 'Invalid response from AI service');
}

// If AI API returned success, pass through
if ($aiResult['success']) {
    // Optionally save to database for history
    saveComparisonHistory($aiResult['comparison']);
    
    jsonResponse(true, 'Analysis complete', $aiResult['comparison']);
} else {
    jsonResponse(false, $aiResult['message'] ?? 'AI analysis failed');
}


// ============================================
// HELPER FUNCTIONS
// ============================================

function buildMultipartData($file, $fieldName, $delimiter) {
    $data = "--" . $delimiter . "\r\n";
    $data .= 'Content-Disposition: form-data; name="' . $fieldName . '"; filename="' . $file['name'] . '"' . "\r\n";
    $data .= 'Content-Type: ' . $file['type'] . "\r\n\r\n";
    $data .= file_get_contents($file['tmp_name']) . "\r\n";
    return $data;
}

function generateFallbackResponse($file1, $file2) {
    /**
     * Fallback response when AI API is unavailable
     * Simulates realistic analysis for demo purposes
     */
    
    // Generate pseudo-random but consistent scores based on file properties
    $seed1 = crc32($file1['name'] . $file1['size']);
    $seed2 = crc32($file2['name'] . $file2['size']);
    
    mt_srand($seed1);
    $score1 = mt_rand(65, 98);
    $fresh1 = mt_rand(70, 100);
    
    mt_srand($seed2);
    $score2 = mt_rand(60, 95);
    $fresh2 = mt_rand(65, 98);
    
    $winner = ($score1 >= $score2) ? 1 : 2;
    $margin = abs($score1 - $score2);
    
    return [
        "vegetable_1" => [
            "name" => "Vegetable 1",
            "freshness_score" => $fresh1,
            "quality_grade" => getGrade($score1),
            "color_score" => mt_rand(60, 95),
            "texture_score" => mt_rand(55, 90),
            "defect_score" => mt_rand(70, 100),
            "size_score" => mt_rand(60, 95),
            "overall_score" => $score1
        ],
        "vegetable_2" => [
            "name" => "Vegetable 2",
            "freshness_score" => $fresh2,
            "quality_grade" => getGrade($score2),
            "color_score" => mt_rand(55, 90),
            "texture_score" => mt_rand(50, 85),
            "defect_score" => mt_rand(65, 98),
            "size_score" => mt_rand(55, 90),
            "overall_score" => $score2
        ],
        "winner" => $winner,
        "winner_name" => "Vegetable " . $winner,
        "margin" => $margin,
        "recommendation" => ($winner == 1) 
            ? "Vegetable 1 is recommended based on visual analysis."
            : "Vegetable 2 is recommended based on visual analysis.",
        "market_value" => "Expect " . round($margin * 0.5) . "% price difference",
        "note" => "DEMO MODE: AI API offline. Install Python dependencies for real analysis."
    ];
}

function getGrade($score) {
    if ($score >= 90) return "A+";
    if ($score >= 80) return "A";
    if ($score >= 70) return "B";
    if ($score >= 60) return "C";
    if ($score >= 50) return "D";
    return "F";
}

function saveComparisonHistory($comparison) {
    /**
     * Save comparison result to database for user history
     * Requires user to be logged in
     */
    global $conn;
    
    if (!isLoggedIn()) return;
    
    $userId = $_SESSION['user_id'];
    $veg1Score = $comparison['vegetable_1']['overall_score'] ?? 0;
    $veg2Score = $comparison['vegetable_2']['overall_score'] ?? 0;
    $winner = $comparison['winner'] ?? 0;
    
    $stmt = $conn->prepare("INSERT INTO ai_compare_results (user_id, veg1_score, veg2_score, winner, analysis) VALUES (?, ?, ?, ?, ?)");
    $analysisJson = json_encode($comparison);
    $stmt->bind_param("iddis", $userId, $veg1Score, $veg2Score, $winner, $analysisJson);
    $stmt->execute();
}
?>