# Firebase Collections Setup for Chatify Chatbot

This directory contains a JavaScript script to create and initialize Firebase collections for the Chatify Chatbot application.

## Overview

The `create-firebase-collections.js` script creates the following Firebase collections:

### Firestore Collections

- **conversations** - Chat conversation metadata and settings
- **messages** - Individual chat messages with role, content, and metadata
- **userSessions** - User session tracking and preferences
- **chatAnalytics** - Usage analytics and statistics
- **systemSettings** - System configuration and settings
- **chatbotTemplates** - Universal chatbot templates for different use cases

### Realtime Database Structure

- **conversations** - Chat conversations data
- **messages** - Individual chat messages
- **userSessions** - User session data
- **analytics** - Chat analytics and usage data
- **settings** - System settings and configuration
- **templates** - Universal chatbot templates

## Prerequisites

1. **Node.js** (version 16 or higher)
2. **Firebase Project** with Firestore and Realtime Database enabled
3. **Firebase Service Account** credentials
4. **Environment Variables** configured

## Setup Instructions

### 1. Install Dependencies

```bash
cd app
npm install
```

### 2. Configure Environment Variables

Create a `.env` file in the `app` directory with the following Firebase credentials:

```env
# Firebase Configuration
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_DATABASE_URL=https://your-project-id-default-rtdb.firebaseio.com
FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
FIREBASE_CLIENT_EMAIL=your-service-account@your-project-id.iam.gserviceaccount.com
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYour-Private-Key-Here\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_ID=your-client-id
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
FIREBASE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
FIREBASE_CLIENT_X509_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project-id.iam.gserviceaccount.com
FIREBASE_UNIVERSE_DOMAIN=googleapis.com
```

### 3. Run the Setup Script

```bash
npm run setup-collections
```

Or run directly:

```bash
node create-firebase-collections.js
```

## Collection Schemas

### Conversations Collection

```javascript
{
  id: "string",                    // Auto-generated document ID
  userId: "string",                // User identifier
  title: "string",                 // Conversation title
  systemPrompt: "string",          // System prompt used
  model: "string",                 // AI model used
  temperature: "number",           // Temperature setting
  maxTokens: "number",             // Max tokens setting
  messageCount: "number",          // Total messages
  totalTokens: "number",           // Total tokens used
  createdAt: "timestamp",          // Creation timestamp
  updatedAt: "timestamp",          // Last update timestamp
  isActive: "boolean",             // Active status
  tags: "array"                    // Optional tags
}
```

### Messages Collection

```javascript
{
  id: "string",                    // Auto-generated document ID
  conversationId: "string",        // Reference to conversation
  role: "string",                  // "system", "user", or "assistant"
  content: "string",               // Message content
  tokens: "number",                // Token count
  timestamp: "timestamp",          // Message timestamp
  model: "string",                 // AI model used
  temperature: "number",           // Temperature used
  maxTokens: "number",             // Max tokens used
  usage: "object",                 // Token usage details
  metadata: "object"               // Additional metadata
}
```

### User Sessions Collection

```javascript
{
  id: "string",                    // Auto-generated document ID
  userId: "string",                // User identifier
  sessionId: "string",             // Unique session ID
  isActive: "boolean",             // Active status
  startTime: "timestamp",          // Session start time
  lastActivity: "timestamp",       // Last activity
  totalMessages: "number",         // Total messages
  totalTokens: "number",           // Total tokens used
  ipAddress: "string",             // User's IP address
  userAgent: "string",             // Browser/device info
  preferences: "object",           // User preferences
  metadata: "object"               // Additional metadata
}
```

### Chatbot Templates Collection

