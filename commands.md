
(base) PS C:\Users\Yugendra\Downloads\Probe\apps\decision-probe\apps\backend> uvicorn main:app --host 0.0.0.0 --port 8005 --reload



(base) PS C:\Users\Yugendra\Downloads\Probe\apps\decision-probe\apps\frontend> cd apps/decision-probe/apps/frontend
>> npm install
>> npm run dev

---------------------------------------------------------------------------------------

(base) PS C:\Users\Yugendra\Downloads\Probe\apps\driftguard-probe\ui> cd apps/driftguard-probe/ui
>> npm install
>> npm run dev

--------------------------------------------------------------------------------------

(base) PS C:\Users\Yugendra\Downloads\Probe\packages\driftguard-sdk\dashboard> npm run dev



(base) PS C:\Users\Yugendra\Downloads\Probe\packages\driftguard-sdk> uvicorn monitoring.evidently_app:app --host 0.0.0.0 --port 8001 --reload



(base) PS C:\Users\Yugendra\Downloads\Probe\packages\driftguard-sdk> $p = netstat -ano | Select-String ":8000 " | ForEach-Object { ($_ -split '\s+')[-1] } | Select-Object -First 1
>> Stop-Process -Id $p -Force
>> uvicorn main:app --host 0.0.0.0 --port 8000 --reload


---------------------------------------------------------------------------------------