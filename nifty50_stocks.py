# NIFTY 50 Stock Symbol Mapping for yfinance and Fyers API
NIFTY_50_STOCKS = {
    'ADANIENT.NS': {'fyers': 'NSE:ADANIENT', 'name': 'Adani Enterprises'},
    'ADANIPORTS.NS': {'fyers': 'NSE:ADANIPORTS', 'name': 'Adani Ports'},
    'APOLLOHOSP.NS': {'fyers': 'NSE:APOLLOHOSP', 'name': 'Apollo Hospitals'},
    'ASIANPAINT.NS': {'fyers': 'NSE:ASIANPAINT', 'name': 'Asian Paints'},
    'AXISBANK.NS': {'fyers': 'NSE:AXISBANK', 'name': 'Axis Bank'},
    'BAJAJ-AUTO.NS': {'fyers': 'NSE:BAJAJ-AUTO', 'name': 'Bajaj Auto'},
    'BAJFINANCE.NS': {'fyers': 'NSE:BAJFINANCE', 'name': 'Bajaj Finance'},
    'BAJAJFINSV.NS': {'fyers': 'NSE:BAJAJFINSV', 'name': 'Bajaj Finserv'},
    'BEL.NS': {'fyers': 'NSE:BEL', 'name': 'Bharat Electronics'},
    'BPCL.NS': {'fyers': 'NSE:BPCL', 'name': 'BPCL'},
    'BHARTIARTL.NS': {'fyers': 'NSE:BHARTIARTL', 'name': 'Bharti Airtel'},
    'BRITANNIA.NS': {'fyers': 'NSE:BRITANNIA', 'name': 'Britannia'},
    'CIPLA.NS': {'fyers': 'NSE:CIPLA', 'name': 'Cipla'},
    'COALINDIA.NS': {'fyers': 'NSE:COALINDIA', 'name': 'Coal India'},
    'DRREDDY.NS': {'fyers': 'NSE:DRREDDY', 'name': 'Dr. Reddy\'s'},
    'EICHERMOT.NS': {'fyers': 'NSE:EICHERMOT', 'name': 'Eicher Motors'},
    'GRASIM.NS': {'fyers': 'NSE:GRASIM', 'name': 'Grasim Industries'},
    'HCLTECH.NS': {'fyers': 'NSE:HCLTECH', 'name': 'HCL Technologies'},
    'HDFCBANK.NS': {'fyers': 'NSE:HDFCBANK', 'name': 'HDFC Bank'},
    'HDFCLIFE.NS': {'fyers': 'NSE:HDFCLIFE', 'name': 'HDFC Life'},
    'HEROMOTOCO.NS': {'fyers': 'NSE:HEROMOTOCO', 'name': 'Hero MotoCorp'},
    'HINDALCO.NS': {'fyers': 'NSE:HINDALCO', 'name': 'Hindalco'},
    'HINDUNILVR.NS': {'fyers': 'NSE:HINDUNILVR', 'name': 'Hindustan Unilever'},
    'ICICIBANK.NS': {'fyers': 'NSE:ICICIBANK', 'name': 'ICICI Bank'},
    'ITC.NS': {'fyers': 'NSE:ITC', 'name': 'ITC'},
    'INDUSINDBK.NS': {'fyers': 'NSE:INDUSINDBK', 'name': 'IndusInd Bank'},
    'INFY.NS': {'fyers': 'NSE:INFY', 'name': 'Infosys'},
    'JSWSTEEL.NS': {'fyers': 'NSE:JSWSTEEL', 'name': 'JSW Steel'},
    'KOTAKBANK.NS': {'fyers': 'NSE:KOTAKBANK', 'name': 'Kotak Mahindra Bank'},
    'LT.NS': {'fyers': 'NSE:LT', 'name': 'Larsen & Toubro'},
    'M&M.NS': {'fyers': 'NSE:M&M', 'name': 'Mahindra & Mahindra'},
    'MARUTI.NS': {'fyers': 'NSE:MARUTI', 'name': 'Maruti Suzuki'},
    'NTPC.NS': {'fyers': 'NSE:NTPC', 'name': 'NTPC'},
    'NESTLEIND.NS': {'fyers': 'NSE:NESTLEIND', 'name': 'Nestle India'},
    'ONGC.NS': {'fyers': 'NSE:ONGC', 'name': 'ONGC'},
    'POWERGRID.NS': {'fyers': 'NSE:POWERGRID', 'name': 'Power Grid'},
    'RELIANCE.NS': {'fyers': 'NSE:RELIANCE', 'name': 'Reliance Industries'},
    'SBILIFE.NS': {'fyers': 'NSE:SBILIFE', 'name': 'SBI Life'},
    'SHRIRAMFIN.NS': {'fyers': 'NSE:SHRIRAMFIN', 'name': 'Shriram Finance'},
    'SBIN.NS': {'fyers': 'NSE:SBIN', 'name': 'State Bank of India'},
    'SUNPHARMA.NS': {'fyers': 'NSE:SUNPHARMA', 'name': 'Sun Pharma'},
    'TCS.NS': {'fyers': 'NSE:TCS', 'name': 'Tata Consultancy Services'},
    'TATACONSUM.NS': {'fyers': 'NSE:TATACONSUM', 'name': 'Tata Consumer'},
    'TATAMOTORS.NS': {'fyers': 'NSE:TATAMOTORS', 'name': 'Tata Motors'},
    'TATASTEEL.NS': {'fyers': 'NSE:TATASTEEL', 'name': 'Tata Steel'},
    'TECHM.NS': {'fyers': 'NSE:TECHM', 'name': 'Tech Mahindra'},
    'TITAN.NS': {'fyers': 'NSE:TITAN', 'name': 'Titan Company'},
    'TRENT.NS': {'fyers': 'NSE:TRENT', 'name': 'Trent'},
    'ULTRACEMCO.NS': {'fyers': 'NSE:ULTRACEMCO', 'name': 'UltraTech Cement'},
    'WIPRO.NS': {'fyers': 'NSE:WIPRO', 'name': 'Wipro'}
}

