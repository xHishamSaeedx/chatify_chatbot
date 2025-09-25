const admin = require("firebase-admin");
const path = require("path");

// Initialize Firebase Admin SDK
const initializeFirebase = () => {
  try {
    // Check if Firebase is already initialized
    if (admin.apps.length > 0) {
      return admin.apps[0];
    }

    // Create credentials from environment variables
    const serviceAccount = {
      type: "service_account",
      project_id: process.env.FIREBASE_PROJECT_ID,
      private_key_id: process.env.FIREBASE_PRIVATE_KEY_ID,
      private_key: process.env.FIREBASE_PRIVATE_KEY?.replace(/\\n/g, "\n"),
      client_email: process.env.FIREBASE_CLIENT_EMAIL,
      client_id: process.env.FIREBASE_CLIENT_ID,
      auth_uri:
        process.env.FIREBASE_AUTH_URI ||
        "https://accounts.google.com/o/oauth2/auth",
      token_uri:
        process.env.FIREBASE_TOKEN_URI || "https://oauth2.googleapis.com/token",
      auth_provider_x509_cert_url:
        process.env.FIREBASE_AUTH_PROVIDER_X509_CERT_URL ||
        "https://www.googleapis.com/oauth2/v1/certs",
      client_x509_cert_url: process.env.FIREBASE_CLIENT_X509_CERT_URL,
      universe_domain: process.env.FIREBASE_UNIVERSE_DOMAIN || "googleapis.com",
    };

    // Initialize Firebase Admin SDK
    const firebaseApp = admin.initializeApp({
      credential: admin.credential.cert(serviceAccount),
      databaseURL: process.env.FIREBASE_DATABASE_URL,
      storageBucket: process.env.FIREBASE_STORAGE_BUCKET,
    });

    console.log("✅ Firebase Admin SDK initialized successfully");
    return firebaseApp;
  } catch (error) {
    console.error("❌ Error initializing Firebase Admin SDK:", error);
    throw error;
  }
};

// Get Firestore database instance
const getFirestore = () => {
  const app = initializeFirebase();
  return app.firestore();
};

// Get Realtime Database instance
const getDatabase = () => {
  const app = initializeFirebase();
  return app.database();
};

