<?php
// ============================================
// MANDIMART CONFIGURATION
// Update these for your XAMPP/WAMP setup
// ============================================

// Database Settings
define('DB_HOST', 'localhost');
define('DB_USER', 'root');        // XAMPP default: root
define('DB_PASS', '');            // XAMPP default: empty
define('DB_NAME', 'mandimart');

// Site Settings
define('SITE_NAME', 'MandiMart');
define('SITE_URL', 'http://localhost/mandimart/');

// File Upload Settings
define('UPLOAD_DIR', '../uploads/');
define('MAX_FILE_SIZE', 5 * 1024 * 1024); // 5MB

// Session Settings
session_start();

// Error Reporting (disable in production)
error_reporting(E_ALL);
ini_set('display_errors', 1);

// Time Zone
date_default_timezone_set('Asia/Kolkata');
?>