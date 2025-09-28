# fintech_dashboard_persistent_commented.py
# 🏦 Persistent FinTech Dashboard with RBAC + 2FA
# Author: Dr. Usama's teaching demo

# --------------------------
# 📦 Import required libraries
# --------------------------
import streamlit as st          # Streamlit is used to build the web app
import pyotp                   # pyotp helps us generate and verify one-time passwords (OTP)
import qrcode                  # qrcode generates QR codes for Google Authenticator setup
import io                      # io is used to handle in-memory image buffers
import json                    # json is used to save/load user data persistently
import os                      # os is used to check if data files exist
from PIL import Image          # PIL (Pillow) is used to display and resize QR codes
import random                  # random helps simulate large transfer requests for admin demo

# --------------------------
# 📁 Persistent Storage Setup
# --------------------------
DATA_FILE = "users.json"  # File where user accounts and balances are stored

# Function to save users back to file
def save_users(users):
    with open(DATA_FILE, "w") as f:          # Open file in write mode
        json.dump(users, f, indent=4)        # Dump users as pretty-printed JSON

# Function to load users from file, or create defaults if file is missing/corrupted
def load_users():
    if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:  # If no file or file empty
        # Default users created the very first time
        users = {
            "customer1": {"password": "secure123", "role": "Customer", "balance": 1500, "secret": pyotp.random_base32()},
            "customer2": {"password": "wallet321", "role": "Customer", "balance": 3200, "secret": pyotp.random_base32()},
            "admin1": {"password": "adminpass", "role": "Admin", "secret": pyotp.random_base32()},
        }
        save_users(users)  # Save to JSON file
        return users
    else:
        try:
            with open(DATA_FILE, "r") as f:  # Open file for reading
                users = json.load(f)         # Load JSON content into dictionary
            # Ensure each user has a secret for OTP
            changed = False
            for u in users:
                if "secret" not in users[u]:
                    users[u]["secret"] = pyotp.random_base32()
                    changed = True
            if changed:                      # If we added new secrets, save back
                save_users(users)
            return users
        except json.JSONDecodeError:         # Handle corrupted JSON file
            users = {
                "customer1": {"password": "secure123", "role": "Customer", "balance": 1500, "secret": pyotp.random_base32()},
                "customer2": {"password": "wallet321", "role": "Customer", "balance": 3200, "secret": pyotp.random_base32()},
                "admin1": {"password": "adminpass", "role": "Admin", "secret": pyotp.random_base32()},
            }
            save_users(users)
            return users

# Load all users into memory
USERS = load_users()

# --------------------------
# 🎨 Streamlit Page Configuration
# --------------------------
st.set_page_config(page_title="Persistent FinTech Dashboard", page_icon="💳", layout="wide")

# --------------------------
# 🏦 App Header
# --------------------------
st.title("💳 Persistent FinTech Dashboard with RBAC + 2FA")   # App title
st.markdown("""                                              # Short description
This is a **mini FinTech system** with:
- ✅ 2FA login (Google Authenticator, per user)
- ✅ RBAC (Role-Based Access Control)
- ✅ Persistent storage (balances & secrets saved in `users.json`)
""")

# --------------------------
# 🔑 Login Form
# --------------------------
st.subheader("🔑 Step 1: Login")  # Login section header

# Input fields for login
username = st.text_input("Username")                 # Username field
password = st.text_input("Password", type="password")# Password field (hidden)
otp_input = st.text_input("Enter OTP (6 digits)", max_chars=6)  # OTP input

# Initialize session state for login tracking
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

# If user typed a username that exists, show QR code for their OTP secret
if username and username in USERS:
    user_secret = USERS[username]["secret"]   # Fetch secret for this user
    # Generate provisioning URI for Google Authenticator
    uri = pyotp.TOTP(user_secret).provisioning_uri(
        name=f"{username}@fintechdemo.com", issuer_name="FinTech Demo App"
    )
    qr = qrcode.make(uri)                     # Generate QR code
    buf = io.BytesIO()                        # Create in-memory buffer
    qr.save(buf, format="PNG")                # Save QR image to buffer
    buf.seek(0)                               # Reset buffer pointer
    qr_img = Image.open(buf).resize((250, 250))  # Open and resize QR image
    st.image(qr_img, caption=f"📱 Scan this QR in Google Authenticator for {username}", use_container_width=False)