// Collection schemas and initial data
const collections = {
  // Conversations collection - stores chat conversation metadata
  conversations: {
    schema: {
      id: "string", // Auto-generated document ID
      userId: "string", // User identifier
      title: "string", // Conversation title (auto-generated or user-defined)
      systemPrompt: "string", // System prompt used for this conversation
      model: "string", // AI model used (e.g., "gpt-3.5-turbo")
      temperature: "number", // Temperature setting used
      maxTokens: "number", // Max tokens setting
      messageCount: "number", // Total number of messages in conversation
      totalTokens: "number", // Total tokens used in conversation
      createdAt: "timestamp", // When conversation was created
      updatedAt: "timestamp", // Last message timestamp
      isActive: "boolean", // Whether conversation is still active
      tags: "array", // Optional tags for organization
    },
    indexes: [
      { fields: ["userId", "createdAt"] },
      { fields: ["userId", "isActive", "updatedAt"] },
      { fields: ["createdAt"] },
    ],
  },

  // Messages collection - stores individual chat messages
  messages: {
    schema: {
      id: "string", // Auto-generated document ID
      conversationId: "string", // Reference to conversation
      role: "string", // "system", "user", or "assistant"
      content: "string", // Message content
      tokens: "number", // Token count for this message
      timestamp: "timestamp", // When message was sent
      model: "string", // AI model used for this message
      temperature: "number", // Temperature used
      maxTokens: "number", // Max tokens used
      usage: "object", // Token usage details
      metadata: "object", // Additional metadata
    },
    indexes: [
      { fields: ["conversationId", "timestamp"] },
      { fields: ["role", "timestamp"] },
      { fields: ["timestamp"] },
    ],
  },

  // User sessions collection - stores user session data
  userSessions: {
    schema: {
      id: "string", // Auto-generated document ID
      userId: "string", // User identifier
      sessionId: "string", // Unique session identifier
      isActive: "boolean", // Whether session is active
      startTime: "timestamp", // Session start time
      lastActivity: "timestamp", // Last activity timestamp
      totalMessages: "number", // Total messages in session
      totalTokens: "number", // Total tokens used in session
      ipAddress: "string", // User's IP address
      userAgent: "string", // User's browser/device info
      preferences: "object", // User preferences (temperature, model, etc.)
      metadata: "object", // Additional session metadata
    },
    indexes: [
      { fields: ["userId", "isActive", "lastActivity"] },
      { fields: ["sessionId"] },
      { fields: ["lastActivity"] },
    ],
  },

  // Chat analytics collection - stores usage analytics
  chatAnalytics: {
    schema: {
      id: "string", // Auto-generated document ID
      date: "string", // Date in YYYY-MM-DD format
      totalConversations: "number", // Total conversations created
      totalMessages: "number", // Total messages sent
      totalTokens: "number", // Total tokens used
      uniqueUsers: "number", // Unique users who chatted
      averageMessagesPerConversation: "number", // Average messages per conversation
      averageTokensPerMessage: "number", // Average tokens per message
      modelUsage: "object", // Usage by model type
      hourlyStats: "object", // Hourly breakdown
      createdAt: "timestamp", // When this analytics record was created
      updatedAt: "timestamp", // Last update timestamp
    },
    indexes: [{ fields: ["date"] }, { fields: ["createdAt"] }],
  },

  // System settings collection - stores application settings
  systemSettings: {
    schema: {
      id: "string", // Auto-generated document ID
      key: "string", // Setting key
      value: "any", // Setting value
      description: "string", // Setting description
      category: "string", // Setting category
      isPublic: "boolean", // Whether setting is public
      createdAt: "timestamp", // When setting was created
      updatedAt: "timestamp", // Last update timestamp
      updatedBy: "string", // Who updated the setting
    },
    indexes: [
      { fields: ["key"] },
      { fields: ["category"] },
      { fields: ["isPublic"] },
    ],
  },

  // Chatbot templates collection - stores universal chatbot templates
  chatbotTemplates: {
    schema: {
      id: "string", // Auto-generated document ID
      name: "string", // Template name
      title: "string", // Display title
      description: "string", // Template description
      category: "string", // Template category (e.g., "customer-service", "creative", "technical")
      systemPrompt: "string", // System prompt for the chatbot
      welcomeMessage: "string", // Initial welcome message
      model: "string", // Recommended AI model (e.g., "gpt-3.5-turbo", "gpt-4")
      temperature: "number", // Recommended temperature setting
      maxTokens: "number", // Recommended max tokens
      tags: "array", // Searchable tags
      isPublic: "boolean", // Whether template is publicly available
      isDefault: "boolean", // Whether this is a default template
      usageCount: "number", // How many times this template has been used
      rating: "number", // Average user rating (1-5)
      ratingCount: "number", // Number of ratings
      author: "string", // Template author/creator
      version: "string", // Template version
      language: "string", // Primary language (e.g., "en", "es", "fr")
      industry: "string", // Target industry (e.g., "healthcare", "finance", "education")
      features: "array", // Template features (e.g., ["file-upload", "voice-input", "multi-language"])
      examples: "array", // Example conversations or use cases
      configuration: "object", // Additional configuration options
      metadata: "object", // Additional metadata
      createdAt: "timestamp", // When template was created
      updatedAt: "timestamp", // Last update timestamp
      lastUsed: "timestamp", // When template was last used
    },
    indexes: [
      { fields: ["category", "isPublic", "usageCount"] },
      { fields: ["isPublic", "isDefault"] },
      { fields: ["tags"] },
      { fields: ["language", "industry"] },
      { fields: ["author", "createdAt"] },
      { fields: ["rating", "ratingCount"] },
      { fields: ["lastUsed"] },
      { fields: ["createdAt"] },
    ],
  },
};