# Sector classification for better analytics
SECTOR_MAPPING = {
    'Banking': ['HDFCBANK.NS', 'ICICIBANK.NS', 'AXISBANK.NS', 'KOTAKBANK.NS', 'INDUSINDBK.NS', 'SBIN.NS'],
    'IT': ['TCS.NS', 'INFY.NS', 'HCLTECH.NS', 'TECHM.NS', 'WIPRO.NS'],
    'Energy': ['RELIANCE.NS', 'ONGC.NS', 'BPCL.NS', 'COALINDIA.NS', 'NTPC.NS', 'POWERGRID.NS'],
    'Auto': ['MARUTI.NS', 'TATAMOTORS.NS', 'BAJAJ-AUTO.NS', 'HEROMOTOCO.NS', 'M&M.NS', 'EICHERMOT.NS'],
    'Pharma': ['SUNPHARMA.NS', 'DRREDDY.NS', 'CIPLA.NS', 'APOLLOHOSP.NS'],
    'FMCG': ['HINDUNILVR.NS', 'BRITANNIA.NS', 'ITC.NS', 'TATACONSUM.NS', 'NESTLEIND.NS'],
    'Materials': ['TATASTEEL.NS', 'JSWSTEEL.NS', 'HINDALCO.NS', 'ULTRACEMCO.NS', 'GRASIM.NS'],
    'Financial Services': ['BAJFINANCE.NS', 'BAJAJFINSV.NS', 'HDFCLIFE.NS', 'SBILIFE.NS', 'SHRIRAMFIN.NS'],
    'Telecom': ['BHARTIARTL.NS'],
    'Consumer Discretionary': ['TITAN.NS', 'TRENT.NS'],
    'Industrials': ['LT.NS', 'BEL.NS'],
    'Infrastructure': ['ADANIPORTS.NS', 'ADANIENT.NS'],
    'Paints': ['ASIANPAINT.NS']
}

def get_stock_sector(symbol):
    """Get sector for a given stock symbol"""
    for sector, stocks in SECTOR_MAPPING.items():
        if symbol in stocks:
            return sector
    return 'Others'

def get_sector_stocks(sector):
    """Get all stocks in a given sector"""
    return SECTOR_MAPPING.get(sector, [])

def get_all_sectors():
    """Get list of all sectors"""
    return list(SECTOR_MAPPING.keys())
