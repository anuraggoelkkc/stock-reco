"""
Web Scraping - Beautiful Soup
"""

# importing required libraries
import requests


def retrieve_data():
    # target URL to scrap
    url = "https://ewmw.edelweiss.in/api/spm/GetConsolidatedSecondaryPageData/EQ/Long%20term,Medium%20term,Short%20term/All/null"

    # headers
    headers = {
        'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"
    }

    response = requests.request("GET", url, headers=headers)

    data = response.json()
    print(data)
    # data = BeautifulSoup(response.text, 'html.parser')
    # data
    return data


def scrape_data(data):
    """
    field in url  -> new_value
    InitiationDate -> reco_date
    CompanyName -> stock_display_name
    Symbol -> stock_name 
    Report_ID -> report_id 
    Ltp -> current_price    
    ExitPrice -> target_price
    MarketCapital -> market_capital
    Expected Returns(%) is to has to be calculated as per above values. 
    """
    key_mapping = {
        "InitiationDate" : "RecoDate",
        "CompanyName" : "Name",
        "Symbol" : "Symbol",
        # "Report_ID" : "ReportID",
        "LTPChange": "LTPChange",
        "LTPChangePerc": "LTPChangePerc",
        "ID": "ID",
        "Ltp" : "CurrentPrice",
        "ExitPrice" : "TargetPrice",
        "MarketCapital" : "MarketCapital"
    }

    formatted_data = []
    for tab_details in data:
        tab_data = tab_details['TabData']
        tab_name = tab_details['TabName']
        # print("tab data", tab_data)
        for item in tab_data:
            new_format = {}
            for input_key, op_key in key_mapping.items():
                new_format[op_key] = item[input_key]
                new_format['TabName'] = tab_name
                per_returns = round(((item['ExitPrice'] - item['Ltp']) * 100)/ item['Ltp'], 2)
                new_format["ExpectedReturnsPerc"] = per_returns
            formatted_data.append(new_format)
    return formatted_data


def initialise_cloud_firestore():
    import firebase_admin
    from firebase_admin import credentials
    from firebase_admin import firestore

    # Use a service account
    cred = credentials.Certificate('secrets/serviceAccount.json')
    firebase_admin.initialize_app(cred)

    db = firestore.client()
    return db

def update_collection(data):
    db = initialise_cloud_firestore()
    for record in data:
        id = str(record.pop('ID'))
        doc_ref = db.collection(u'trending').document(id)
        doc_ref.set(record)

if __name__ == "__main__":
    data = retrieve_data()
    formatted_data = scrape_data(data)
    print(formatted_data)
    record = update_collection(formatted_data)