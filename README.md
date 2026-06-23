# ShopWise: AI Shopping Assistant

ShopWise is a full-stack, conversational AI-driven shopping assistant web application. It parses natural language shopping queries, matches user specifications against a database inventory, ranks the results, and displays detailed recommendation details. It is styled with a premium dark-theme glassmorphism visual interface.

## 🚀 Key Innovative Features

1. **Natural Language Query Parser**: Parses phrases like *"Suggest a phone under ₹20,000 with a good camera"* to extract budget, category, and feature keywords.
2. **Budget Elasticity Toggle**:
   * **Strict**: Filters products strictly under budget.
   * **Flexible (+10%)**: Extends budget by 10% for products with exceptional customer ratings.
   * **Value (+20%)**: Extends budget by 20% to showcase premium, high-value specification upgrades.
3. **AI Verdict Comparison Engine**: Allows side-by-side spec comparison for up to 3 products and programmatically generates a written verdict on which option fits different use cases (e.g. Performance, Portability, Budget Pick).
4. **Wishlist Target Price & simulated Price Drops**: Allows users to save items, input their target discount price, and click a simulator to scan for discounts, firing real-time toasts and active UI card updates.
5. **Audited Admin Dashboard**: Administrators can perform CRUD actions on product specifications and audit user actions (logins, queries, wishlist triggers).

---

## 📁 Project Structure

```text
ai-shopping-assistant/
│
├── app.py                  # Main Flask backend application & routing
├── database.py             # SQLite helper connection methods & schema CRUD
├── db_init.py              # Database seeding script (mock products & test users)
├── ai_engine.py            # NLP Query parser, recommendation scorer & verdict writer
├── test_ai.py              # Diagnostic parser test cases
├── resume_bullet_points.md # 4 professional resume description bullets
├── README.md               # Technical setup instructions
│
├── static/
│   ├── css/
│   │   └── style.css       # Premium glassmorphic stylesheet
│   └── js/
│       └── main.js         # Client-side AJAX chat, wishlist, alerts, & compare managers
│
└── templates/
    ├── base.html           # Layout wrapper and navigation bars
    ├── index.html          # Conversational assistant panel
    ├── products.html       # Catalog browser with price/category side filters
    ├── product_detail.html # Detail spec sheets and visual spec-score ratings
    ├── compare.html        # Side-by-side spec comparison & AI verdicts
    ├── wishlist.html       # Wishlist screen with simulated price alert checkers
    ├── history.html        # Log of past recommendations queries
    ├── login.html          # Authentication logins
    ├── register.html       # Authentication registrations
    └── admin.html          # Admin CRUD tables and activity logs
```

---

## 🛠️ Setup Instructions

### 1. Prerequisites
Make sure you have Python 3.8+ installed on your computer.

### 2. Install Dependencies
This project uses standard Python libraries like `sqlite3`, `re`, `json`, and `hashlib`. The only external package needed is Flask.
Install Flask via pip:
```bash
pip install flask
```

### 3. Initialize and Seed the Database
Before running, build and seed the SQLite tables with dummy products and users:
```bash
python db_init.py
```
*(Note: If you run `app.py` first, it will automatically detect a missing database and seed it for you!)*

### 4. Run the Application
Start the local server:
```bash
python app.py
```
Navigate to **`http://127.0.0.1:5000`** in your browser.

---

## 🔑 Test Credentials

* **Regular User**:
  * Username: `user`
  * Password: `user123`
* **Admin User**:
  * Username: `admin`
  * Password: `admin123`

---

## 🧪 Running Tests
To verify NLP query parsing logic:
```bash
python test_ai.py
```
*(On Windows PowerShell, use `$env:PYTHONIOENCODING="utf-8"; python test_ai.py` to prevent console Rupee symbol print encoding errors).*
