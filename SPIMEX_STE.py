import requests
import pandas
import json

url = "https://uat.spx.spimex.com/api/history/SPIMEX_STE" # Please replace "YOUR_URL_HERE" with the actual URL
payload = {
    "SIDs": ["DSC5BTC065J"],
    "start": "2024-08-01"
}
sessionId = "f4876816-c1c4-4c69-b85b-22b36b2c61d2"
headers = {
    'Content-Type': 'application/json',
    'Cookie': f'clientType=api; sessionId={sessionId}; username=146_596_aig'
}

def send_post_request(url, payload, headers):
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error during request: {e}")
        return None

def authenticate_and_get_session_id(auth_url, login, password):
    auth_payload = {
        "login": login,
        "password": password
    }
    auth_headers = {
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post(auth_url, data=json.dumps(auth_payload), headers=auth_headers)
        response.raise_for_status()
        auth_response_json = response.json()
        if "sessionId" in auth_response_json:
            print(f"Authentication successful. Session ID: {auth_response_json['sessionId']}")
            return auth_response_json["sessionId"]
        else:
            print("Session ID not found in authentication response.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error during authentication request: {e}")
        return None

def process_and_export_to_excel(data):
    if not data or "response" not in data or not data["response"]:
        print("Invalid or empty data received.")
        return

    # Assuming we are interested in the first item in the 'response' array
    first_response_item = data["response"][0]

    instrument_data = first_response_item.get("fields", {}).get("instrument", {})
    trades_data = first_response_item.get("fields", {}).get("trades", [])
    orders_data = first_response_item.get("fields", {}).get("orders", [])
    hist_close_data = first_response_item.get("fields", {}).get("hist_close", [])

    # Convert instrument data to a DataFrame
    # For instrument, it's a single row of data, so we put it in a list
    instrument_df = pandas.DataFrame([instrument_data])

    # Convert trades data to a DataFrame
    trades_df = pandas.DataFrame(trades_data)

    # Convert orders data to a DataFrame
    orders_df = pandas.DataFrame(orders_data)

    # Convert hist_close data to a DataFrame
    hist_close_df = pandas.DataFrame(hist_close_data)

    # Define the Excel file name
    excel_file_name = "SPIMEX_Data.xlsx"

    with pandas.ExcelWriter(excel_file_name, engine='xlsxwriter') as writer:
        # Write instrument data to a sheet named 'Instrument'
        instrument_df.to_excel(writer, sheet_name='Instrument', index=False)
        print(f"Instrument data written to sheet 'Instrument' in {excel_file_name}")

        # Write trades data to a sheet named 'Trades'
        trades_df.to_excel(writer, sheet_name='Trades', index=False)
        print(f"Trades data written to sheet 'Trades' in {excel_file_name}")

        # Write orders data to a sheet named 'Orders'
        orders_df.to_excel(writer, sheet_name='Orders', index=False)
        print(f"Orders data written to sheet 'Orders' in {excel_file_name}")

        # Write hist_close data to a sheet named 'Hist_Close'
        hist_close_df.to_excel(writer, sheet_name='Hist_Close', index=False)
        print(f"Historical Close data written to sheet 'Hist_Close' in {excel_file_name}")

if __name__ == "__main__":
    auth_url = "https://uat.spx.spimex.com/api/auth"
    login = "146_596_aig"
    password = "Vg7#nLp@xR2tQe9M"
    
    # Get sessionId from authentication
    sessionId = authenticate_and_get_session_id(auth_url, login, password)
    
    if sessionId:
        # Update headers with the new sessionId
        headers['Cookie'] = f'clientType=api; sessionId={sessionId}; username={login}'
        
        json_response = send_post_request(url, payload, headers)
        if json_response:
            process_and_export_to_excel(json_response)
        else:
            print("Failed to get JSON response.")
    else:
        print("Failed to obtain sessionId. Exiting.")
