#!/bin/bash
set -e

echo "Starting Vouch application..."

# Wait for MongoDB to be ready
echo "Waiting for MongoDB..."
until curl -s mongodb:27017 > /dev/null 2>&1; do
    echo "MongoDB is unavailable - sleeping"
    sleep 2
done
echo "MongoDB is up!"

# Wait for Elasticsearch to be ready
echo "Waiting for Elasticsearch..."
until curl -s http://elasticsearch:9200/_cluster/health > /dev/null 2>&1; do
    echo "Elasticsearch is unavailable - sleeping"
    sleep 2
done
echo "Elasticsearch is up!"

# Wait for Ollama to be ready
echo "Waiting for Ollama..."
until curl -s http://ollama:11434/api/tags > /dev/null 2>&1; do
    echo "Ollama is unavailable - sleeping"
    sleep 2
done
echo "Ollama is up!"

# Check if llama3.2-vision model is available
echo "Checking for llama3.2-vision model..."
MODEL_CHECK=$(curl -s http://ollama:11434/api/tags | grep -c "llama3.2-vision" || echo "0")
if [ "$MODEL_CHECK" -eq "0" ]; then
    echo "WARNING: llama3.2-vision model not found. The model should be pulled in the ollama service."
    echo "Receipt analysis will not work until the model is available."
else
    echo "llama3.2-vision model is available!"
fi

echo "All services are ready! Starting application..."

# Execute the main command
exec "$@"
