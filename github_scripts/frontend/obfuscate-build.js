const JavaScriptObfuscator = require('javascript-obfuscator');
const fs = require('fs');
const path = require('path');

// Configuration for production obfuscation
const obfuscationConfig = {
    compact: true,
    controlFlowFlattening: true,
    controlFlowFlatteningThreshold: 0.75,
    deadCodeInjection: true,
    deadCodeInjectionThreshold: 0.4,
    debugProtection: false,
    disableConsoleOutput: true,
    identifierNamesGenerator: 'hexadecimal',
    log: false,
    renameGlobals: false,
    rotateStringArray: true,
    selfDefending: true,
    stringArray: true,
    stringArrayThreshold: 0.75,
    transformObjectKeys: true,
    unicodeEscapeSequence: false
};

function obfuscateFile(filePath) {
    const code = fs.readFileSync(filePath, 'utf8');
    const obfuscatedCode = JavaScriptObfuscator.obfuscate(code, obfuscationConfig).getObfuscatedCode();
    fs.writeFileSync(filePath, obfuscatedCode);
    console.log(`✅ Obfuscated: ${filePath}`);
}

function obfuscateDirectory(dir) {
    const files = fs.readdirSync(dir);
    
    files.forEach(file => {
        const filePath = path.join(dir, file);
        const stat = fs.statSync(filePath);
        
        if (stat.isDirectory()) {
            obfuscateDirectory(filePath);
        } else if (file.endsWith('.js') && !file.includes('.map')) {
            obfuscateFile(filePath);
        }
    });
}

// Obfuscate build directory
const buildDir = path.join(__dirname, 'build', 'static', 'js');

if (fs.existsSync(buildDir)) {
    console.log('🔒 Starting frontend obfuscation...');
    obfuscateDirectory(buildDir);
    console.log('✅ Frontend obfuscation complete!');
} else {
    console.error('❌ Build directory not found. Run yarn build first.');
}
