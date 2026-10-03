<?php
// proxy.php - Token hidden on server side (not visible in browser)
header("Access-Control-Allow-Origin: https://vasventures.in");
header("Access-Control-Allow-Methods: POST, GET, DELETE, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With");
header("Content-Type: application/json");

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

// =============================================
// BEARER TOKEN - HIDDEN ON SERVER (NOT VISIBLE IN BROWSER)
// =============================================
// The token is NOT stored in this file (the repo is public).
// It is read from an env file OUTSIDE public_html on the server:
//     /home/<cpanel-user>/.vasventures.env   ->   TOGETHR_API_TOKEN=xxxx
// (local testing fallback: a .env file next to this one – never committed)
function vas_env($key) {
    foreach ([dirname(__DIR__, 2) . '/.vasventures.env', __DIR__ . '/.env'] as $file) {
        if (!is_readable($file)) continue;
        foreach (file($file, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES) as $line) {
            $line = trim($line);
            if ($line === '' || $line[0] === '#' || strpos($line, '=') === false) continue;
            [$k, $v] = array_map('trim', explode('=', $line, 2));
            if ($k === $key) return trim($v, "\"'");
        }
    }
    return '';
}
define('API_BEARER_TOKEN', vas_env('TOGETHR_API_TOKEN'));
if (API_BEARER_TOKEN === '') {
    http_response_code(500);
    echo json_encode(['error' => 'Server is not configured']);
    exit();
}

$endpoint = $_GET['endpoint'] ?? '';
$target_url = '';

switch ($endpoint) {
    case 'send-otp':
        $target_url = 'https://togethr-auth-service-20740607843.asia-south1.run.app/delete/account/send-otp';
        break;
    case 'verify-otp':
        $target_url = 'https://togethr-auth-service-20740607843.asia-south1.run.app/delete/account/verify-otp';
        break;
    case 'delete-account':
        $target_url = 'https://togethr-profile-service-20740607843.asia-south1.run.app/delete-user-account';
        break;
    default:
        http_response_code(400);
        echo json_encode(['error' => 'Unknown endpoint']);
        exit();
}

$request_body = file_get_contents('php://input');
$request_method = $_SERVER['REQUEST_METHOD'];

// =============================================
// ALWAYS ADD THE TOKEN SERVER-SIDE
// (Browser never sees this token)
// =============================================
$headers = [
    'Content-Type: application/json',
    'Authorization: Bearer ' . API_BEARER_TOKEN
];

// Forward the request to the API
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $target_url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_CUSTOMREQUEST, $request_method);
curl_setopt($ch, CURLOPT_POSTFIELDS, $request_body);
curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
curl_setopt($ch, CURLOPT_TIMEOUT, 30);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, true);
curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 2);

$response = curl_exec($ch);
$http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$curl_error = curl_error($ch);
curl_close($ch);

if ($curl_error) {
    http_response_code(500);
    echo json_encode(['error' => 'Proxy error: ' . $curl_error]);
} else {
    http_response_code($http_code);
    echo $response;
}
?>