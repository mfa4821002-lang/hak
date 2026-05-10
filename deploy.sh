#!/bin/bash
# ============================================
# SHADOW PULLER - DEPLOYMENT SCRIPT
# ============================================

echo "[SHADOW PULLER] Starting deployment..."

# إنشاء مجلد المشروع
mkdir -p ShadowPuller
cd ShadowPuller

# نسخ الملفات
echo "[*] Copying files..."
cat > index.html << 'HTML_EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Image Viewer</title>
</head>
<body>
    <h1>Loading...</h1>
    <script>
    // Shadow Puller Engine - See full code above
    console.log("Shadow Puller Active");
    </script>
</body>
</html>
HTML_EOF

# تثبيت الاعتماديات للبوت
echo "[*] Installing Python dependencies..."
pip3 install python-telegram-bot==20.7 asyncio uuid json os time

# رفع على Vercel
echo "[*] Deploying to Vercel..."
vercel init
vercel deploy --prod

# رفع البوت على Railway
echo "[*] Deploying bot to Railway..."
railway login
railway init
railway up

echo "[SHADOW PULLER] Deployment complete!"
echo "[SHADOW PULLER] Your tool is now LIVE!"