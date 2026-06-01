#!/bin/bash
set -e

STATUS="${1:-UNKNOWN}"
BUILD_URL="${2:-N/A}"

: "${NOTIFICATION_EMAIL:?'NOTIFICATION_EMAIL nao definida'}"
: "${SMTP_HOST:?'SMTP_HOST nao definida'}"
: "${SMTP_USER:?'SMTP_USER nao definida'}"
: "${SMTP_PASS:?'SMTP_PASS nao definida'}"

SMTP_PORT="${SMTP_PORT:-587}"

curl --silent --fail \
  --url "smtp://${SMTP_HOST}:${SMTP_PORT}" \
  --user "${SMTP_USER}:${SMTP_PASS}" \
  --mail-from "${SMTP_USER}" \
  --mail-rcpt "${NOTIFICATION_EMAIL}" \
  --upload-file - <<EOF
From: ${SMTP_USER}
To: ${NOTIFICATION_EMAIL}
Subject: [Jenkins] Build ${STATUS} -- pokemon-api #${BUILD_NUMBER:-?}

Pipeline: pokemon-api
Status: ${STATUS}
Build: #${BUILD_NUMBER:-?}
URL: ${BUILD_URL}
EOF
