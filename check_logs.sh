#!/usr/bin/env bash
TOKEN=$($HOME/google-cloud-sdk/bin/gcloud auth print-access-token 2>/dev/null)
curl -s "https://logging.googleapis.com/v2/entries:list" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"resourceNames":["projects/gen-lang-client-0803878197"],"filter":"resource.type=cloud_run_revision AND resource.labels.service_name=kurodot-agent","orderBy":"timestamp desc","pageSize":10}' \
  | python3 -c "
import json,sys
r=json.load(sys.stdin)
entries=r.get('entries',[])
print(f'Found {len(entries)} entries')
for e in entries:
  ts=e.get('timestamp','')[:19]
  sev=e.get('severity','INFO')
  msg=e.get('textPayload','') or str(e.get('jsonPayload',{}))
  print(f'[{ts}] [{sev}] {msg[:400]}')
  print('---')
"
