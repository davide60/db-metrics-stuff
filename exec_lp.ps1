# one off exec to set path in ananconda
#$INCLUDE = "C:\instantclient_18_5"
#$OLDPATH = [System.Environment]::GetEnvironmentVariable('PATH','machine')
#$NEWPATH = "$OLDPATH;$INCLUDE"
#[Environment]::SetEnvironmentVariable("PATH", "$NEWPATH", "Machine")
#($env:PATH).split(";")
$env:TNS_ADMIN = 'C:/tns'
$DB1 = "CARSPRD_ETL"
$DB2 = "CARSPRD_ST"
Set-Location -Path "C:\Users\david olivari\Projects\gitProjs\db-metrics-stuff"
$Server = Read-Host -Prompt 'Have you cleared the data directory for previous runs data?(Y) to continue'
if ( $server -ne 'Y' -or $server -ne 'y' )
{
    exit
}

$loops=1
Do {
    Write-Output $loops
    $loops++
    # pythonw executes in the backgroud
    pythonw.exe  resource_monitor_chart.py -t $DB1 
    pythonw.exe  resource_monitor_chart.py -t $DB2
    Start-Sleep -Second 600
    }
While ($loops -le 36)
python  resource_monitor_chart.py -t $DB1 --plot
python  resource_monitor_chart.py -t $DB2 --plot
