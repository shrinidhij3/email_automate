# Test Login Script for Email Automation Backend
# Replace these with your actual credentials
$username = "sky"
$password = "12121212"

# Base URL for the API
$baseUrl = "https://email-automate-ob1a.onrender.com"

# 1. Get CSRF Token
Write-Host "Step 1: Getting CSRF token..."
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession

try {
    $response = Invoke-WebRequest -Uri "$baseUrl/api/csrf-token/" `
        -Headers @{
            "Accept" = "application/json"
        } `
        -WebSession $session
    
    $csrfToken = ($response.Content | ConvertFrom-Json).csrfToken
    Write-Host "CSRF Token: $csrfToken"
    
    # 2. Login
    Write-Host "`nStep 2: Attempting to login..."
    $loginBody = @{
        username = $username
        password = $password
    } | ConvertTo-Json
    
    $loginResponse = Invoke-WebRequest -Uri "$baseUrl/api/auth/login/" `
        -Method POST `
        -Headers @{
            "Content-Type" = "application/json"
            "X-CSRFToken" = $csrfToken
            "Referer" = $baseUrl
        } `
        -Body $loginBody `
        -WebSession $session
    
    Write-Host "Login Response:" $loginResponse.StatusCode
    Write-Host "Response Content:" $loginResponse.Content
    
    # 3. Test protected endpoint
    Write-Host "`nStep 3: Testing protected endpoint..."
    $protectedResponse = Invoke-WebRequest -Uri "$baseUrl/api/campaigns/" `
        -Headers @{
            "Accept" = "application/json"
            "X-CSRFToken" = $csrfToken
            "Referer" = $baseUrl
        } `
        -WebSession $session
    
    Write-Host "Protected Endpoint Response:" $protectedResponse.StatusCode
    Write-Host "Response Content:" $protectedResponse.Content
    
} catch {
    Write-Host "`nError occurred:"
    Write-Host "Status Code:" $_.Exception.Response.StatusCode.value__
    Write-Host "Message:" $_.ErrorDetails.Message
    
    if ($_.Exception.Response.Headers) {
        Write-Host "Response Headers:"
        $_.Exception.Response.Headers | Format-Table -AutoSize
    }
}

Write-Host "`nTest complete. Check the output above for results."
