import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import uuid
from datetime import datetime

# Load the secrets
gsheets_secrets = st.secrets["connections"]["gsheets"]

# Set up credentials from the secrets
credentials_dict = {
    "type": gsheets_secrets["type"],
    "project_id": gsheets_secrets["project_id"],
    "private_key_id": gsheets_secrets["private_key_id"],
    "private_key": gsheets_secrets["private_key"].replace('\\n', '\n'),
    "client_email": gsheets_secrets["client_email"],
    "client_id": gsheets_secrets["client_id"],
    "auth_uri": gsheets_secrets["auth_uri"],
    "token_uri": gsheets_secrets["token_uri"],
    "auth_provider_x509_cert_url": gsheets_secrets["auth_provider_x509_cert_url"],
    "client_x509_cert_url": gsheets_secrets["client_x509_cert_url"]
}

# Authenticate and connect to Google Sheets
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"])
client = gspread.authorize(credentials)

# Open the Google Sheet by URL
spreadsheet = client.open_by_url(gsheets_secrets["spreadsheet"])

# Define menu items and prices
menu_items = {
    "Nasi Goreng": 20000,
    "Indomie Goreng": 18000,
    "Soda Gembira": 10000
}

# Initialize session state for summary
if 'summary' not in st.session_state:
    st.session_state['summary'] = {}

def add_transaction(id, item, quantity, price, total, waktu):
    spreadsheet.sheet1.append_row([id, waktu, item, quantity, price, total])
    st.success(f"Transaction for {item} added successfully!")

st.set_page_config(page_title="Waroeng Klasik", page_icon="🍜")

st.title("🍜 Waroeng Klasik")

# Display menu items in three columns
cols = st.columns(3)

for i, (item, price) in enumerate(menu_items.items()):
    with cols[i]:
        if st.button(item):
            if item in st.session_state['summary']:
                st.session_state['summary'][item]['quantity'] += 1
            else:
                st.session_state['summary'][item] = {
                    'price': price,
                    'quantity': 1
                }
        st.write(f"Price: Rp {price:,}")

# Display summary of all selected items
st.write("## Summary")
if st.session_state['summary']:
    summary = pd.DataFrame(
        [(item, details['price'], details['quantity'], details['price'] * details['quantity'])
         for item, details in st.session_state['summary'].items()],
        columns=["Item", "Price", "Quantity", "Total"]
    )
    st.dataframe(summary)
    total_quantity = summary["Quantity"].sum()
    total_price = summary["Total"].sum()
    st.write(f"**Total Quantity: {total_quantity}**")
    st.write(f"**Total Price: Rp {total_price:,}**")
    
    for item in list(st.session_state['summary']):
        if st.button(f"Remove {item}"):
            del st.session_state['summary'][item]
            break

    if st.button("Check Out"):
        checkout_id = str(uuid.uuid4())  # Generate a unique ID for the checkout
        checkout_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Get the current time
        for item, details in st.session_state['summary'].items():
            add_transaction(
                checkout_id,
                item,
                details['quantity'],
                details['price'],
                details['price'] * details['quantity'],
                checkout_time
            )
        st.session_state['summary'] = {}
else:
    st.write("No items added to the summary.")
