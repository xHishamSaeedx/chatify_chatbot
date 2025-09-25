const admin = require("firebase-admin");
const path = require("path");
require("dotenv").config({ path: path.join(__dirname, "..", ".env") });

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

// Default chatbot templates
const defaultTemplates = [
  {
    name: "general-assistant",
    title: "General Assistant",
    description:
      "A helpful and friendly general-purpose assistant for answering questions and helping with tasks",
    category: "general",
    systemPrompt:
      "You are a helpful, friendly, and knowledgeable assistant. You provide accurate information and help users with their questions and tasks. Be concise but thorough in your responses.",
    welcomeMessage:
      "Hello! I'm here to help you with any questions or tasks you might have. How can I assist you today?",
    model: "gpt-3.5-turbo",
    temperature: 0.7,
    maxTokens: 1000,
    tags: ["general", "helpful", "friendly", "assistant", "questions"],
    isPublic: true,
    isDefault: true,
    usageCount: 0,
    rating: 0,
    ratingCount: 0,
    author: "system",
    version: "1.0.0",
    language: "en",
    industry: "general",
    features: ["text-input", "conversation", "q-and-a"],
    examples: [
      "Answering general questions",
      "Helping with tasks and problem-solving",
      "Providing information and explanations",
      "Creative writing assistance",
    ],
    configuration: {
      allowFileUpload: false,
      maxConversationLength: 50,
      responseStyle: "friendly",
      enableMemory: true,
    },
    metadata: {
      templateType: "general",
      difficulty: "beginner",
      estimatedSetupTime: "2 minutes",
    },
  },
  {
    name: "customer-service",
    title: "Customer Service Bot",
    description:
      "Professional customer service assistant for handling inquiries, complaints, and support requests",
    category: "customer-service",
    systemPrompt:
      "You are a professional customer service representative. You are helpful, empathetic, and solution-oriented. Always maintain a polite and professional tone while working to resolve customer issues efficiently.",
    welcomeMessage:
      "Hello! I'm here to help you with any questions or concerns you may have. How can I assist you today?",
    model: "gpt-3.5-turbo",
    temperature: 0.3,
    maxTokens: 800,
    tags: ["customer-service", "support", "professional", "help", "complaints"],
    isPublic: true,
    isDefault: true,
    usageCount: 0,
    rating: 0,
    ratingCount: 0,
    author: "system",
    version: "1.0.0",
    language: "en",
    industry: "customer-service",
    features: ["text-input", "conversation", "ticket-creation", "escalation"],
    examples: [
      "Handling product inquiries",
      "Processing returns and refunds",
      "Technical support assistance",
      "Account management help",
    ],
    configuration: {
      allowFileUpload: true,
      maxConversationLength: 30,
      responseStyle: "professional",
      enableEscalation: true,
      autoTicketCreation: true,
    },
    metadata: {
      templateType: "customer-service",
      difficulty: "intermediate",
      estimatedSetupTime: "5 minutes",
    },
  },
  {
    name: "creative-writer",
    title: "Creative Writing Assistant",
    description:
      "Inspirational writing companion for creative projects, storytelling, and content creation",
    category: "creative",
    systemPrompt:
      "You are a creative writing assistant with a passion for storytelling and creative expression. You help users develop ideas, improve their writing, and overcome creative blocks. Be encouraging and imaginative in your responses.",
    welcomeMessage:
      "Welcome, creative soul! I'm here to help you bring your ideas to life. What story would you like to tell today?",
    model: "gpt-4",
    temperature: 0.9,
    maxTokens: 1500,
    tags: ["creative", "writing", "storytelling", "inspiration", "content"],
    isPublic: true,
    isDefault: true,
    usageCount: 0,
    rating: 0,
    ratingCount: 0,
    author: "system",
    version: "1.0.0",
    language: "en",
    industry: "creative",
    features: ["text-input", "conversation", "brainstorming", "editing"],
    examples: [
      "Story and character development",
      "Poetry and creative writing",
      "Blog post and article writing",
      "Marketing copy creation",
    ],
    configuration: {
      allowFileUpload: true,
      maxConversationLength: 100,
      responseStyle: "creative",
      enableBrainstorming: true,
      writingPrompts: true,
    },
    metadata: {
      templateType: "creative",
      difficulty: "beginner",
      estimatedSetupTime: "3 minutes",
    },
  },
  {
    name: "technical-expert",
    title: "Technical Expert",
    description:
      "Specialized technical assistant for programming, troubleshooting, and technical problem-solving",
    category: "technical",
    systemPrompt:
      "You are a technical expert with deep knowledge in programming, software development, and technical problem-solving. Provide accurate, detailed technical guidance and code examples when appropriate.",
    welcomeMessage:
      "Hello! I'm here to help with your technical questions and challenges. What technical problem can I help you solve today?",
    model: "gpt-4",
    temperature: 0.2,
    maxTokens: 2000,
    tags: ["technical", "programming", "debugging", "code", "development"],
    isPublic: true,
    isDefault: true,
    usageCount: 0,
    rating: 0,
    ratingCount: 0,
    author: "system",
    version: "1.0.0",
    language: "en",
    industry: "technology",
    features: ["text-input", "conversation", "code-generation", "debugging"],
    examples: [
      "Programming help and code review",
      "Debugging and troubleshooting",
      "Architecture and design guidance",
      "Technical documentation",
    ],
    configuration: {
      allowFileUpload: true,
      maxConversationLength: 75,
      responseStyle: "technical",
      enableCodeExecution: false,
      syntaxHighlighting: true,
    },
    metadata: {
      templateType: "technical",
      difficulty: "advanced",
      estimatedSetupTime: "4 minutes",
    },
  },
  {
    name: "educational-tutor",
    title: "Educational Tutor",
    description:
      "Patient and knowledgeable tutor for learning, homework help, and educational support",
    category: "education",
    systemPrompt:
      "You are a patient and knowledgeable educational tutor. You help students learn by explaining concepts clearly, providing examples, and encouraging questions. Adapt your explanations to the student's level.",
    welcomeMessage:
      "Hello! I'm here to help you learn and understand new concepts. What subject or topic would you like to explore today?",
    model: "gpt-3.5-turbo",
    temperature: 0.5,
    maxTokens: 1200,
    tags: ["education", "tutoring", "learning", "homework", "academic"],
    isPublic: true,
    isDefault: true,
    usageCount: 0,
    rating: 0,
    ratingCount: 0,
    author: "system",
    version: "1.0.0",
    language: "en",
    industry: "education",
    features: ["text-input", "conversation", "step-by-step", "examples"],
    examples: [
      "Math problem solving",
      "Science concept explanations",
      "Language learning support",
      "Study strategies and tips",
    ],
    configuration: {
      allowFileUpload: true,
      maxConversationLength: 60,
      responseStyle: "educational",
      enableStepByStep: true,
      adaptiveLearning: true,
    },
    metadata: {
      templateType: "educational",
      difficulty: "intermediate",
      estimatedSetupTime: "3 minutes",
    },
  },
  {
    name: "business-consultant",
    title: "Business Consultant",
    description:
      "Strategic business advisor for planning, analysis, and decision-making support",
    category: "business",
    systemPrompt:
      "You are an experienced business consultant with expertise in strategy, operations, and business development. Provide practical, actionable advice while considering business context and constraints.",
    welcomeMessage:
      "Hello! I'm here to help you with your business challenges and opportunities. What business question can I help you address today?",
    model: "gpt-4",
    temperature: 0.4,
    maxTokens: 1500,
    tags: ["business", "consulting", "strategy", "planning", "analysis"],
    isPublic: true,
    isDefault: true,
    usageCount: 0,
    rating: 0,
    ratingCount: 0,
    author: "system",
    version: "1.0.0",
    language: "en",
    industry: "business",
    features: ["text-input", "conversation", "analysis", "planning"],
    examples: [
      "Business strategy development",
      "Market analysis and research",
      "Financial planning and budgeting",
      "Operational efficiency improvements",
    ],
    configuration: {
      allowFileUpload: true,
      maxConversationLength: 40,
      responseStyle: "professional",
      enableAnalysis: true,
      businessFrameworks: true,
    },
    metadata: {
      templateType: "business",
      difficulty: "advanced",
      estimatedSetupTime: "5 minutes",
    },
  },
];

