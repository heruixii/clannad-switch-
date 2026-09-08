$ErrorActionPreference='Stop'
$root='D:\switch游戏\个人汉化\clannad\汉化工作'
$src=Join-Path $root '03_text\switch_work\paks\FONT.PAK_unpacked'
$base=Join-Path $root '05_build\font_package'
$dst=Join-Path $base 'FONT.PAK_unpacked'
$gen=Join-Path $base 'generated_info'
$log=Join-Path $base 'font_patch_reports.jsonl'
$exe=Join-Path $root 'tools\LuckSystem\tools\slotpatch\slotpatch.exe'
$map=Join-Path $root '05_build\font_patch_plan\slot_map_v2.tsv'
$ttf='C:\Windows\Fonts\NotoSansSC-VF.ttf'
Remove-Item -LiteralPath $base -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $dst,$gen | Out-Null
Copy-Item -Path (Join-Path $src '*') -Destination $dst -Recurse -Force
Copy-Item -LiteralPath (Join-Path $root '03_text\switch_work\paks\FONT.PAK.pakhead') -Destination (Join-Path $base 'FONT.PAK.pakhead')
Set-Content -LiteralPath $log -Value '' -Encoding UTF8
$images=Get-ChildItem -LiteralPath $src -File | Where-Object {$_.Name -notlike 'info*'} | Sort-Object Name
$canon=@{}
$i=0
foreach($im in $images){
  $i++
  if($im.Name -notmatch '(\d+)(\.2)?$'){throw "No size suffix: $($im.Name)"}
  $infoName='info'+$Matches[1]+$Matches[2]
  $infoSrc=Join-Path $src $infoName
  if(-not(Test-Path $infoSrc)){throw "Missing $infoName for $($im.Name)"}
  $outImg=Join-Path $dst $im.Name
  $tmpInfo=Join-Path $gen ($im.Name+'.info')
  $rep=& $exe patch $infoSrc $im.FullName $ttf $map $outImg $tmpInfo 2>&1
  if($LASTEXITCODE -ne 0){Write-Host $rep;throw "slotpatch failed $($im.Name) exit=$LASTEXITCODE"}
  $rep | Add-Content -LiteralPath $log -Encoding UTF8
  $h=(Get-FileHash -LiteralPath $tmpInfo -Algorithm SHA256).Hash
  if($canon.ContainsKey($infoName)){
    if($canon[$infoName] -ne $h){throw "info hash mismatch $infoName from $($im.Name)"}
  } else {
    $canon[$infoName]=$h
    Copy-Item -LiteralPath $tmpInfo -Destination (Join-Path $dst $infoName) -Force
  }
  Write-Host ("PATCHED {0}/{1} {2} info={3}" -f $i,$images.Count,$im.Name,$infoName)
}
$needInfos=(Get-ChildItem -LiteralPath $src -File -Filter 'info*').Name
foreach($n in $needInfos){if(-not(Test-Path (Join-Path $dst $n))){throw "final missing info $n"}}
Write-Host ('DONE images='+$images.Count+' infos='+$needInfos.Count+' files='+((Get-ChildItem -LiteralPath $dst -File).Count))
