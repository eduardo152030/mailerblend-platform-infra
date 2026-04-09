{
  "serverRoot": "https://infra-focalboard.mailerblend.com",
  "port": 8000,
  "dbtype": "postgres",
  "dbconfig": "postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/focalboard?sslmode=disable",
  "postgres_dbconfig": "dbname=focalboard sslmode=disable",
  "useSSL": false,
  "webpath": "./pack",
  "filespath": "/opt/focalboard/data/files",
  "telemetry": false,
  "session_expire_time": 2592000,
  "session_refresh_time": 18000,
  "localOnly": false,
  "enableLocalMode": false,
  "enablePublicSharedBoards": true,
  "featureFlags": {}
}