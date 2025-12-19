#!/bin/bash

# Script to create .env file from Firebase credentials JSON

FIREBASE_JSON_FILE="app/data/portal-11326-firebase-adminsdk-fbsvc-2cd1059886.json"

if [ ! -f "$FIREBASE_JSON_FILE" ]; then
    echo "Error: Firebase credentials file not found at $FIREBASE_JSON_FILE"
    exit 1
fi

# Read the JSON file and create .env
echo "Creating .env file..."

# Minify JSON (remove newlines and extra spaces)
FIREBASE_CREDS=$(cat "$FIREBASE_JSON_FILE" | tr -d '\n' | tr -s ' ')

# Create .env file
cat > .env << EOF
# Firebase Credentials (loaded from JSON)
FIREBASE_CREDENTIALS_JSON='$FIREBASE_CREDS'

# API Configuration
SECRET_KEY=your-secret-key-change-in-production
EOF

echo "✅ .env file created successfully!"
echo ""
echo "The Firebase credentials have been loaded into .env"
echo "You can now safely commit your code without the JSON file."
echo ""
echo "To use the .env file, the backend will automatically load it on startup."
