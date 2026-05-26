import os, json, redis
from dotenv import load_dotenv
load_dotenv()
r = redis.from_url(os.environ['REDIS_URL'])
print('Runs in index:', r.lrange('runs:index', 0, -1))
run = json.loads(r.get('run:20260525_231530'))
print('Timestamp:', run['timestamp'])
print('Generated:', run['generated_at'])
print('Models stored:', list(run['reports'].keys()))