# Login button logic
if st.button("Login"):
    if username in USERS and password == USERS[username]["password"]:  # Check username/password
        role = USERS[username]["role"]                                # Fetch role
        user_totp = pyotp.TOTP(USERS[username]["secret"])             # Get user-specific TOTP generator

        if user_totp.verify(otp_input, valid_window=1):  # Verify OTP, allow ±30 sec drift
            st.session_state.logged_in = True
            st.session_state.user = username
            st.session_state.role = role
            st.success(f"🎉 Login successful! Welcome {username} ({role}).")  # Success message
            st.balloons()  # Show balloons animation
        else:
            st.error("❌ OTP invalid or expired.")  # Wrong OTP
    else:
        st.error("❌ Invalid username or password.") # Wrong username/password

# --------------------------
# 👤 Customer Dashboard
# --------------------------
if st.session_state.logged_in and st.session_state.role == "Customer":
    user = st.session_state.user
    st.header("👤 Customer Dashboard")             # Section header
    st.write(f"Welcome **{user}**")                # Show username

    balance = USERS[user]["balance"]               # Get balance
    st.metric("💰 Account Balance", f"${balance}") # Show balance metric

    st.subheader("💸 Make a Transfer")             # Transfer section
    # Select recipient (only other customers)
    recipient = st.selectbox("Select recipient", [u for u in USERS if USERS[u]["role"] == "Customer" and u != user])
    amount = st.number_input("Enter amount", min_value=1, max_value=10000, step=1)  # Transfer amount

    # Transfer button
    if st.button("Transfer Money"):
        if amount <= USERS[user]["balance"]:       # Check balance
            USERS[user]["balance"] -= amount       # Deduct from sender
            USERS[recipient]["balance"] += amount  # Add to recipient
            save_users(USERS)                      # Save updated balances
            st.success(f"✅ Transfer of ${amount} to {recipient} successful!") # Success message
        else:
            st.error("❌ Insufficient funds.")      # Error if not enough balance

# --------------------------
# 👨‍💼 Admin Dashboard
# --------------------------
elif st.session_state.logged_in and st.session_state.role == "Admin":
    st.header("👨‍💼 Admin Dashboard")               # Section header
    st.write(f"Welcome **{st.session_state.user}**")

    st.subheader("📋 View All Customer Accounts")  # Show all balances
    for u, data in USERS.items():
        if data["role"] == "Customer":
            st.write(f"**{u}** → Balance: ${data['balance']}")

    st.subheader("✅ Approve Large Transfers")      # Simulated approval section
    fake_request = {"from": "customer1", "to": "customer2", "amount": random.randint(5000, 10000)}
    st.write(f"Pending Request: {fake_request['from']} → {fake_request['to']} | Amount: ${fake_request['amount']}")

    if st.button("Approve Transfer"):
        if USERS[fake_request["from"]]["balance"] >= fake_request["amount"]:
            USERS[fake_request["from"]]["balance"] -= fake_request["amount"]
            USERS[fake_request["to"]]["balance"] += fake_request["amount"]
            save_users(USERS)
            st.success("✅ Transfer approved and processed!")
        else:
            st.error("❌ Insufficient funds in sender account.")

    if st.button("Reject Transfer"):
        st.warning("❌ Transfer request rejected.")

# --------------------------
# 📚 Teaching Notes
# --------------------------
with st.expander("ℹ️ Teaching Notes"):   # Collapsible teaching notes
    st.markdown("""
    - **Persistence**: All account data (including OTP secrets) is saved in `users.json`.
    - **2FA**: Each user has a unique Google Authenticator secret.
    - **RBAC**: Customers can transfer/view balances; Admins can manage system.
    - **Security Principle**: Authentication (who you are) + Authorization (what you can do).
    """)
