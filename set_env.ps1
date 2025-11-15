param (
    [string]$s
)

if (-not $s) {
    Write-Host "Usage: .\set_env.ps1 -s <name>"
    exit 1
}

# مسیر فایل .env.{name}
$envFile = ".env.$s"

# بررسی وجود فایل
if (-not (Test-Path $envFile)) {
    Write-Host "Environment file $envFile not found!"
    exit 1
}

# بارگذاری متغیرهای محیطی از فایل .env.{name}
Get-Content $envFile | ForEach-Object {
    if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
        $key = $matches[1].Trim()
        $value = $matches[2].Trim()

        # تنظیم متغیر محیطی
        [System.Environment]::SetEnvironmentVariable($key, $value, [System.EnvironmentVariableTarget]::Process)
    }
}

Write-Host "Environment variables from $envFile loaded successfully."
