param(
    [string]$FileName
)

$cv_api = '4a6d1824adf3ac9dc351741d7dc3f7c81e99cf58'

try {get-process -Name "comictagger" -ErrorAction Stop | Stop-Process -Force}
catch {}

$cmdString = '.\comictagger\comictagger.exe --cv-api-key $cv_api -f "%file%" -o -s -t CR -w'
$cmdString = $cmdString.Replace('%file%',$FileName).Replace('-f " ','-f "').Replace(' " -o','" -o')
$cmdString

$cmdScript = [scriptblock]::Create($cmdString)

Invoke-Command -ScriptBlock $cmdScript