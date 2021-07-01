# db-metrics-stuff
This reporsitory contains utilities for database (Oracle) monitoring
## ASH Load viewer
This project uses a query (created by Yannick Jaquier ) on v$sysmetric, tied with v$active_session_history to have an hour long (now - 60)  detail om the load experienced on the database.
The map produced has similat colours as available in Oracle Enterprise Manager.
## Usage
Connections to DB made using TNS alias, also a config file is used to match alias to passwords/host
example
[TNS_ALIAS]
service  : <service name from thnsnames.ora>
host     : <hostname>
port     : 1521
password_system : XXXXXXXX

two modes:
###data collection 
pythonw.exe  resource_monitor_chart.py -t $DB1
####plotting
python  resource_monitor_chart.py -t $DB2 --plot
See powershell wrapper
