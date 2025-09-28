# 💳 Persistent FinTech Dashboard with RBAC + 2FA

A teaching demo project built with **Streamlit**, showcasing:

- ✅ **Role-Based Access Control (RBAC)**
- ✅ **Two-Factor Authentication (2FA)** with Google Authenticator
- ✅ **Persistent storage** using `users.json`

This mini FinTech dashboard is designed for **teaching security principles** like authentication (who you are) and authorization (what you can do).

---

## 📂 Project Structure

```
fintech_dashboard_persistent_commented.py   # Main Streamlit app
users.json                                  # Persistent user data (auto-generated)
```

---

## 🚀 Features

### 🔐 Authentication & 2FA
- Users log in with **username + password + OTP** (Google Authenticator).
- QR code provided to easily set up in Google Authenticator.

### 👥 Role-Based Access Control (RBAC)
- **Customers**: Can view balance & transfer money.
- **Admins**: Can view all accounts, approve/reject large transfers.

### 💾 Persistence
- User accounts and balances are saved in `users.json`.
- Balances update after transfers and remain saved across app restarts.

---

## ⚙️ Installation

1. **Clone the repo:**
   ```bash
   git clone https://github.com/yourusername/fintech-dashboard.git
   cd fintech-dashboard
   ```

2. **Install dependencies:**
   ```bash
   pip install streamlit pyotp qrcode pillow
   ```

3. **Run the app:**
   ```bash
   streamlit run fintech_dashboard_persistent_commented.py
   ```

---

## 🖥️ Usage

1. **Scan QR Code**
   - Open Google Authenticator → Add account → Scan QR shown on dashboard.

2. **Login with demo credentials**
   (created automatically in `users.json` if not already present):
   - `customer1 / secure123`
   - `customer2 / wallet321`
   - `admin1 / adminpass`

3. **Explore Dashboards**
   - **Customer Dashboard** → View balance, transfer money.
   - **Admin Dashboard** → Monitor accounts, approve/reject high-value transfers.

---

## 📚 Teaching Notes

- **Persistence** → Account data stored in `users.json`.
- **2FA** → Google Authenticator integration for OTP validation.
- **RBAC** → Customers vs Admin roles.
- **Security Concept** → Combines authentication + authorization.

---

## 👨‍🏫 Author

**Dr. Usama Arshad**  
Assistant Professor (Business Analytics) | FinTech & AI Educator