// Create Firestore collections with initial data
async function createFirestoreCollections() {
  const db = getFirestore();

  console.log("🔧 Creating Firestore collections...");

  for (const [collectionName, collectionConfig] of Object.entries(
    collections
  )) {
    try {
      console.log(`📝 Creating collection: ${collectionName}`);

      // Create a sample document to initialize the collection
      const sampleDoc = {
        _initialized: true,
        _createdAt: admin.firestore.FieldValue.serverTimestamp(),
        _description: `Initial document for ${collectionName} collection`,
      };

      // Add collection-specific sample data
      if (collectionName === "conversations") {
        sampleDoc.userId = "sample-user";
        sampleDoc.title = "Sample Conversation";
        sampleDoc.systemPrompt = "You are a helpful assistant.";
        sampleDoc.model = "gpt-3.5-turbo";
        sampleDoc.temperature = 0.7;
        sampleDoc.maxTokens = 1000;
        sampleDoc.messageCount = 0;
        sampleDoc.totalTokens = 0;
        sampleDoc.isActive = true;
        sampleDoc.tags = ["sample"];
      } else if (collectionName === "messages") {
        sampleDoc.conversationId = "sample-conversation";
        sampleDoc.role = "user";
        sampleDoc.content = "Hello, this is a sample message.";
        sampleDoc.tokens = 10;
        sampleDoc.model = "gpt-3.5-turbo";
        sampleDoc.temperature = 0.7;
        sampleDoc.maxTokens = 1000;
        sampleDoc.usage = {
          prompt_tokens: 10,
          completion_tokens: 0,
          total_tokens: 10,
        };
        sampleDoc.metadata = {};
      } else if (collectionName === "userSessions") {
        sampleDoc.userId = "sample-user";
        sampleDoc.sessionId = "sample-session";
        sampleDoc.isActive = true;
        sampleDoc.totalMessages = 0;
        sampleDoc.totalTokens = 0;
        sampleDoc.ipAddress = "127.0.0.1";
        sampleDoc.userAgent = "Sample User Agent";
        sampleDoc.preferences = { temperature: 0.7, model: "gpt-3.5-turbo" };
        sampleDoc.metadata = {};
      } else if (collectionName === "chatAnalytics") {
        sampleDoc.date = new Date().toISOString().split("T")[0];
        sampleDoc.totalConversations = 0;
        sampleDoc.totalMessages = 0;
        sampleDoc.totalTokens = 0;
        sampleDoc.uniqueUsers = 0;
        sampleDoc.averageMessagesPerConversation = 0;
        sampleDoc.averageTokensPerMessage = 0;
        sampleDoc.modelUsage = {};
        sampleDoc.hourlyStats = {};
      } else if (collectionName === "systemSettings") {
        sampleDoc.key = "default_model";
        sampleDoc.value = "gpt-3.5-turbo";
        sampleDoc.description = "Default AI model for chat completions";
        sampleDoc.category = "ai";
        sampleDoc.isPublic = true;
        sampleDoc.updatedBy = "system";
      } else if (collectionName === "chatbotTemplates") {
        sampleDoc.name = "general-assistant";
        sampleDoc.title = "General Assistant";
        sampleDoc.description =
          "A helpful and friendly general-purpose assistant";
        sampleDoc.category = "general";
        sampleDoc.systemPrompt =
          "You are a helpful, friendly, and knowledgeable assistant. You provide accurate information and help users with their questions and tasks.";
        sampleDoc.welcomeMessage =
          "Hello! I'm here to help you with any questions or tasks you might have. How can I assist you today?";
        sampleDoc.model = "gpt-3.5-turbo";
        sampleDoc.temperature = 0.7;
        sampleDoc.maxTokens = 1000;
        sampleDoc.tags = ["general", "helpful", "friendly", "assistant"];
        sampleDoc.isPublic = true;
        sampleDoc.isDefault = true;
        sampleDoc.usageCount = 0;
        sampleDoc.rating = 0;
        sampleDoc.ratingCount = 0;
        sampleDoc.author = "system";
        sampleDoc.version = "1.0.0";
        sampleDoc.language = "en";
        sampleDoc.industry = "general";
        sampleDoc.features = ["text-input", "conversation"];
        sampleDoc.examples = [
          "Answering general questions",
          "Helping with tasks and problem-solving",
          "Providing information and explanations",
        ];
        sampleDoc.configuration = {
          allowFileUpload: false,
          maxConversationLength: 50,
          responseStyle: "friendly",
        };
        sampleDoc.metadata = {
          templateType: "general",
          difficulty: "beginner",
        };
      }

      // Add the sample document
      const docRef = await db.collection(collectionName).add(sampleDoc);
      console.log(
        `✅ Created sample document in ${collectionName}: ${docRef.id}`
      );

      // Delete the sample document after creation
      await docRef.delete();
      console.log(`🗑️  Cleaned up sample document from ${collectionName}`);
    } catch (error) {
      console.error(`❌ Error creating collection ${collectionName}:`, error);
    }
  }

  console.log("✅ Firestore collections creation completed!");
}

