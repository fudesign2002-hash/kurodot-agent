#!/usr/bin/env bash
TOKEN=$($HOME/google-cloud-sdk/bin/gcloud auth print-access-token 2>/dev/null)
curl -s "https://logging.googleapis.com/v2/entries:list" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"resourceNames":["projects/gen-lang-client-0803878197"],"filter":"resource.type=cloud_run_revision AND resource.labels.service_name=kurodot-agent AND severity=ERROR","orderBy":"timestamp desc","pageSize":3}' \
  | python3 -c "
import json,sys
r=json.load(sys.stdin)
entries=r.get('entries',[])
for e in entries:
  ts=e.get('timestamp','')[:19]
  msg=e.get('textPayload','') or str(e.get('jsonPayload',{}))
  print(f'[{ts}]')
  print(msg[:2000])
  print('=====')
"
