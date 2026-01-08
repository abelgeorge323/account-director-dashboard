# Vanilla JavaScript Dashboard - Deployment Guide

## 📋 Overview

Your Account Director Performance Dashboard is now a pure vanilla JavaScript application with no framework dependencies. This makes it incredibly easy to deploy and customize.

## 🏗️ Project Structure

```
Account-Directors/
├── index.html          # Main SPA file with embedded CSS
├── app.js              # All JavaScript logic
├── data.json           # Pre-built data (generated from CSV)
├── build_data.py       # Python script to rebuild data.json
├── data/
│   ├── performance_reviews.csv
│   └── verticals.csv
└── VANILLA_JS_DEPLOYMENT.md (this file)
```

## 🔄 Updating Data

Whenever you update the CSV files:

```bash
python build_data.py
```

This regenerates `data.json` with the latest data.

## 🚀 Deployment Options

### Option 1: Netlify (Recommended - Easiest!)

1. **Push to GitHub:**
   ```bash
   git add index.html app.js data.json
   git commit -m "Add vanilla JS dashboard"
   git push origin main
   ```

2. **Deploy on Netlify:**
   - Go to [netlify.com](https://www.netlify.com/)
   - Click "Add new site" → "Import from Git"
   - Select your GitHub repository
   - Build settings:
     - Build command: `python build_data.py` (optional)
     - Publish directory: `/` (root)
   - Click "Deploy site"

3. **✅ Done!** Your site will be live at `https://your-site-name.netlify.app`

**Auto-updates:** Every time you push to GitHub, Netlify will automatically rebuild and redeploy.

---

### Option 2: Vercel

1. **Push to GitHub** (same as above)

2. **Deploy on Vercel:**
   - Go to [vercel.com](https://vercel.com/)
   - Click "Add New..." → "Project"
   - Import your GitHub repository
   - Click "Deploy"

3. **✅ Done!** Your site will be live at `https://your-site-name.vercel.app`

---

### Option 3: GitHub Pages (Free!)

1. **Push to GitHub** (same as above)

2. **Enable GitHub Pages:**
   - Go to your repository settings
   - Scroll to "Pages"
   - Source: Deploy from branch `main`
   - Folder: `/ (root)`
   - Save

3. **✅ Done!** Your site will be live at `https://yourusername.github.io/Account-Directors/`

---

### Option 4: Heroku (Static Site)

Since you're already familiar with Heroku:

1. **Create a simple static server:**
   
   Create `server.py`:
   ```python
   from http.server import HTTPServer, SimpleHTTPRequestHandler
   import os
   
   port = int(os.environ.get('PORT', 8000))
   httpd = HTTPServer(('', port), SimpleHTTPRequestHandler)
   print(f"Serving at port {port}")
   httpd.serve_forever()
   ```

2. **Update Procfile:**
   ```
   web: python server.py
   ```

3. **Deploy:**
   ```bash
   git add .
   git commit -m "Vanilla JS dashboard"
   git push heroku main
   ```

---

### Option 5: Run Locally

For testing:

```bash
# Python 3
python -m http.server 8000

# Or Node.js
npx http-server
```

Then open: `http://localhost:8000`

---

## 🎨 Customization Guide

### Change Colors

Edit the `:root` variables in `index.html`:

```css
:root {
    --primary-dark: #0f172a;      /* Dark text */
    --primary-blue: #1e40af;      /* Primary blue */
    --primary-light: #3b82f6;     /* Light blue */
    --bg-main: #f8fafc;           /* Background */
    /* ... */
}
```

### Add New Metrics

Edit `renderMetrics()` in `app.js`:

```javascript
function renderMetrics(data) {
    // Add your custom metric here
    const customMetric = /* your calculation */;
    
    container.innerHTML += `
        <div class="metric-card fade-in">
            <div class="metric-label">Your Metric</div>
            <div class="metric-value">${customMetric}</div>
        </div>
    `;
}
```

### Add Dark Mode

Add this to `app.js`:

```javascript
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
}

// Load dark mode preference
if (localStorage.getItem('darkMode') === 'true') {
    document.body.classList.add('dark-mode');
}
```

Then add dark mode CSS in `index.html`:

```css
body.dark-mode {
    --primary-dark: #f8fafc;
    --text-primary: #f8fafc;
    --bg-main: #0f172a;
    --bg-card: #1e293b;
    --border-color: #334155;
}
```

---

## 🔧 Advanced Features

### Add Export to PDF

Install `html2pdf.js`:

```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
```

Add button:
```javascript
function exportToPDF() {
    const element = document.getElementById('rankings-view');
    html2pdf().from(element).save('rankings.pdf');
}
```

### Add Search

Add to `app.js`:

```javascript
function searchADs(query) {
    return AppState.data.accountDirectors.filter(ad =>
        ad.accountDirector.toLowerCase().includes(query.toLowerCase())
    );
}
```

---

## 📱 Mobile Responsive

The dashboard is already mobile-responsive! Test it by resizing your browser window.

Breakpoints:
- Desktop: > 1024px (full layout)
- Tablet: 768px - 1024px (compact sidebar)
- Mobile: < 768px (stacked layout)

---

## 🔒 Security Notes

**⚠️ Important:** The current setup loads `data.json` publicly. Anyone can see the review data.

### To Secure:

1. **Add Authentication:**
   - Deploy behind a login (Netlify Identity, Auth0, etc.)
   - Or use a backend API with authentication

2. **Password Protection:**
   - Netlify: Built-in password protection (Site settings → Access control)
   - Vercel: Password protection in Pro plan

3. **Private Repository:**
   - Keep your GitHub repo private
   - Only share the deployed URL with authorized users

---

## 🚀 Performance Tips

1. **Enable Compression:**
   - Most hosts (Netlify, Vercel) do this automatically
   - Reduces file sizes by 70%+

2. **Cache Data:**
   - `data.json` is cached by the browser
   - Only refreshes when you rebuild

3. **Optimize Images:**
   - Not applicable (no images currently)
   - If you add images, use WebP format

---

## 🐛 Troubleshooting

### "Failed to load data" Error

**Cause:** `data.json` not found or not deployed.

**Fix:**
1. Run `python build_data.py` locally
2. Ensure `data.json` is committed to git
3. Redeploy

### Blank Page

**Cause:** JavaScript error.

**Fix:**
1. Open browser DevTools (F12)
2. Check Console for errors
3. Verify `data.json` exists and is valid JSON

### Filters Not Working

**Cause:** Data structure mismatch.

**Fix:**
1. Rebuild data: `python build_data.py`
2. Check console for errors
3. Verify CSV structure matches expectations

---

## 📞 Support

For issues:
1. Check browser console (F12)
2. Verify `data.json` is valid: `python -m json.tool data.json`
3. Check that CSV files haven't changed structure

---

## ✅ Deployment Checklist

Before deploying:

- [ ] Run `python build_data.py`
- [ ] Test locally: `python -m http.server 8000`
- [ ] Check all views work (Rankings, Reviews, Rubric)
- [ ] Test filters and sorting
- [ ] Verify mobile layout (resize browser)
- [ ] Commit all files: `index.html`, `app.js`, `data.json`
- [ ] Push to GitHub
- [ ] Deploy to your chosen platform
- [ ] Test live URL
- [ ] Set up password protection if needed

---

**You now have a fully functional, customizable, and deployable vanilla JavaScript dashboard! 🎉**

