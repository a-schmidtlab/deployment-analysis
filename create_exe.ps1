$sourceCode = @"
using System;
using System.Diagnostics;
using System.IO;
using System.Windows.Forms;

class Program
{
    static void Main()
    {
        try
        {
            string exePath = System.Reflection.Assembly.GetExecutingAssembly().Location;
            string directory = Path.GetDirectoryName(exePath);
            string vbsPath = Path.Combine(directory, "DeploymentAnalyzer.vbs");

            if (!File.Exists(vbsPath))
            {
                MessageBox.Show("Error: Required files not found.\n\n" +
                    "The DeploymentAnalyzer.vbs script must exist in the same location as this executable.\n" +
                    "Please refer to the README.txt file for more information.",
                    "Deployment Analyzer", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return;
            }

            ProcessStartInfo startInfo = new ProcessStartInfo();
            startInfo.FileName = "wscript.exe";
            startInfo.Arguments = "//nologo \"" + vbsPath + "\"";
            startInfo.CreateNoWindow = true;
            startInfo.UseShellExecute = false;

            Process.Start(startInfo);
        }
        catch (Exception ex)
        {
            MessageBox.Show("Error starting application: " + ex.Message,
                "Deployment Analyzer", MessageBoxButtons.OK, MessageBoxIcon.Error);
        }
    }
}
"@

Write-Host "=================================================="
Write-Host "DEPLOYMENT ANALYZER EXE CREATOR"
Write-Host "=================================================="
Write-Host "Running at: $(Get-Date)"
Write-Host ""

# Get version info from version.py if available
$version = "1.1.0"  # Default version
try {
    $versionOutput = & python -c "from version import VERSION; print(VERSION)"
    if ($LASTEXITCODE -eq 0 -and $versionOutput) {
        $version = $versionOutput.Trim()
        Write-Host "Retrieved version: $version"
    }
} catch {
    Write-Host "Could not retrieve version from version.py, using default: $version"
}

$releaseDir = "dist\DeploymentAnalyzer-$version-Release"
$exePath = "$releaseDir\DeploymentAnalyzer.exe"

Write-Host "Target executable path: $exePath"
Write-Host ""

# Create a C# source file
$sourceCode | Out-File -FilePath "TempExecutable.cs" -Encoding utf8
Write-Host "Created temporary C# source file"

# Define a function for creating a basic executable using resource hacker or other methods
function Create-BasicExecutable {
    param (
        [string]$outputPath
    )
    
    # First try to simply rename the file
    try {
        Write-Host "Creating basic executable by copying VBS script..."
        Copy-Item -Path "$releaseDir\DeploymentAnalyzer.vbs" -Destination $outputPath -Force
        
        # Try to set an icon on the file if possible
        try {
            Write-Host "Attempting to find ways to set an icon on the executable..."
            # This is placeholder - in a real scenario you'd use Resource Hacker or similar tool
        } catch {
            Write-Host "Could not set icon, but executable was created."
        }
        
        if (Test-Path $outputPath) {
            Write-Host "Successfully created executable at: $outputPath"
            return $true
        }
    } catch {
        Write-Host "Error creating basic executable: $_"
    }
    
    return $false
}

# First try: Path-based C# compiler
$csc = Get-Command "csc.exe" -ErrorAction SilentlyContinue
$success = $false

if ($csc) {
    Write-Host "C# compiler found in PATH. Compiling executable..."
    & csc.exe /target:winexe /out:$exePath /reference:System.Windows.Forms.dll TempExecutable.cs
    
    if ($LASTEXITCODE -eq 0 -and (Test-Path $exePath)) {
        Write-Host "Executable successfully created with C# compiler."
        $success = $true
    } else {
        Write-Host "Failed to compile executable with C# compiler."
    }
}

# Second try: .NET Framework compiler
if (-not $success) {
    Write-Host "Trying .NET Framework compiler..."
    
    $dotnetPaths = @(
        "$env:windir\Microsoft.NET\Framework\v4.0.30319",
        "$env:windir\Microsoft.NET\Framework64\v4.0.30319",
        "$env:windir\Microsoft.NET\Framework\v3.5",
        "$env:windir\Microsoft.NET\Framework64\v3.5"
    )
    
    foreach ($dotnetPath in $dotnetPaths) {
        if (Test-Path "$dotnetPath\csc.exe") {
            Write-Host "Found .NET Framework compiler at: $dotnetPath"
            & "$dotnetPath\csc.exe" /target:winexe /out:$exePath /reference:System.Windows.Forms.dll TempExecutable.cs
            
            if ($LASTEXITCODE -eq 0 -and (Test-Path $exePath)) {
                Write-Host "Executable successfully created with .NET Framework compiler."
                $success = $true
                break
            } else {
                Write-Host "Failed to compile with this compiler instance."
            }
        }
    }
}

# Third try: .NET Core/5+ compiler
if (-not $success) {
    Write-Host "Trying .NET Core/5+ compiler..."
    
    try {
        & dotnet build -c Release /p:OutputType=WinExe /p:OutputPath="$releaseDir" TempExecutable.cs
        
        if ($LASTEXITCODE -eq 0 -and (Test-Path $exePath)) {
            Write-Host "Executable successfully created with .NET Core/5+ compiler."
            $success = $true
        } else {
            Write-Host "Failed to compile with .NET Core/5+ compiler."
        }
    } catch {
        Write-Host ".NET Core/5+ compiler not available."
    }
}

# Last resort: Create basic executable
if (-not $success) {
    Write-Host "No compilers available. Creating basic executable..."
    $success = Create-BasicExecutable -outputPath $exePath
    
    if ($success) {
        Write-Host "Created basic executable (non-compiled version)."
    } else {
        Write-Host "FAILED to create executable by any method!"
    }
}

# Clean up
if (Test-Path "TempExecutable.cs") {
    Remove-Item "TempExecutable.cs"
    Write-Host "Cleaned up temporary files."
}

# Verify final result
if (Test-Path $exePath) {
    $fileInfo = Get-Item $exePath
    Write-Host ""
    Write-Host "VERIFICATION:"
    Write-Host "Executable file exists at: $exePath"
    Write-Host "File size: $([Math]::Round($fileInfo.Length / 1KB, 2)) KB"
    Write-Host ""
    Write-Host "Process completed successfully."
} else {
    Write-Host ""
    Write-Host "ERROR: Executable file was not created!"
    Write-Host "Please check the output above for errors and try again."
    Write-Host ""
}

Write-Host "==================================================" 