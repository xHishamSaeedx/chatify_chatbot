#!/usr/bin/env bash

echo "Starting Chatify Chatbot on port $PORT"
echo "Environment: $ENVIRONMENT"
echo "Host: $HOST"
echo "Redis URL: ${REDIS_URL:+Set}"

# Test if Redis URL is set
if [ -z "$REDIS_URL" ]; then
    echo "⚠️ WARNING: REDIS_URL not set, using fallback storage"
else
    echo "✅ Redis URL configured"
fi

python render_start_fixed.py

