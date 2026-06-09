# well_client/fetch_api.py
import http.client
import json
from datetime import datetime, timedelta

REALTIME_DATA_HOST = "pdumitradome.id"
REALTIME_DATA_PATH = "/dome_api/realtime-data"

DEFAULT_PARAM = [
    "dt","md","bitdepth","blockpos","hklda","mudflowin",
    "ropi","rpm","torqa","stppress","woba","speedup","speeddown","md"
]

async def fetch_well_realtime(token: str, start_time: str, end_time: str, param=None):
    """Ambil data realtime sumur via GET body JSON (sesuai format yang berhasil di terminal)"""
    if param is None:
        param = DEFAULT_PARAM

    payload = json.dumps({
        "token": token,
        "timeStart": start_time,
        "timeEnd": end_time,
        "param": param
    })
    headers = {'Content-Type': 'application/json'}

    conn = http.client.HTTPSConnection(REALTIME_DATA_HOST)
    conn.request("GET", REALTIME_DATA_PATH, payload, headers)
    res = conn.getresponse()
    if res.status != 200:
        raise Exception(f"Fetch API failed: {res.status} {res.reason}")
    data = res.read()
    result = json.loads(data.decode()).get("result", [])
    return result

async def fetch_wells_ops(token: str = None, time_window_minutes=1):
    """Ambil semua data realtime 1 menit terakhir dari token tertentu"""
    now = datetime.utcnow()
    start_time = (now - timedelta(minutes=time_window_minutes)).strftime("%Y-%m-%d %H:%M:%S")
    end_time = now.strftime("%Y-%m-%d %H:%M:%S")
    if not token:
        raise Exception("Token required for fetch_wells_ops")
    return await fetch_well_realtime(token, start_time, end_time)