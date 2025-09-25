const path = require("path");
require("dotenv").config({ path: path.join(__dirname, "..", ".env") });

console.log("🔍 Checking environment variables...");
console.log("=" * 50);

// List of required Firebase environment variables
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

console.log("📋 Environment Variables Status:");
console.log("");

let allPresent = true;

requiredEnvVars.forEach((varName) => {
  const value = process.env[varName];
  const isPresent = !!value;
  const status = isPresent ? "✅" : "❌";

  console.log(`${status} ${varName}: ${isPresent ? "Present" : "Missing"}`);

  if (isPresent) {
    // Show first few characters for verification (but hide sensitive data)
    if (varName === "FIREBASE_PRIVATE_KEY") {
      console.log(
        `   Value: ${value.substring(0, 20)}...${value.substring(
          value.length - 20
        )}`
      );
    } else if (varName.includes("URL") || varName.includes("EMAIL")) {
      console.log(`   Value: ${value}`);
    } else {
      console.log(`   Value: ${value.substring(0, 10)}...`);
    }
  }

  if (!isPresent) {
    allPresent = false;
  }

  console.log("");
});

console.log("=" * 50);

if (allPresent) {
  console.log("🎉 All required environment variables are present!");
  console.log("✅ You can now run the Firebase setup scripts.");
} else {
  console.log("❌ Some environment variables are missing.");
  console.log("");
  console.log("💡 To fix this:");
  console.log(
    "1. Make sure you have a .env file in the chatify_chatbot directory"
  );
  console.log(
    "2. Add all the required Firebase environment variables to the .env file"
  );
  console.log(
    "3. The .env file should be in the same directory as the app folder"
  );
  console.log("");
  console.log("📝 Example .env file structure:");
  console.log("FIREBASE_PROJECT_ID=your-project-id");
  console.log(
    "FIREBASE_DATABASE_URL=https://your-project-id-default-rtdb.firebaseio.com"
  );
  console.log("FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com");
  console.log(
    "FIREBASE_CLIENT_EMAIL=your-service-account@your-project-id.iam.gserviceaccount.com"
  );
  console.log("FIREBASE_PRIVATE_KEY_ID=your-private-key-id");
  console.log(
    'FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\\nYour-Private-Key-Here\\n-----END PRIVATE KEY-----\\n"'
  );
  console.log("FIREBASE_CLIENT_ID=your-client-id");
  console.log(
    "FIREBASE_CLIENT_X509_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project-id.iam.gserviceaccount.com"
  );
}

console.log("");
console.log("🔍 Current working directory:", process.cwd());
console.log("📁 Script directory:", __dirname);
console.log("📄 Looking for .env at:", path.join(__dirname, "..", ".env"));
