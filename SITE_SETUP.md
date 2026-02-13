# Simply Smart Automation - Local Demo Site

Your professional business website with an integrated dashboard and sales form.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Start the Server
```bash
npm start
```

You'll see:
```
╔════════════════════════════════════════════╗
║   Simply Smart Automation - Local Demo     ║
╠════════════════════════════════════════════╣
║                                            ║
║  🚀 Server running on http://localhost:3000    ║
║                                            ║
║  📊 Dashboard: http://localhost:3000/dashboard ║
║  📋 Form: http://localhost:3000/form         ║
║                                            ║
║  Use Ctrl+C to stop the server             ║
║                                            ║
╚════════════════════════════════════════════╝
```

### 3. Open in Browser

- **Homepage:** http://localhost:3000
- **Dashboard:** http://localhost:3000/dashboard
- **Sales Form:** http://localhost:3000/form

---

## 📁 Project Structure

```
.
├── server.js                 # Express server
├── package.json             # Dependencies
├── public/
│   ├── index.html          # Landing page
│   ├── dashboard.html      # Business dashboard
│   ├── form.html           # Sales intake form
│   └── styles.css          # All styles
└── README.md               # This file
```

---

## 📊 What You Get

### Landing Page (`/`)
- Professional business site overview
- Call-to-action buttons
- Service descriptions
- Navigation to dashboard and form

### Dashboard (`/dashboard`)
**Real-time business metrics:**
- Active clients count
- Open proposals
- Pipeline value ($)
- Orders this week
- Recent orders table
- Active clients & deal values
- Quick action buttons

**Features:**
- Auto-refreshes every 30 seconds
- Shows order status (pending, invoiced, shipped)
- Color-coded order types (New, Renewal, Upsell)
- Client status and next actions

### Sales Form (`/form`)
**The actual intake form with fields:**
- Customer Name (required)
- Customer Email (required)
- Date (defaults to today)
- Sales Rep dropdown (Doc, Other guy)
- Order Type dropdown (New, Renewal, Upsell)
- Product Name dropdown (Laser 1/2, Mini Laser 1/2)
- Quantity (required)
- Sub-product option (Yes/No)
- Notes (optional)

**On Submit:**
1. Validates all required fields
2. Posts to `/api/orders`
3. Shows success confirmation
4. Displays generated IDs:
   - Invoice ID (QBO)
   - Shipment ID (ShipStation)
5. Lists what automation executed

---

## 🔌 API Endpoints

### Get Dashboard Data
```bash
GET /api/dashboard
```

Returns:
```json
{
  "summary": {
    "activeClients": 2,
    "proposals": 1,
    "pipelineValue": 28000,
    "thisWeekOrders": 2,
    "todayOrders": 0
  },
  "recentOrders": [...],
  "clients": [...]
}
```

### Get All Orders
```bash
GET /api/orders
```

### Submit New Order
```bash
POST /api/orders
Content-Type: application/json

{
  "customerName": "Tech Corp",
  "customerEmail": "john@techcorp.com",
  "date": "2026-01-21",
  "salesRep": "Doc",
  "orderType": "New",
  "productName": "Laser 1",
  "quantity": 2
}
```

Returns:
```json
{
  "success": true,
  "order": {...},
  "automation": {
    "qboInvoice": "Created invoice INV-...",
    "shipstationOrder": "Created shipment SHIP-...",
    "emailSent": "Confirmation sent to john@techcorp.com"
  }
}
```

---

## 🎨 Design Features

- **Professional gradient** theme (blue)
- **Responsive** design (mobile-friendly)
- **Real-time updates** on dashboard
- **Color-coded** statuses and badges
- **Smooth animations** and transitions
- **Accessible** form inputs

---

## 🚀 Next Steps

### To Deploy This Live:

**Option 1: Vercel (Easiest)**
```bash
npm install -g vercel
vercel
```

**Option 2: Heroku**
```bash
npm install -g heroku
heroku login
heroku create
git push heroku main
```

**Option 3: DigitalOcean Droplet ($5/mo)**
1. Create Ubuntu droplet
2. Install Node.js
3. Clone your repo
4. `npm install && npm start`
5. Use PM2 to keep it running

**Option 4: Self-host on your VPS**
- Point domain to your server
- Run behind Nginx reverse proxy
- Use SSL certificate (Let's Encrypt)

---

## 🔧 Customization

### Change Colors
Edit `public/styles.css` - modify the `:root` variables at the top:
```css
:root {
  --primary: #0066cc;      /* Main blue */
  --primary-dark: #0052a3; /* Darker blue */
  /* ... etc */
}
```

### Add Product Pricing
Edit `server.js` - add pricing to the order creation:
```javascript
const productPricing = {
  'Laser 1': 5000,
  'Laser 2': 7500,
  'Mini Laser 1': 2000,
  'Mini Laser 2': 3000
};
```

### Add Sales Reps
Edit `public/form.html` - update the sales rep dropdown:
```html
<option value="Doc">Doc</option>
<option value="Your Name">Your Name</option>
```

---

## 📞 Support

Questions? Review the code in:
- **Frontend:** `public/form.html`, `public/dashboard.html`
- **Backend:** `server.js`
- **Styles:** `public/styles.css`

Everything is commented and straightforward.

---

## 📜 License

MIT - Use freely, modify as needed.

---

**Simply Smart Automation**  
Built to scale, designed for humans.
