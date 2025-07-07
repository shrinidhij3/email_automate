# Script to test getting campaigns from the API

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
Write-Host "`nStep 3: Getting all campaigns..." -ForegroundColor Cyan
$campaignsResponse = Invoke-ApiRequest -Uri "$baseUrl/api/campaigns/" -Session $session

if (-not $campaignsResponse.Success) {
    Write-Host "Failed to get campaigns" -ForegroundColor Red
    Write-Host "Status: $($campaignsResponse.StatusCode)" -ForegroundColor Red
    Write-Host "Error: $($campaignsResponse.Error)" -ForegroundColor Red
    exit 1
}

# Display the campaigns in a formatted table
$campaigns = $campaignsResponse.Content
Write-Host "`nCampaigns retrieved successfully" -ForegroundColor Green
Write-Host "Total campaigns: $($campaigns.Count)" -ForegroundColor Green

# Format and display the campaigns
$campaigns | Format-Table -Property id, name, subject, created_by -AutoSize

# 4. Get a specific campaign (if any exist)
if ($campaigns.Count -gt 0) {
    $campaignId = $campaigns[0].id
    Write-Host "`nStep 4: Getting details for campaign ID: $campaignId" -ForegroundColor Cyan
    
    $campaignResponse = Invoke-ApiRequest -Uri "$baseUrl/api/campaigns/$campaignId/" -Session $session
    
    if ($campaignResponse.Success) {
        Write-Host "`nCampaign details:" -ForegroundColor Green
        $campaignResponse.Content | ConvertTo-Json -Depth 5 | ConvertFrom-Json | Format-List *
    } else {
        Write-Host "Failed to get campaign details" -ForegroundColor Red
        Write-Host "Status: $($campaignResponse.StatusCode)" -ForegroundColor Red
        Write-Host "Error: $($campaignResponse.Error)" -ForegroundColor Red
    }
}

Write-Host "`nTest complete!" -ForegroundColor Cyan
