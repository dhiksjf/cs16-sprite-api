#!/bin/bash

# Quick Start Script for CS 1.6 Sprite Generator API
# This script helps you get started quickly

set -e

echo "=========================================="
echo "CS 1.6 Sprite Generator API - Quick Start"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed!"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

echo "✅ Docker found"

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "⚠️  Docker Compose not found, trying docker compose..."
    if ! docker compose version &> /dev/null; then
        echo "❌ Docker Compose is not installed!"
        echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
        exit 1
    fi
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

echo "✅ Docker Compose found"
echo ""

# Create necessary directories
echo "Creating directories..."
mkdir -p outputs temp
echo "✅ Directories created"
echo ""

# Build and start
echo "Building Docker image..."
$COMPOSE_CMD build

echo ""
echo "Starting API server..."
$COMPOSE_CMD up -d

echo ""
echo "Waiting for server to start..."
sleep 5

# Check if server is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo ""
    echo "=========================================="
    echo "✅ API is running successfully!"
    echo "=========================================="
    echo ""
    echo "🌐 API URL: http://localhost:8000"
    echo "📚 Interactive Docs: http://localhost:8000/docs"
    echo "📖 Alternative Docs: http://localhost:8000/redoc"
    echo ""
    echo "📝 To view logs:"
    echo "   $COMPOSE_CMD logs -f"
    echo ""
    echo "🛑 To stop:"
    echo "   $COMPOSE_CMD down"
    echo ""
    echo "🧪 To test the API:"
    echo "   python test_api.py"
    echo ""
else
    echo ""
    echo "❌ Server failed to start!"
    echo "Check logs with: $COMPOSE_CMD logs"
    exit 1
fi
