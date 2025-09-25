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

// Test Firestore connection
async function testFirestoreConnection() {
  try {
    console.log("🔍 Testing Firestore connection...");

    const db = admin.firestore();

    // Test write operation
    const testDoc = {
      test: true,
      message: "Firebase connection test",
      timestamp: admin.firestore.FieldValue.serverTimestamp(),
    };

    const docRef = await db.collection("_test").add(testDoc);
    console.log("✅ Firestore write test successful:", docRef.id);

    // Test read operation
    const doc = await docRef.get();
    if (doc.exists) {
      console.log("✅ Firestore read test successful:", doc.data());
    } else {
      console.log("❌ Firestore read test failed: Document not found");
    }

    // Clean up test document
    await docRef.delete();
    console.log("✅ Firestore cleanup successful");

    return true;
  } catch (error) {
    console.error("❌ Firestore test failed:", error);
    return false;
  }
}

// Test Realtime Database connection
async function testRealtimeDatabaseConnection() {
  try {
    console.log("🔍 Testing Realtime Database connection...");

    const db = admin.database();

    // Test write operation
    const testData = {
      test: true,
      message: "Realtime Database connection test",
      timestamp: admin.database.ServerValue.TIMESTAMP,
    };

    const ref = db.ref("_test/connection");
    await ref.set(testData);
    console.log("✅ Realtime Database write test successful");

    // Test read operation
    const snapshot = await ref.once("value");
    const data = snapshot.val();
    if (data && data.test) {
      console.log("✅ Realtime Database read test successful:", data);
    } else {
      console.log("❌ Realtime Database read test failed: Data not found");
    }

    // Clean up test data
    await ref.remove();
    console.log("✅ Realtime Database cleanup successful");

    return true;
  } catch (error) {
    console.error("❌ Realtime Database test failed:", error);
    return false;
  }
}

// Test Storage connection
async function testStorageConnection() {
  try {
    console.log("🔍 Testing Storage connection...");

    const bucket = admin.storage().bucket();

    // Test bucket access
    const [exists] = await bucket.exists();
    if (exists) {
      console.log("✅ Storage bucket access test successful");
      return true;
    } else {
      console.log("❌ Storage bucket access test failed: Bucket not found");
      return false;
    }
  } catch (error) {
    console.error("❌ Storage test failed:", error);
    return false;
  }
}

// Main test function
async function runAllTests() {
  try {
    console.log("🚀 Starting Firebase connection tests...");
    console.log("=" * 50);

    // Initialize Firebase
    initializeFirebase();
    console.log("");

    // Test Firestore
    const firestoreSuccess = await testFirestoreConnection();
    console.log("");

    // Test Realtime Database
    const realtimeSuccess = await testRealtimeDatabaseConnection();
    console.log("");

    // Test Storage
    const storageSuccess = await testStorageConnection();
    console.log("");

    console.log("=" * 50);
    console.log("📊 Test Results:");
    console.log(`  • Firestore: ${firestoreSuccess ? "✅ PASS" : "❌ FAIL"}`);
    console.log(
      `  • Realtime Database: ${realtimeSuccess ? "✅ PASS" : "❌ FAIL"}`
    );
    console.log(`  • Storage: ${storageSuccess ? "✅ PASS" : "❌ FAIL"}`);

    const allTestsPassed =
      firestoreSuccess && realtimeSuccess && storageSuccess;

    if (allTestsPassed) {
      console.log("");
      console.log("🎉 All Firebase connection tests passed!");
      console.log("✅ Your Firebase configuration is working correctly.");
    } else {
      console.log("");
      console.log("❌ Some Firebase connection tests failed.");
      console.log("💡 Please check your Firebase configuration and try again.");
    }
  } catch (error) {
    console.error("❌ Test execution failed:", error);
  } finally {
    process.exit(0);
  }
}

// Run tests if called directly
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

  runAllTests();
}

module.exports = {
  testFirestoreConnection,
  testRealtimeDatabaseConnection,
  testStorageConnection,
  runAllTests,
};
