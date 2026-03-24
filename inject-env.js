const fs = require('fs');
const path = require('path');

// Target the index.html file in the frontend directory
const filePath = path.join(__dirname, 'frontend', 'index.html');
const backendUrl = process.env.BACKEND_API_URL || 'https://doodle-marathon.onrender.com';

if (fs.existsSync(filePath)) {
    let content = fs.readFileSync(filePath, 'utf8');
    
    // Replace the placeholder with the environment variable
    content = content.replace('window.BACKEND_API_URL = null;', `window.BACKEND_API_URL = "${backendUrl}";`);
    
    fs.writeFileSync(filePath, content);
    console.log(`Successfully injected Backend URL: ${backendUrl}`);
} else {
    console.error(`Error: Could not find ${filePath}`);
    process.exit(1);
}
