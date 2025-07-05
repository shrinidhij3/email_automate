# Navigate to repository
Set-Location -Path "c:\Users\Thorsignia System 1\Documents\Shrinidhi\n8n"

# Initialize git-filter-repo if needed
if (!(Test-Path .git\filter-repo)) {
    git filter-repo --force
}

# Create a temporary file for patterns
$patternsFile = "gitignore_patterns.txt"
"" | Out-File -FilePath $patternsFile -Encoding utf8

# Process each line in .gitignore
Get-Content .gitignore | ForEach-Object {
    $pattern = $_.Trim()
    # Skip comments and empty lines
    if ($pattern -and !$pattern.StartsWith('#')) {
        # Remove leading slashes for git-filter-repo
        $pattern = $pattern.TrimStart('/')
        # Escape special regex characters
        $escapedPattern = [regex]::Escape($pattern)
        # Replace * with .* for regex
        $escapedPattern = $escapedPattern -replace '\\\*', '.*'
        # Add to patterns file
        "^$escapedPattern$" | Out-File -FilePath $patternsFile -Append -Encoding utf8
    }
}

# Remove all files matching the patterns from history
git filter-repo --invert-paths --path-regex "$(Get-Content $patternsFile -Raw)" --force

# Clean up
try {
    Remove-Item -Path $patternsFile -Force -ErrorAction Stop
} catch {
    Write-Warning "Could not remove temporary file: $_"
}

# Force push the changes
git push origin --force --all
git push origin --force --tags

Write-Host "Cleanup complete. All files listed in .gitignore have been removed from Git history."
