# Test Campaign Script for Email Automation Backend
# Replace these with your actual credentials
$username = "sky"
$password = "12121212"
$baseUrl = "https://email-automate-ob1a.onrender.com"

# Function to make API requests
function Invoke-ApiRequest {
    param (
        [string]$Uri,
        [string]$Method = "GET",
        [object]$Body = $null,
        [hashtable]$Headers = @{},
        [Microsoft.PowerShell.Commands.WebRequestSession]$Session
    )
    
    $params = @{
        Uri = $Uri
        Method = $Method
        Headers = $Headers
        WebSession = $Session
    }
    
    if ($Body) {
        $params["Body"] = $Body
        $params["ContentType"] = "application/json"
    }
    
    try {
        $response = Invoke-WebRequest @params -UseBasicParsing
        return @{
            Success = $true
            StatusCode = $response.StatusCode
            Content = $response.Content | ConvertFrom-Json
            Headers = $response.Headers
        }
    } catch {
        $errorResponse = $_.Exception.Response
        $errorContent = if ($errorResponse) { 
            $reader = New-Object System.IO.StreamReader($errorResponse.GetResponseStream())
            $reader.ReadToEnd() | ConvertFrom-Json
        } else { $_.Exception.Message }
        
        return @{
            Success = $false
            StatusCode = if ($errorResponse) { $errorResponse.StatusCode } else { 0 }
            Error = $errorContent
            Exception = $_.Exception
        }
    }
}

# 1. Get CSRF Token
Write-Host "Step 1: Getting CSRF token..." -ForegroundColor Cyan
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$csrfResponse = Invoke-ApiRequest -Uri "$baseUrl/api/csrf-token/" -Session $session

if (-not $csrfResponse.Success) {
    Write-Host "Failed to get CSRF token" -ForegroundColor Red
    Write-Host "Error: $($csrfResponse.Error)" -ForegroundColor Red
    exit 1
}

$csrfToken = $csrfResponse.Content.csrfToken
Write-Host "CSRF Token: $csrfToken" -ForegroundColor Green

# 2. Login
Write-Host "`nStep 2: Logging in..." -ForegroundColor Cyan
$loginBody = @{
    username = $username
    password = $password
} | ConvertTo-Json

$loginResponse = Invoke-ApiRequest -Uri "$baseUrl/api/auth/login/" `
    -Method POST `
    -Body $loginBody `
    -Headers @{
        "X-CSRFToken" = $csrfToken
        "Referer" = $baseUrl
    } `
    -Session $session

if (-not $loginResponse.Success) {
    Write-Host "Login failed" -ForegroundColor Red
    Write-Host "Status: $($loginResponse.StatusCode)" -ForegroundColor Red
    Write-Host "Error: $($loginResponse.Error)" -ForegroundColor Red
    exit 1
}

Write-Host "Login successful" -ForegroundColor Green
Write-Host "User: $($loginResponse.Content)" -ForegroundColor Green

# 3. List Campaigns
Write-Host "`nStep 3: Listing campaigns..." -ForegroundColor Cyan
$campaignsResponse = Invoke-ApiRequest -Uri "$baseUrl/api/campaigns/" `
    -Headers @{
        "X-CSRFToken" = $csrfToken
        "Referer" = $baseUrl
    } `
    -Session $session

if ($campaignsResponse.Success) {
    Write-Host "Campaigns retrieved successfully" -ForegroundColor Green
    Write-Host "Total campaigns: $($campaignsResponse.Content.count)" -ForegroundColor Green
    $campaignsResponse.Content.results | Format-Table -AutoSize
} else {
    Write-Host "Failed to retrieve campaigns" -ForegroundColor Red
    Write-Host "Status: $($campaignsResponse.StatusCode)" -ForegroundColor Red
    Write-Host "Error: $($campaignsResponse.Error)" -ForegroundColor Red
}

# 4. Create a Test Campaign (Optional)
Write-Host "`nStep 4: Creating a test campaign..." -ForegroundColor Cyan

# First, clear any existing cookies and headers
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession

# 4.1 Get a fresh CSRF token
Write-Host "`n4.1 Getting fresh CSRF token..." -ForegroundColor Cyan
$csrfResponse = Invoke-WebRequest -Uri "$baseUrl/api/csrf-token/" -Headers @{"Accept" = "application/json"} -WebSession $session -UseBasicParsing
$csrfToken = ($csrfResponse.Content | ConvertFrom-Json).csrfToken

# 4.2 Login with the new session
Write-Host "`n4.2 Logging in..." -ForegroundColor Cyan
$loginBody = @{
    username = $username
    password = $password
} | ConvertTo-Json

