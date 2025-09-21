"""
Top 100 stocks mapping for real-time ML models
Maps YFinance symbols to Fyers symbols for the requested 100 stocks
"""

# Top 100 stocks as requested by user
TOP_100_STOCKS = [
    'ABB.NS', 'ADANIENSOL.NS', 'ADANIENT.NS', 'ADANIGREEN.NS', 'ADANIPORTS.NS',
    'ADANIPOWER.NS', 'ATGL.NS', 'AMBUJACEM.NS', 'APOLLOHOSP.NS', 'ASIANPAINT.NS',
    'DMART.NS', 'AXISBANK.NS', 'BAJAJ-AUTO.NS', 'BAJFINANCE.NS', 'BAJAJFINSV.NS',
    'BAJAJHLDNG.NS', 'BANKBARODA.NS', 'BEL.NS', 'BHEL.NS', 'BPCL.NS',
    'BHARTIARTL.NS', 'BOSCHLTD.NS', 'BRITANNIA.NS', 'CANBK.NS', 'CHOLAFIN.NS',
    'CIPLA.NS', 'COALINDIA.NS', 'DLF.NS', 'DABUR.NS', 'DIVISLAB.NS',
    'DRREDDY.NS', 'EICHERMOT.NS', 'GAIL.NS', 'GODREJCP.NS', 'GRASIM.NS',
    'HCLTECH.NS', 'HDFCBANK.NS', 'HDFCLIFE.NS', 'HAVELLS.NS', 'HEROMOTOCO.NS',
    'HINDALCO.NS', 'HAL.NS', 'HINDUNILVR.NS', 'ICICIBANK.NS', 'ICICIGI.NS',
    'ICICIPRULI.NS', 'ITC.NS', 'IOC.NS', 'IRCTC.NS', 'IRFC.NS',
    'INDUSINDBK.NS', 'NAUKRI.NS', 'INFY.NS', 'INDIGO.NS', 'JSWENERGY.NS',
    'JSWSTEEL.NS', 'JINDALSTEL.NS', 'JIOFIN.NS', 'KOTAKBANK.NS', 'LTIM.NS',
    'LT.NS', 'LICI.NS', 'LODHA.NS', 'M&M.NS', 'MARUTI.NS',
    'NHPC.NS', 'NTPC.NS', 'NESTLEIND.NS', 'ONGC.NS', 'PIDILITIND.NS',
    'PFC.NS', 'POWERGRID.NS', 'PNB.NS', 'RECLTD.NS', 'RELIANCE.NS',
    'SBILIFE.NS', 'MOTHERSON.NS', 'SHREECEM.NS', 'SHRIRAMFIN.NS', 'SIEMENS.NS',
    'SBIN.NS', 'SUNPHARMA.NS', 'TVSMOTOR.NS', 'TCS.NS', 'TATACONSUM.NS',
    'TATAMOTORS.NS', 'TATAPOWER.NS', 'TATASTEEL.NS', 'TECHM.NS', 'TITAN.NS',
    'TORNTPHARM.NS', 'TRENT.NS', 'ULTRACEMCO.NS', 'UNIONBANK.NS', 'UNITDSPR.NS',
    'VBL.NS', 'VEDL.NS', 'WIPRO.NS', 'ZOMATO.NS', 'ZYDUSLIFE.NS'
]