```javascript
{
  id: "string",                    // Auto-generated document ID
  name: "string",                  // Template name (unique identifier)
  title: "string",                 // Display title
  description: "string",           // Template description
  category: "string",              // Template category (e.g., "customer-service", "creative", "technical")
  systemPrompt: "string",          // System prompt for the chatbot
  welcomeMessage: "string",        // Initial welcome message
  model: "string",                 // Recommended AI model (e.g., "gpt-3.5-turbo", "gpt-4")
  temperature: "number",           // Recommended temperature setting
  maxTokens: "number",             // Recommended max tokens
  tags: "array",                   // Searchable tags
  isPublic: "boolean",             // Whether template is publicly available
  isDefault: "boolean",            // Whether this is a default template
  usageCount: "number",            // How many times this template has been used
  rating: "number",                // Average user rating (1-5)
  ratingCount: "number",           // Number of ratings
  author: "string",                // Template author/creator
  version: "string",               // Template version
  language: "string",              // Primary language (e.g., "en", "es", "fr")
  industry: "string",              // Target industry (e.g., "healthcare", "finance", "education")
  features: "array",               // Template features (e.g., ["file-upload", "voice-input", "multi-language"])
  examples: "array",               // Example conversations or use cases
  configuration: "object",         // Additional configuration options
  metadata: "object",              // Additional metadata
  createdAt: "timestamp",          // When template was created
  updatedAt: "timestamp",          // Last update timestamp
  lastUsed: "timestamp"            // When template was last used
}
```

## Security Rules

After creating the collections, make sure to set up proper Firestore security rules:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Conversations - users can only access their own
    match /conversations/{conversationId} {
      allow read, write: if request.auth != null &&
        request.auth.uid == resource.data.userId;
    }

    // Messages - users can only access messages from their conversations
    match /messages/{messageId} {
      allow read, write: if request.auth != null &&
        request.auth.uid == get(/databases/$(database)/documents/conversations/$(resource.data.conversationId)).data.userId;
    }

    // User sessions - users can only access their own sessions
    match /userSessions/{sessionId} {
      allow read, write: if request.auth != null &&
        request.auth.uid == resource.data.userId;
    }

    // Analytics - read-only for authenticated users
    match /chatAnalytics/{analyticsId} {
      allow read: if request.auth != null;
      allow write: if false; // Only server-side writes
    }

    // System settings - read-only for authenticated users
    match /systemSettings/{settingId} {
      allow read: if request.auth != null;
      allow write: if false; // Only admin writes
    }
  }
}
```

## Indexes

The script provides index configurations for optimal query performance. Create these indexes in the Firebase Console:

### Conversations Indexes

- `userId` + `createdAt`
- `userId` + `isActive` + `updatedAt`
- `createdAt`

### Messages Indexes

- `conversationId` + `timestamp`
- `role` + `timestamp`
- `timestamp`

### User Sessions Indexes

- `userId` + `isActive` + `lastActivity`
- `sessionId`
- `lastActivity`

## Testing

After running the setup script, you can test the Firebase connection:

```bash
npm run test-firebase
```

5. **Populate default templates (optional):**
   ```bash
   npm run populate-templates
   ```

## Troubleshooting

### Common Issues

1. **Authentication Error**: Ensure all Firebase environment variables are correctly set
2. **Permission Denied**: Check that your service account has proper permissions
3. **Collection Already Exists**: The script handles existing collections gracefully
4. **Network Issues**: Ensure your network can access Firebase services

### Environment Variable Issues

If you're having trouble with environment variables, you can also use a service account JSON file:

1. Download your service account JSON file from Firebase Console
2. Place it in the `app` directory as `serviceAccountKey.json`
3. Modify the script to use the JSON file instead of environment variables

## Next Steps

1. **Review Collections**: Check the created collections in Firebase Console
2. **Set Security Rules**: Implement proper security rules for your use case
3. **Create Indexes**: Set up the recommended indexes for better performance
4. **Test Integration**: Test your Python application with the new collections
5. **Monitor Usage**: Set up monitoring and alerts for your Firebase usage

## Support

For issues or questions:

1. Check the Firebase Console for any error messages
2. Review the script logs for detailed error information
3. Ensure all prerequisites are met
4. Verify your Firebase project configuration
