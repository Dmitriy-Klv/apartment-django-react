#!/bin/sh
set -e

BASIC_AUTH_ENABLED=$(echo "${BASIC_AUTH_ENABLED:-true}" | tr '[:upper:]' '[:lower:]')

case "$BASIC_AUTH_ENABLED" in
    true|1)
        : "${BASIC_AUTH_USER:?BASIC_AUTH_USER is required when BASIC_AUTH_ENABLED=true}"
        : "${BASIC_AUTH_PASSWORD:?BASIC_AUTH_PASSWORD is required when BASIC_AUTH_ENABLED=true}"

        htpasswd -bc /etc/nginx/.htpasswd "$BASIC_AUTH_USER" "$BASIC_AUTH_PASSWORD"

        cat > /etc/nginx/conf.d/auth_mode.conf <<EOF
auth_basic "Restricted";
auth_basic_user_file /etc/nginx/.htpasswd;
EOF
        ;;
    *)
        cat > /etc/nginx/conf.d/auth_mode.conf <<EOF
auth_basic off;
EOF
        ;;
esac
