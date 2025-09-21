import yfinance as yf

def calculate_intrinsic_value(fcf, growth_rate, discount_rate, terminal_growth_rate, years, shares_outstanding):
    # Handle potential division by zero in terminal value formula
    if discount_rate == terminal_growth_rate:
        raise ValueError("Discount rate and terminal growth rate cannot be equal. It causes division by zero.")

    discounted_fcfs = []
    for year in range(1, years + 1):
        projected_fcf = fcf * ((1 + growth_rate) ** year)
        discounted_fcf = projected_fcf / ((1 + discount_rate) ** year)
        discounted_fcfs.append(discounted_fcf)

    # Terminal value calculation
    terminal_fcf = fcf * ((1 + growth_rate) ** years)
    terminal_value = (terminal_fcf * (1 + terminal_growth_rate)) / (discount_rate - terminal_growth_rate)
    discounted_terminal_value = terminal_value / ((1 + discount_rate) ** years)

    # Total intrinsic equity value
    total_value_crores = sum(discounted_fcfs) + discounted_terminal_value
    equity_value_rupees = total_value_crores * 1e7  # Convert from crores to INR
    intrinsic_value_per_share = equity_value_rupees / shares_outstanding

    return intrinsic_value_per_share

def analyze_company(ticker, assumptions):
    print(f"\nAnalyzing {ticker}...")

    stock = yf.Ticker(ticker)

    try:
        # Fix: Use iloc to avoid deprecation warning
        current_price = stock.history(period='1d')['Close'].iloc[0]
    except Exception as e:
        print(f"Error fetching market price for {ticker}: {e}")
        return None

    try:
        shares_outstanding = stock.info['sharesOutstanding']
        company_name = stock.info.get('longName', 'Unknown Company')
    except KeyError:
        print(f"Unable to fetch required data for {ticker}.")
        return None

    try:
        intrinsic_value = calculate_intrinsic_value(
            assumptions['fcf'],
            assumptions['growth_rate'],
            assumptions['discount_rate'],
            assumptions['terminal_growth_rate'],
            assumptions['years'],
            shares_outstanding
        )
    except ValueError as ve:
        print(f"Error: {ve}")
        return None

    status = "Undervalued" if intrinsic_value > current_price else "Overvalued"

    print(f"\nCompany: {company_name}")
    print(f"Current Market Price: Rs. {current_price:,.2f}")
    print(f"Estimated Intrinsic Value: Rs. {intrinsic_value:,.2f}")
    print(f"Status: {status}\n")

    return {
        "company": company_name,
        "ticker": ticker,
        "price": current_price,
        "intrinsic_value": intrinsic_value,
        "status": status
    }

def get_user_input():
    ticker = input("Enter stock ticker (e.g., TCS.NS): ").strip().upper()

    print("\n--- Enter assumptions (in INR crores, decimals allowed) ---")
    try:
        fcf = float(input("Free Cash Flow (FCF): "))
        growth_rate = float(input("Growth Rate (e.g., 0.08 for 8%): "))
        discount_rate = float(input("Discount Rate (e.g., 0.10 for 10%): "))
        terminal_growth_rate = float(input("Terminal Growth Rate (e.g., 0.04): "))

        if discount_rate == terminal_growth_rate:
            print("Discount rate and terminal growth rate cannot be equal.")
            return None, None

        years = int(input("Number of years to project: "))
    except ValueError:
        print("Invalid input. Please enter numeric values.")
        return None, None

    assumptions = {
        'fcf': fcf,
        'growth_rate': growth_rate,
        'discount_rate': discount_rate,
        'terminal_growth_rate': terminal_growth_rate,
        'years': years
    }

    return ticker, assumptions

# --- Main Execution ---
if __name__ == "__main__":
    ticker, assumptions = get_user_input()

    if ticker and assumptions:
        analyze_company(ticker, assumptions)
    else:
        print("Analysis aborted due to invalid input.")
# Error loading model: HTTP 404 NOT FOUND
{"error":"Model not found"}