# Enhanced mapping including all top 100 stocks
ENHANCED_FYERS_YFINANCE_MAPPING = {
    # Core stocks with exact Fyers mapping
    'ABB.NS': {'fyers': 'NSE:ABB-EQ', 'name': 'ABB India Ltd'},
    'ADANIENSOL.NS': {'fyers': 'NSE:ADANIENSOL-EQ', 'name': 'Adani Energy Solutions Ltd'},
    'ADANIENT.NS': {'fyers': 'NSE:ADANIENT-EQ', 'name': 'Adani Enterprises Ltd'},
    'ADANIGREEN.NS': {'fyers': 'NSE:ADANIGREEN-EQ', 'name': 'Adani Green Energy Ltd'},
    'ADANIPORTS.NS': {'fyers': 'NSE:ADANIPORTS-EQ', 'name': 'Adani Ports and Special Economic Zone Ltd'},
    'ADANIPOWER.NS': {'fyers': 'NSE:ADANIPOWER-EQ', 'name': 'Adani Power Ltd'},
    'ATGL.NS': {'fyers': 'NSE:ATGL-EQ', 'name': 'Adani Total Gas Ltd'},
    'AMBUJACEM.NS': {'fyers': 'NSE:AMBUJACEM-EQ', 'name': 'Ambuja Cements Ltd'},
    'APOLLOHOSP.NS': {'fyers': 'NSE:APOLLOHOSP-EQ', 'name': 'Apollo Hospitals Enterprise Ltd'},
    'ASIANPAINT.NS': {'fyers': 'NSE:ASIANPAINT-EQ', 'name': 'Asian Paints Ltd'},
    'DMART.NS': {'fyers': 'NSE:DMART-EQ', 'name': 'Avenue Supermarts Ltd'},
    'AXISBANK.NS': {'fyers': 'NSE:AXISBANK-EQ', 'name': 'Axis Bank Ltd'},
    'BAJAJ-AUTO.NS': {'fyers': 'NSE:BAJAJ-AUTO-EQ', 'name': 'Bajaj Auto Ltd'},
    'BAJFINANCE.NS': {'fyers': 'NSE:BAJFINANCE-EQ', 'name': 'Bajaj Finance Ltd'},
    'BAJAJFINSV.NS': {'fyers': 'NSE:BAJAJFINSV-EQ', 'name': 'Bajaj Finserv Ltd'},
    'BAJAJHLDNG.NS': {'fyers': 'NSE:BAJAJHLDNG-EQ', 'name': 'Bajaj Holdings & Investment Ltd'},
    'BANKBARODA.NS': {'fyers': 'NSE:BANKBARODA-EQ', 'name': 'Bank of Baroda'},
    'BEL.NS': {'fyers': 'NSE:BEL-EQ', 'name': 'Bharat Electronics Ltd'},
    'BHEL.NS': {'fyers': 'NSE:BHEL-EQ', 'name': 'Bharat Heavy Electricals Ltd'},
    'BPCL.NS': {'fyers': 'NSE:BPCL-EQ', 'name': 'Bharat Petroleum Corporation Ltd'},
    'BHARTIARTL.NS': {'fyers': 'NSE:BHARTIARTL-EQ', 'name': 'Bharti Airtel Ltd'},
    'BOSCHLTD.NS': {'fyers': 'NSE:BOSCHLTD-EQ', 'name': 'Bosch Ltd'},
    'BRITANNIA.NS': {'fyers': 'NSE:BRITANNIA-EQ', 'name': 'Britannia Industries Ltd'},
    'CANBK.NS': {'fyers': 'NSE:CANBK-EQ', 'name': 'Canara Bank'},
    'CHOLAFIN.NS': {'fyers': 'NSE:CHOLAFIN-EQ', 'name': 'Cholamandalam Investment and Finance Company Ltd'},
    'CIPLA.NS': {'fyers': 'NSE:CIPLA-EQ', 'name': 'Cipla Ltd'},
    'COALINDIA.NS': {'fyers': 'NSE:COALINDIA-EQ', 'name': 'Coal India Ltd'},
    'DLF.NS': {'fyers': 'NSE:DLF-EQ', 'name': 'DLF Ltd'},
    'DABUR.NS': {'fyers': 'NSE:DABUR-EQ', 'name': 'Dabur India Ltd'},
    'DIVISLAB.NS': {'fyers': 'NSE:DIVISLAB-EQ', 'name': 'Divi\'s Laboratories Ltd'},
    'DRREDDY.NS': {'fyers': 'NSE:DRREDDY-EQ', 'name': 'Dr. Reddy\'s Laboratories Ltd'},
    'EICHERMOT.NS': {'fyers': 'NSE:EICHERMOT-EQ', 'name': 'Eicher Motors Ltd'},
    'GAIL.NS': {'fyers': 'NSE:GAIL-EQ', 'name': 'GAIL (India) Ltd'},
    'GODREJCP.NS': {'fyers': 'NSE:GODREJCP-EQ', 'name': 'Godrej Consumer Products Ltd'},
    'GRASIM.NS': {'fyers': 'NSE:GRASIM-EQ', 'name': 'Grasim Industries Ltd'},
    'HCLTECH.NS': {'fyers': 'NSE:HCLTECH-EQ', 'name': 'HCL Technologies Ltd'},
    'HDFCBANK.NS': {'fyers': 'NSE:HDFCBANK-EQ', 'name': 'HDFC Bank Ltd'},
    'HDFCLIFE.NS': {'fyers': 'NSE:HDFCLIFE-EQ', 'name': 'HDFC Life Insurance Company Ltd'},
    'HAVELLS.NS': {'fyers': 'NSE:HAVELLS-EQ', 'name': 'Havells India Ltd'},
    'HEROMOTOCO.NS': {'fyers': 'NSE:HEROMOTOCO-EQ', 'name': 'Hero MotoCorp Ltd'},
    'HINDALCO.NS': {'fyers': 'NSE:HINDALCO-EQ', 'name': 'Hindalco Industries Ltd'},
    'HAL.NS': {'fyers': 'NSE:HAL-EQ', 'name': 'Hindustan Aeronautics Ltd'},
    'HINDUNILVR.NS': {'fyers': 'NSE:HINDUNILVR-EQ', 'name': 'Hindustan Unilever Ltd'},
    'ICICIBANK.NS': {'fyers': 'NSE:ICICIBANK-EQ', 'name': 'ICICI Bank Ltd'},
    'ICICIGI.NS': {'fyers': 'NSE:ICICIGI-EQ', 'name': 'ICICI Lombard General Insurance Company Ltd'},
    'ICICIPRULI.NS': {'fyers': 'NSE:ICICIPRULI-EQ', 'name': 'ICICI Prudential Life Insurance Company Ltd'},
    'ITC.NS': {'fyers': 'NSE:ITC-EQ', 'name': 'ITC Ltd'},
    'IOC.NS': {'fyers': 'NSE:IOC-EQ', 'name': 'Indian Oil Corporation Ltd'},
    'IRCTC.NS': {'fyers': 'NSE:IRCTC-EQ', 'name': 'Indian Railway Catering and Tourism Corporation Ltd'},
    'IRFC.NS': {'fyers': 'NSE:IRFC-EQ', 'name': 'Indian Railway Finance Corporation Ltd'},
    'INDUSINDBK.NS': {'fyers': 'NSE:INDUSINDBK-EQ', 'name': 'IndusInd Bank Ltd'},
    'NAUKRI.NS': {'fyers': 'NSE:NAUKRI-EQ', 'name': 'Info Edge (India) Ltd'},
    'INFY.NS': {'fyers': 'NSE:INFY-EQ', 'name': 'Infosys Ltd'},
    'INDIGO.NS': {'fyers': 'NSE:INDIGO-EQ', 'name': 'InterGlobe Aviation Ltd'},
    'JSWENERGY.NS': {'fyers': 'NSE:JSWENERGY-EQ', 'name': 'JSW Energy Ltd'},
    'JSWSTEEL.NS': {'fyers': 'NSE:JSWSTEEL-EQ', 'name': 'JSW Steel Ltd'},
    'JINDALSTEL.NS': {'fyers': 'NSE:JINDALSTEL-EQ', 'name': 'Jindal Steel & Power Ltd'},
    'JIOFIN.NS': {'fyers': 'NSE:JIOFIN-EQ', 'name': 'Jio Financial Services Ltd'},
    'KOTAKBANK.NS': {'fyers': 'NSE:KOTAKBANK-EQ', 'name': 'Kotak Mahindra Bank Ltd'},
    'LTIM.NS': {'fyers': 'NSE:LTIM-EQ', 'name': 'LTIMindtree Ltd'},
    'LT.NS': {'fyers': 'NSE:LT-EQ', 'name': 'Larsen & Toubro Ltd'},
    'LICI.NS': {'fyers': 'NSE:LICI-EQ', 'name': 'Life Insurance Corporation of India'},
    'LODHA.NS': {'fyers': 'NSE:LODHA-EQ', 'name': 'Macrotech Developers Ltd'},
    'M&M.NS': {'fyers': 'NSE:M&M-EQ', 'name': 'Mahindra & Mahindra Ltd'},
    'MARUTI.NS': {'fyers': 'NSE:MARUTI-EQ', 'name': 'Maruti Suzuki India Ltd'},
    'NHPC.NS': {'fyers': 'NSE:NHPC-EQ', 'name': 'NHPC Ltd'},
    'NTPC.NS': {'fyers': 'NSE:NTPC-EQ', 'name': 'NTPC Ltd'},
    'NESTLEIND.NS': {'fyers': 'NSE:NESTLEIND-EQ', 'name': 'Nestle India Ltd'},
    'ONGC.NS': {'fyers': 'NSE:ONGC-EQ', 'name': 'Oil & Natural Gas Corporation Ltd'},
    'PIDILITIND.NS': {'fyers': 'NSE:PIDILITIND-EQ', 'name': 'Pidilite Industries Ltd'},
    'PFC.NS': {'fyers': 'NSE:PFC-EQ', 'name': 'Power Finance Corporation Ltd'},
    'POWERGRID.NS': {'fyers': 'NSE:POWERGRID-EQ', 'name': 'Power Grid Corporation of India Ltd'},
    'PNB.NS': {'fyers': 'NSE:PNB-EQ', 'name': 'Punjab National Bank'},
    'RECLTD.NS': {'fyers': 'NSE:RECLTD-EQ', 'name': 'REC Ltd'},
    'RELIANCE.NS': {'fyers': 'NSE:RELIANCE-EQ', 'name': 'Reliance Industries Ltd'},
    'SBILIFE.NS': {'fyers': 'NSE:SBILIFE-EQ', 'name': 'SBI Life Insurance Company Ltd'},
    'MOTHERSON.NS': {'fyers': 'NSE:MOTHERSON-EQ', 'name': 'Motherson Sumi Wiring India Ltd'},
    'SHREECEM.NS': {'fyers': 'NSE:SHREECEM-EQ', 'name': 'Shree Cement Ltd'},
    'SHRIRAMFIN.NS': {'fyers': 'NSE:SHRIRAMFIN-EQ', 'name': 'Shriram Finance Ltd'},
    'SIEMENS.NS': {'fyers': 'NSE:SIEMENS-EQ', 'name': 'Siemens Ltd'},
    'SBIN.NS': {'fyers': 'NSE:SBIN-EQ', 'name': 'State Bank of India'},
    'SUNPHARMA.NS': {'fyers': 'NSE:SUNPHARMA-EQ', 'name': 'Sun Pharmaceutical Industries Ltd'},
    'TVSMOTOR.NS': {'fyers': 'NSE:TVSMOTOR-EQ', 'name': 'TVS Motor Company Ltd'},
    'TCS.NS': {'fyers': 'NSE:TCS-EQ', 'name': 'Tata Consultancy Services Ltd'},
    'TATACONSUM.NS': {'fyers': 'NSE:TATACONSUM-EQ', 'name': 'Tata Consumer Products Ltd'},
    'TATAMOTORS.NS': {'fyers': 'NSE:TATAMOTORS-EQ', 'name': 'Tata Motors Ltd'},
    'TATAPOWER.NS': {'fyers': 'NSE:TATAPOWER-EQ', 'name': 'Tata Power Company Ltd'},
    'TATASTEEL.NS': {'fyers': 'NSE:TATASTEEL-EQ', 'name': 'Tata Steel Ltd'},
    'TECHM.NS': {'fyers': 'NSE:TECHM-EQ', 'name': 'Tech Mahindra Ltd'},
    'TITAN.NS': {'fyers': 'NSE:TITAN-EQ', 'name': 'Titan Company Ltd'},
    'TORNTPHARM.NS': {'fyers': 'NSE:TORNTPHARM-EQ', 'name': 'Torrent Pharmaceuticals Ltd'},
    'TRENT.NS': {'fyers': 'NSE:TRENT-EQ', 'name': 'Trent Ltd'},
    'ULTRACEMCO.NS': {'fyers': 'NSE:ULTRACEMCO-EQ', 'name': 'UltraTech Cement Ltd'},
    'UNIONBANK.NS': {'fyers': 'NSE:UNIONBANK-EQ', 'name': 'Union Bank of India'},
    'UNITDSPR.NS': {'fyers': 'NSE:UNITDSPR-EQ', 'name': 'United Spirits Ltd'},
    'VBL.NS': {'fyers': 'NSE:VBL-EQ', 'name': 'Varun Beverages Ltd'},
    'VEDL.NS': {'fyers': 'NSE:VEDL-EQ', 'name': 'Vedanta Ltd'},
    'WIPRO.NS': {'fyers': 'NSE:WIPRO-EQ', 'name': 'Wipro Ltd'},
    'ZOMATO.NS': {'fyers': 'NSE:ZOMATO-EQ', 'name': 'Zomato Ltd'},
    'ZYDUSLIFE.NS': {'fyers': 'NSE:ZYDUSLIFE-EQ', 'name': 'Zydus Lifesciences Ltd'}
}

def get_fyers_symbol(yf_symbol):
    """Convert YFinance symbol to Fyers symbol"""
    mapping = ENHANCED_FYERS_YFINANCE_MAPPING.get(yf_symbol)
    return mapping['fyers'] if mapping else None

def get_yfinance_symbol(fyers_symbol):
    """Convert Fyers symbol to YFinance symbol"""
    for yf_sym, data in ENHANCED_FYERS_YFINANCE_MAPPING.items():
        if data['fyers'] == fyers_symbol:
            return yf_sym
    return None

def get_all_symbols():
    """Get all available symbols"""
    return list(ENHANCED_FYERS_YFINANCE_MAPPING.keys())

def is_symbol_supported(symbol):
    """Check if symbol is in the top 100 supported stocks"""
    return symbol in TOP_100_STOCKS or symbol in ENHANCED_FYERS_YFINANCE_MAPPING