// Populate chatbot templates collection
async function populateTemplates() {
  try {
    console.log("🚀 Starting chatbot templates population...");
    console.log("=" * 60);

    // Initialize Firebase
    initializeFirebase();
    const db = admin.firestore();

    console.log("📝 Adding default chatbot templates...");
    console.log("");

    let addedCount = 0;
    let skippedCount = 0;

    for (const template of defaultTemplates) {
      try {
        // Check if template already exists
        const existingQuery = await db
          .collection("chatbotTemplates")
          .where("name", "==", template.name)
          .limit(1)
          .get();

        if (!existingQuery.empty) {
          console.log(`⏭️  Skipping ${template.name} - already exists`);
          skippedCount++;
          continue;
        }

        // Add timestamps
        const templateWithTimestamps = {
          ...template,
          createdAt: admin.firestore.FieldValue.serverTimestamp(),
          updatedAt: admin.firestore.FieldValue.serverTimestamp(),
          lastUsed: null,
        };

        // Add the template
        const docRef = await db
          .collection("chatbotTemplates")
          .add(templateWithTimestamps);

        console.log(`✅ Added template: ${template.title} (${docRef.id})`);
        addedCount++;
      } catch (error) {
        console.error(`❌ Error adding template ${template.name}:`, error);
      }
    }

    console.log("");
    console.log("=" * 60);
    console.log("🎉 Chatbot templates population completed!");
    console.log("");
    console.log("📊 Summary:");
    console.log(`  • Templates added: ${addedCount}`);
    console.log(`  • Templates skipped: ${skippedCount}`);
    console.log(`  • Total templates: ${defaultTemplates.length}`);
    console.log("");
    console.log("📋 Available templates:");
    defaultTemplates.forEach((template) => {
      console.log(`  • ${template.title} (${template.category})`);
    });
    console.log("");
    console.log("💡 Next steps:");
    console.log("  1. Review templates in Firebase Console");
    console.log("  2. Customize templates for your specific needs");
    console.log("  3. Test templates with your chatbot application");
    console.log("  4. Add more specialized templates as needed");
  } catch (error) {
    console.error("❌ Error populating templates:", error);
    process.exit(1);
  } finally {
    process.exit(0);
  }
}

// Run the script if called directly
if (require.main === module) {
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

  populateTemplates();
}

module.exports = {
  populateTemplates,
  defaultTemplates,
};
