#!/bin/bash
set -e

echo "=========================================="
echo "5 Cypress Automation — DigitalOcean Deploy"
echo "=========================================="

# Update system
sudo apt update
sudo apt install -y nodejs npm python3 python3-pip python3-venv git nginx certbot python3-certbot-nginx

# Install PM2
sudo npm install -g pm2

# Clone repo
cd /home/jimmy
git clone https://github.com/simplysmartai/5cypressautomation.git 5cypress
cd /home/jimmy/5cypress

# Install Node dependencies
npm install --production

# Install Python dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate

# Start with PM2
pm2 start server.js --name 5cypress
pm2 save
pm2 startup

echo ""
echo "✅ Deployment complete!"
echo "Server started with PM2"
echo ""
echo "Next steps:"
echo "1. Upload .env file"
echo "2. Configure Nginx"
echo "3. Install SSL certificate"
