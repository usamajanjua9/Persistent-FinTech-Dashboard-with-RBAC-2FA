# fintech_dashboard_persistent_commented.py
# 🏦 Persistent FinTech Dashboard with RBAC + 2FA
# Author: Dr. Usama's teaching demo

# --------------------------
# 📦 Import required libraries
# --------------------------
import streamlit as st          # For building the web app
import pyotp                   # For generating/verifying OTPs (Google Authenticator)
import qrcode                  # To generate QR codes for Google Authenticator
import io                      # For handling QR code image buffer
import json                    # For saving/loading user data persistently
import os                      # To check if data file exists
from PIL import Image          # To display QR codes in Streamlit
import random                  # To simulate large transfer requests

# --------------------------
# 📁 Persistent Storage Setup
# --------------------------
DATA_FILE = "users.json"  # File to store user accounts persistently

# Load user data from file (or create default users if file does not exist)
def load_users():
    if not os.path.exists(DATA_FILE):
        # Default demo data (created only the first time)
        users = {
            "customer1": {"password": "secure123", "role": "Customer", "balance": 1500},
            "customer2": {"password": "wallet321", "role": "Customer", "balance": 3200},
            "admin1": {"password": "adminpass", "role": "Admin"},
        }
        save_users(users)  # Save to file
    else:
        # If file exists, load JSON data
        with open(DATA_FILE, "r") as f:
            users = json.load(f)
    return users

# Save user data (balances, roles, etc.) back to the file
def save_users(users):
    with open(DATA_FILE, "w") as f:
        json.dump(users, f, indent=4)  # Pretty-print JSON for readability

# Load all users into memory
USERS = load_users()

# --------------------------
# 🔐 Setup for 2FA (Google Authenticator)
# --------------------------
# Generate a random secret key (each user normally gets their own permanent key)
SECRET_KEY = pyotp.random_base32()
totp = pyotp.TOTP(SECRET_KEY)  # Create a TOTP generator

# --------------------------
# 🎨 Streamlit Page Configuration
# --------------------------
st.set_page_config(page_title="Persistent FinTech Dashboard", page_icon="💳", layout="wide")

# --------------------------
# 🏦 App Header
# --------------------------
st.title("💳 Persistent FinTech Dashboard with RBAC + 2FA")
st.markdown("""
This is a **mini FinTech system** with:
- ✅ 2FA login (Google Authenticator)
- ✅ RBAC (Role-Based Access Control)
- ✅ Persistent storage (balances saved in `users.json`)
""")

# --------------------------
# 📱 Generate and Show QR Code
# --------------------------
st.subheader("📱 Step 1: Setup 2FA in Google Authenticator")

# Generate URI for provisioning in Google Authenticator
uri = totp.provisioning_uri(name="student@fintechdemo.com", issuer_name="FinTech Demo App")

# Create QR code for the URI
qr = qrcode.make(uri)

# Save QR to an in-memory buffer
buf = io.BytesIO()
qr.save(buf, format="PNG")
buf.seek(0)
qr_img = Image.open(buf)

# Resize QR to a nice fixed size (e.g., 250x250)
qr_img = qr_img.resize((250, 250))

# Display QR in Streamlit
st.image(qr_img, caption="Scan this QR in Google Authenticator", use_container_width=False)
st.info("👉 Open Google Authenticator → Add account → Scan QR code above.")


# --------------------------
# 🔑 Login Form
# --------------------------
st.subheader("🔑 Step 2: Login Form")

# Take inputs from user
username = st.text_input("Username")
password = st.text_input("Password", type="password")
otp_input = st.text_input("Enter OTP (6 digits)", max_chars=6)

# Session state to store login status
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

# Check login on button click
if st.button("Login"):
    # Validate username and password
    if username in USERS and password == USERS[username]["password"]:
        role = USERS[username]["role"]  # Get role of user

        # Verify OTP from Google Authenticator
        if totp.verify(otp_input):
            st.session_state.logged_in = True
            st.session_state.user = username
            st.session_state.role = role
            st.success(f"🎉 Login successful! Welcome {username} ({role}).")
            st.balloons()
        else:
            st.error("❌ OTP invalid or expired.")
    else:
        st.error("❌ Invalid username or password.")

# --------------------------
# 👤 Customer Dashboard
# --------------------------
if st.session_state.logged_in and st.session_state.role == "Customer":
    user = st.session_state.user
    st.header("👤 Customer Dashboard")
    st.write(f"Welcome **{user}**")

    # Show account balance
    balance = USERS[user]["balance"]
    st.metric("💰 Account Balance", f"${balance}")

    # Transfer money to another customer
    st.subheader("💸 Make a Transfer")
    recipient = st.selectbox("Select recipient", [u for u in USERS if USERS[u]["role"] == "Customer" and u != user])
    amount = st.number_input("Enter amount", min_value=1, max_value=10000, step=1)

    # Process transfer
    if st.button("Transfer Money"):
        if amount <= USERS[user]["balance"]:
            USERS[user]["balance"] -= amount
            USERS[recipient]["balance"] += amount
            save_users(USERS)  # Save updated balances
            st.success(f"✅ Transfer of ${amount} to {recipient} successful!")
        else:
            st.error("❌ Insufficient funds.")

# --------------------------
# 👨‍💼 Admin Dashboard
# --------------------------
elif st.session_state.logged_in and st.session_state.role == "Admin":
    st.header("👨‍💼 Admin Dashboard")
    st.write(f"Welcome **{st.session_state.user}**")

    # Show all customer balances
    st.subheader("📋 View All Customer Accounts")
    for u, data in USERS.items():
        if data["role"] == "Customer":
            st.write(f"**{u}** → Balance: ${data['balance']}")

    # Simulate pending transfer request
    st.subheader("✅ Approve Large Transfers")
    fake_request = {"from": "customer1", "to": "customer2", "amount": random.randint(5000, 10000)}

    st.write(f"Pending Request: {fake_request['from']} → {fake_request['to']} | Amount: ${fake_request['amount']}")

    # Approve transfer
    if st.button("Approve Transfer"):
        if USERS[fake_request["from"]]["balance"] >= fake_request["amount"]:
            USERS[fake_request["from"]]["balance"] -= fake_request["amount"]
            USERS[fake_request["to"]]["balance"] += fake_request["amount"]
            save_users(USERS)
            st.success("✅ Transfer approved and processed!")
        else:
            st.error("❌ Insufficient funds in sender account.")

    # Reject transfer
    if st.button("Reject Transfer"):
        st.warning("❌ Transfer request rejected.")

# --------------------------
# 📚 Teaching Notes
# --------------------------
with st.expander("ℹ️ Teaching Notes"):
    st.markdown("""
    - **Persistence**: All account data is saved in `users.json`.
    - **2FA**: Google Authenticator ensures only real users can log in.
    - **RBAC**: Customers can transfer/view balances; Admins can manage system.
    - **Security Principle**: Authentication (who you are) + Authorization (what you can do).
    """)

