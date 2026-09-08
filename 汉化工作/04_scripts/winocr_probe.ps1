param([Parameter(Mandatory=$true)][string]$Path)
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
[void][Windows.Media.Ocr.OcrEngine, Windows.Foundation, ContentType=WindowsRuntime]
[void][Windows.Graphics.Imaging.BitmapDecoder, Windows.Foundation, ContentType=WindowsRuntime]
[void][Windows.Storage.StorageFile, Windows.Storage, ContentType=WindowsRuntime]
[void][Windows.Storage.Streams.IRandomAccessStream, Windows.Storage, ContentType=WindowsRuntime]
function Await($Op, [Type]$T) {
  $m=[System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object { $_.Name -eq 'AsTask' -and $_.IsGenericMethod -and $_.GetParameters().Count -eq 1 } | Select-Object -First 1
  $gm=$m.MakeGenericMethod($T)
  $task=$gm.Invoke($null,@($Op))
  $task.Wait()
  return $task.Result
}
$file=Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync($Path)) ([Windows.Storage.StorageFile])
$stream=Await ($file.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
$dec=Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
$bmp=Await ($dec.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
$engine=[Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
if($null -eq $engine){throw 'No OCR engine'}
Write-Host ('LANG='+$engine.RecognizerLanguage.LanguageTag)
$res=Await ($engine.RecognizeAsync($bmp)) ([Windows.Media.Ocr.OcrResult])
foreach($line in $res.Lines){
  $words=@(); foreach($w in $line.Words){$r=$w.BoundingRect;$words += [PSCustomObject]@{text=$w.Text;x=$r.X;y=$r.Y;w=$r.Width;h=$r.Height}}
  [PSCustomObject]@{text=($words.text -join ' ');words=$words} | ConvertTo-Json -Compress -Depth 4
}