$loginResponse = Invoke-WebRequest -Uri "$baseUrl/api/auth/login/" `
    -Method POST `
    -Body $loginBody `
    -ContentType "application/json" `
    -Headers @{
        "X-CSRFToken" = $csrfToken
        "Referer" = $baseUrl
        "Origin" = $baseUrl
    } `
    -WebSession $session `
    -UseBasicParsing

# 4.3 Get the CSRF token from cookies after login
$csrfCookie = $session.Cookies.GetCookies([Uri]$baseUrl) | Where-Object { $_.Name -eq 'csrftoken' } | Select-Object -First 1
$cookieToken = $csrfCookie.Value

Write-Host "CSRF Token from Cookie after login: $cookieToken" -ForegroundColor Yellow

# 4.4 Create the campaign
$newCampaign = @{
    name = "Test Campaign $(Get-Date -Format 'yyyyMMdd-HHmmss')"
    subject = "Test Subject"
    body = "This is a test campaign created by the test script."
    email = "test@example.com"
    provider = "gmail"
}

$jsonBody = $newCampaign | ConvertTo-Json

# 4.3 Prepare request headers
$headers = @{
    "X-CSRFToken" = $cookieToken
    "Content-Type" = "application/json"
    "Origin" = $baseUrl
    "Referer" = $baseUrl
    "X-Requested-With" = "XMLHttpRequest"
}

# Debug output
Write-Host "`n4.3 Request Details:" -ForegroundColor Cyan
Write-Host "URL: $baseUrl/api/campaigns/" -ForegroundColor Cyan
Write-Host "Method: POST" -ForegroundColor Cyan
Write-Host "Headers:" -ForegroundColor Cyan
$headers | Format-Table -AutoSize

Write-Host "Request Body:" -ForegroundColor Cyan
$jsonBody

# Prepare the request
$uri = "$baseUrl/api/campaigns/"

# Debug output
Write-Host "`nMaking POST request to: $uri" -ForegroundColor Cyan
Write-Host "Request Headers:" -ForegroundColor Cyan
$headers | Format-Table -AutoSize
Write-Host "Request Body:" -ForegroundColor Cyan
$jsonBody

# 4.4 Sending request...
Write-Host "`n4.4 Sending request..." -ForegroundColor Cyan

# Get the latest CSRF token from cookies
$latestCsrfCookie = $session.Cookies.GetCookies([Uri]$baseUrl) | Where-Object { $_.Name -eq 'csrftoken' } | Select-Object -First 1
$latestCsrfToken = $latestCsrfCookie.Value

# Update headers with the latest token
$headers["X-CSRFToken"] = $latestCsrfToken

Write-Host "Using CSRF Token: $latestCsrfToken" -ForegroundColor Yellow
Write-Host "Session ID: $($session.Cookies.GetCookies([Uri]$baseUrl) | Where-Object { $_.Name -eq 'sessionid' } | Select-Object -ExpandProperty Value)" -ForegroundColor Yellow

# Debug: Show all cookies
Write-Host "`nCurrent Cookies:" -ForegroundColor Cyan
$session.Cookies.GetCookies([Uri]$baseUrl) | Select-Object Name, Value, Domain, Path, Secure, HttpOnly | Format-Table -AutoSize

# Make the request with the latest CSRF token
try {
    $createResponse = Invoke-WebRequest -Uri "$baseUrl/api/campaigns/" `
        -Method POST `
        -Body $jsonBody `
        -Headers $headers `
        -WebSession $session `
        -UseBasicParsing `
        -ErrorAction Stop

    if ($createResponse.StatusCode -in @(200, 201)) {
        Write-Host "Campaign created successfully!" -ForegroundColor Green
        $responseData = $createResponse.Content | ConvertFrom-Json
        Write-Host "Response: $($responseData | ConvertTo-Json -Depth 5)" -ForegroundColor Green
    } else {
        Write-Host "Unexpected status code: $($createResponse.StatusCode)" -ForegroundColor Red
        Write-Host "Response: $($createResponse.Content)" -ForegroundColor Red
    }
} catch {
    Write-Host "Error creating campaign:" -ForegroundColor Red
    Write-Host "Status Code: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Red
    Write-Host "Status Description: $($_.Exception.Response.StatusDescription)" -ForegroundColor Red
    
    try {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $reader.BaseStream.Position = 0
        $reader.DiscardBufferedData()
        $responseBody = $reader.ReadToEnd()
        Write-Host "Response: $responseBody" -ForegroundColor Red
    } catch {
        Write-Host "Could not read response body: $_" -ForegroundColor Red
    }
}

Write-Host "`nTest complete!" -ForegroundColor Cyan