// Create Realtime Database structure
async function createRealtimeDatabaseStructure() {
  const db = getDatabase();

  console.log("🔧 Creating Realtime Database structure...");

  try {
    // Create the main structure
    const structure = {
      conversations: {
        _description: "Chat conversations data",
        _createdAt: admin.database.ServerValue.TIMESTAMP,
      },
      messages: {
        _description: "Individual chat messages",
        _createdAt: admin.database.ServerValue.TIMESTAMP,
      },
      userSessions: {
        _description: "User session data",
        _createdAt: admin.database.ServerValue.TIMESTAMP,
      },
      analytics: {
        _description: "Chat analytics and usage data",
        _createdAt: admin.database.ServerValue.TIMESTAMP,
      },
      settings: {
        _description: "System settings and configuration",
        _createdAt: admin.database.ServerValue.TIMESTAMP,
      },
      templates: {
        _description: "Universal chatbot templates",
        _createdAt: admin.database.ServerValue.TIMESTAMP,
      },
      _metadata: {
        _description: "Chatify Chatbot Firebase collections",
        _version: "1.0.0",
        _createdAt: admin.database.ServerValue.TIMESTAMP,
        _collections: {
          conversations: "Chat conversation metadata and settings",
          messages: "Individual chat messages with role, content, and metadata",
          userSessions: "User session tracking and preferences",
          analytics: "Usage analytics and statistics",
          settings: "System configuration and settings",
          templates: "Universal chatbot templates for different use cases",
        },
      },
    };

    // Set the structure
    await db.ref().set(structure);
    console.log("✅ Realtime Database structure created successfully!");
  } catch (error) {
    console.error("❌ Error creating Realtime Database structure:", error);
  }
}

// Create Firebase indexes for better query performance
async function createFirestoreIndexes() {
  const db = getFirestore();

  console.log("🔧 Creating Firestore indexes...");

  for (const [collectionName, collectionConfig] of Object.entries(
    collections
  )) {
    if (collectionConfig.indexes) {
      for (const index of collectionConfig.indexes) {
        try {
          console.log(`📊 Creating index for ${collectionName}:`, index.fields);

          const indexConfig = {
            collectionGroup: collectionName,
            queryScope: "COLLECTION",
            fields: index.fields.map((field) => ({
              fieldPath: field,
              order: "ASCENDING",
            })),
          };

          // Note: Index creation is typically done via Firebase Console or CLI
          // This is just for documentation purposes
          console.log(
            `ℹ️  Index configuration for ${collectionName}:`,
            JSON.stringify(indexConfig, null, 2)
          );
        } catch (error) {
          console.error(
            `❌ Error creating index for ${collectionName}:`,
            error
          );
        }
      }
    }
  }

  console.log("✅ Firestore indexes configuration completed!");
  console.log(
    "ℹ️  Note: Actual index creation should be done via Firebase Console or CLI"
  );
}

// Main function to create all collections
async function createAllCollections() {
  try {
    console.log(
      "🚀 Starting Firebase collections creation for Chatify Chatbot..."
    );
    console.log("=" * 60);

    // Create Firestore collections
    await createFirestoreCollections();
    console.log("");

    // Create Realtime Database structure
    await createRealtimeDatabaseStructure();
    console.log("");

    // Create indexes configuration
    await createFirestoreIndexes();
    console.log("");

    console.log("=" * 60);
    console.log("🎉 Firebase collections creation completed successfully!");
    console.log("");
    console.log("📋 Created collections:");
    console.log("  • conversations - Chat conversation metadata");
    console.log("  • messages - Individual chat messages");
    console.log("  • userSessions - User session tracking");
    console.log("  • chatAnalytics - Usage analytics");
    console.log("  • systemSettings - System configuration");
    console.log("  • chatbotTemplates - Universal chatbot templates");
    console.log("");
    console.log("💡 Next steps:");
    console.log("  1. Review the created collections in Firebase Console");
    console.log("  2. Set up proper security rules for your collections");
    console.log(
      "  3. Create indexes via Firebase Console for better performance"
    );
    console.log("  4. Test your application with the new collections");
  } catch (error) {
    console.error("❌ Error creating collections:", error);
    process.exit(1);
  } finally {
    process.exit(0);
  }
}

// Run the script if called directly
if (require.main === module) {
  // Load environment variables from parent directory
  require("dotenv").config({ path: path.join(__dirname, "..", ".env") });

  // Validate required environment variables
  const requiredEnvVars = [
    "FIREBASE_PROJECT_ID",
    "FIREBASE_DATABASE_URL",
    "FIREBASE_STORAGE_BUCKET",
    "FIREBASE_CLIENT_EMAIL",
    "FIREBASE_PRIVATE_KEY",
    "FIREBASE_PRIVATE_KEY_ID",
    "FIREBASE_CLIENT_ID",
    "FIREBASE_CLIENT_X509_CERT_URL",
  ];

  const missingVars = requiredEnvVars.filter(
    (varName) => !process.env[varName]
  );

  if (missingVars.length > 0) {
    console.error("❌ Missing required environment variables:");
    missingVars.forEach((varName) => console.error(`  • ${varName}`));
    console.error("");
    console.error(
      "💡 Please ensure all Firebase environment variables are set in your .env file"
    );
    process.exit(1);
  }

  createAllCollections();
}

module.exports = {
  createAllCollections,
  createFirestoreCollections,
  createRealtimeDatabaseStructure,
  createFirestoreIndexes,
  collections,
};
