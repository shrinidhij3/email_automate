# Local Test Script for Email Automation Backend
# This script tests against a local development server

# Configuration
$username = "sky"
$password = "12121212"
$baseUrl = "http://localhost:8000"  # Local development server

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
        ContentType = "application/json"
        UseBasicParsing = $true
    }

    if ($Body) {
        $params.Body = $Body | ConvertTo-Json -Depth 10
    }

    try {
        $response = Invoke-WebRequest @params -ErrorAction Stop
        
        # Try to parse JSON response
        try {
            $content = $response.Content | ConvertFrom-Json -ErrorAction Stop
        } catch {
            $content = $response.Content
        }
        
        return @{
            Success = $true
            StatusCode = $response.StatusCode
            Content = $content
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
}

$loginResponse = Invoke-ApiRequest -Uri "$baseUrl/api/auth/login/" `
    -Method POST `
    -Body $loginBody `
    -Headers @{
        "X-CSRFToken" = $csrfToken
        "Referer" = $baseUrl
        "Origin" = $baseUrl
    } `
    -Session $session

if (-not $loginResponse.Success) {
    Write-Host "Login failed" -ForegroundColor Red
    Write-Host "Status: $($loginResponse.StatusCode)" -ForegroundColor Red
    Write-Host "Error: $($loginResponse.Error)" -ForegroundColor Red
    exit 1
}

Write-Host "Login successful" -ForegroundColor Green
Write-Host "User: $($loginResponse.Content | ConvertTo-Json -Depth 1)" -ForegroundColor Green

# 3. Get Campaigns
Write-Host "`nStep 3: Listing campaigns..." -ForegroundColor Cyan
$campaignsResponse = Invoke-ApiRequest -Uri "$baseUrl/api/campaigns/" -Session $session

if (-not $campaignsResponse.Success) {
    Write-Host "Failed to get campaigns" -ForegroundColor Red
    Write-Host "Status: $($campaignsResponse.StatusCode)" -ForegroundColor Red
    Write-Host "Error: $($campaignsResponse.Error)" -ForegroundColor Red
    exit 1
}

Write-Host "Campaigns retrieved successfully" -ForegroundColor Green
$campaigns = $campaignsResponse.Content
Write-Host "Total campaigns: $($campaigns.Count)" -ForegroundColor Green
$campaigns | Format-Table -AutoSize

# 4. Create a Test Campaign
Write-Host "`nStep 4: Creating a test campaign..." -ForegroundColor Cyan

# Get fresh CSRF token for the POST request
$csrfResponse = Invoke-ApiRequest -Uri "$baseUrl/api/csrf-token/" -Session $session
if ($csrfResponse.Success) {
    $csrfToken = $csrfResponse.Content.csrfToken
    Write-Host "New CSRF Token for POST: $csrfToken" -ForegroundColor Yellow
}

$newCampaign = @{
    name = "Test Campaign $(Get-Date -Format 'yyyyMMdd-HHmmss')"
    subject = "Test Subject"
    body = "This is a test campaign created by the local test script."
    email = "test@example.com"
    provider = "gmail"
}

$jsonBody = $newCampaign | ConvertTo-Json

# Debug output
Write-Host "`nSending request to: $baseUrl/api/campaigns/" -ForegroundColor Cyan
Write-Host "Method: POST" -ForegroundColor Cyan
Write-Host "Headers:" -ForegroundColor Cyan
@{
    "X-CSRFToken" = $csrfToken
    "Content-Type" = "application/json"
    "Referer" = $baseUrl
    "Origin" = $baseUrl
} | Format-Table -AutoSize

Write-Host "Request Body:" -ForegroundColor Cyan
$jsonBody

try {
    $createResponse = Invoke-WebRequest -Uri "$baseUrl/api/campaigns/" `
        -Method POST `
        -Body $jsonBody `
        -Headers @{
            "X-CSRFToken" = $csrfToken
            "Content-Type" = "application/json"
            "Referer" = $baseUrl
            "Origin" = $baseUrl
        } `
        -WebSession $session `
        -UseBasicParsing `
        -ErrorAction Stop

    Write-Host "Campaign created successfully!" -ForegroundColor Green
    Write-Host "Status: $($createResponse.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($createResponse.Content)" -ForegroundColor Green
} catch {
    Write-Host "Failed to create campaign" -ForegroundColor Red
    Write-Host "Status: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Red
    
    $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
    $reader.BaseStream.Position = 0
    $reader.DiscardBufferedData()
    $responseBody = $reader.ReadToEnd()
    
    Write-Host "Response: $responseBody" -ForegroundColor Red
}

Write-Host "`nTest complete!" -ForegroundColor Cyan
