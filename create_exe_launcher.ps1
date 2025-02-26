# PowerShell Script to Create a Small .EXE Launcher for DeploymentAnalyzer
# This creates a proper Windows executable that launches our application

Write-Host "Creating DeploymentAnalyzer.exe launcher..." -ForegroundColor Green

# Define the release directory
$releaseDir = "dist\DeploymentAnalyzer-Release"

# Define the path for our temporary C# source file
$csharpSourcePath = ".\TempLauncher.cs"

# Define the output executable path
$outputExePath = "$releaseDir\DeploymentAnalyzer.exe"

# Check if the release directory exists
if (-not (Test-Path $releaseDir)) {
    Write-Host "Error: Release directory '$releaseDir' not found." -ForegroundColor Red
    exit 1
}

# Create C# source code for the launcher
$sourceCode = @"
using System;
using System.Diagnostics;
using System.IO;
using System.Windows.Forms;

namespace DeploymentAnalyzerLauncher
{
    class Program
    {
        [STAThread]
        static void Main()
        {
            try
            {
                string exePath = System.Reflection.Assembly.GetExecutingAssembly().Location;
                string appDir = Path.GetDirectoryName(exePath);
                string vbsPath = Path.Combine(appDir, "DeploymentAnalyzer.vbs");

                if (!File.Exists(vbsPath))
                {
                    MessageBox.Show(
                        "Error: Required files not found.\n\n" +
                        "The .app folder must exist in the same location as this executable.\n" +
                        "Please refer to the README.txt file for more information.",
                        "Deployment Analyzer",
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Error
                    );
                    return;
                }

                ProcessStartInfo startInfo = new ProcessStartInfo("cscript");
                startInfo.Arguments = "//nologo \"" + vbsPath + "\"";
                startInfo.WindowStyle = ProcessWindowStyle.Hidden;
                Process.Start(startInfo);
            }
            catch (Exception ex)
            {
                MessageBox.Show(
                    "Error launching application: " + ex.Message,
                    "Deployment Analyzer",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error
                );
            }
        }
    }
}
"@

# Write the C# source code to a temporary file
Write-Host "Creating temporary C# source file..." -ForegroundColor Yellow
$sourceCode | Out-File -FilePath $csharpSourcePath -Encoding utf8

try {
    # Compile the C# code
    Write-Host "Compiling executable launcher..." -ForegroundColor Yellow
    Add-Type -OutputAssembly $outputExePath -OutputType WindowsApplication -TypeDefinition $sourceCode -ReferencedAssemblies System.Windows.Forms

    # Check if the compilation was successful
    if (Test-Path $outputExePath) {
        Write-Host "Successfully created executable launcher at: $outputExePath" -ForegroundColor Green
        
        # Remove the old .bat launcher if it exists
        $batLauncher = "$releaseDir\DeploymentAnalyzer.bat"
        if (Test-Path $batLauncher) {
            Remove-Item $batLauncher -Force
            Write-Host "Removed old .bat launcher" -ForegroundColor Yellow
        }
    } else {
        Write-Host "Failed to create executable launcher" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "Error during compilation: $_" -ForegroundColor Red
    exit 1
} finally {
    # Clean up temporary files
    if (Test-Path $csharpSourcePath) {
        Remove-Item $csharpSourcePath -Force
        Write-Host "Cleaned up temporary files" -ForegroundColor Gray
    }
}

Write-Host "Executable launcher creation completed!" -ForegroundColor Green 