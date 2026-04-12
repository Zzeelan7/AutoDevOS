# PowerShell script to set GitHub token for testing
# 
# Get a token from: https://github.com/settings/tokens
#   Steps:
#   1. Click "Fine-grained tokens"
#   2. Click "Generate new token"
#   3. Name: "GitHub Models"
#   4. Permissions: Account - Models (Read-only)
#   5. Repository access: All repositories
#   6. Click "Generate token" and copy
#
# Run this script:
#   .\setup_github_token.ps1
#
# Then provide your token when prompted

param(
    [string]$Token = ""
)

if (-not $Token) {
    $Token = Read-Host "Enter your GitHub Personal Access Token"
}

if ($Token) {
    $env:GITHUB_TOKEN = $Token
    Write-Host "✅ GITHUB_TOKEN set in current session"
    Write-Host "Token: $($Token.Substring(0, 20))..."
    
    # Update .env file
    $envPath = ".\.env"
    if (Test-Path $envPath) {
        $content = Get-Content $envPath -Raw
        $content = $content -replace 'GITHUB_TOKEN="[^"]*"', "GITHUB_TOKEN=`"$Token`""
        Set-Content $envPath $content
        Write-Host "✅ Updated .env file"
    }
    
    Write-Host ""
    Write-Host "✅ Ready to test! Run:"
    Write-Host "   python test_github_models.py"
} else {
    Write-Host "❌ No token provided"
    exit 1
}
