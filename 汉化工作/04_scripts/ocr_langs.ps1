Add-Type -AssemblyName System.Runtime.WindowsRuntime
[void][Windows.Media.Ocr.OcrEngine, Windows.Foundation, ContentType=WindowsRuntime]
[void][Windows.Globalization.Language, Windows.Foundation, ContentType=WindowsRuntime]
foreach($l in [Windows.Media.Ocr.OcrEngine]::AvailableRecognizerLanguages){ Write-Output $l.LanguageTag }
