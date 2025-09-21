# -*- coding: utf-8 -*-
import yfinance as yf

def calculate_intrinsic_value(fcf, growth_rate, discount_rate, terminal_growth_rate, years, shares_outstanding):
    discounted_fcfs = []
    for year in range(1, years + 1):
        projected_fcf = fcf * ((1 + growth_rate) ** year)
        discounted_fcf = projected_fcf / ((1 + discount_rate) ** year)
        discounted_fcfs.append(discounted_fcf)

    terminal_fcf = fcf * ((1 + growth_rate) ** years)
    terminal_value = (terminal_fcf * (1 + terminal_growth_rate)) / (discount_rate - terminal_growth_rate)
    discounted_terminal_value = terminal_value / ((1 + discount_rate) ** years)

    total_value_crores = sum(discounted_fcfs) + discounted_terminal_value
    equity_value_rupees = total_value_crores * 1e7  # Convert crores to INR
    intrinsic_value_per_share = equity_value_rupees / shares_outstanding

    return intrinsic_value_per_share

def analyze_company(ticker, company_name, assumptions):
    print(f"\nAnalyzing {company_name} ({ticker})...")

    stock = yf.Ticker(ticker)

    try:
        current_price = stock.history(period='1d')['Close'][0]
    except Exception as e:
        print(f"Error fetching market price for {ticker}: {e}")
        return None

    try:
        shares_outstanding = stock.info['sharesOutstanding']
    except KeyError:
        print(f"Unable to fetch shares outstanding for {company_name}.")
        return None

    intrinsic_value = calculate_intrinsic_value(
        assumptions['fcf'],
        assumptions['growth_rate'],
        assumptions['discount_rate'],
        assumptions['terminal_growth_rate'],
        assumptions['years'],
        shares_outstanding
    )

    status = "Undervalued" if intrinsic_value > current_price else "Overvalued"

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

# --- Assumptions ---
assumptions_tcs = {
    'fcf': 40000,                 # in Crores INR
    'growth_rate': 0.08,
    'discount_rate': 0.10,
    'terminal_growth_rate': 0.04,
    'years': 5
}

assumptions_wipro = {
    'fcf': 12000,                # in Crores INR
    'growth_rate': 0.06,
    'discount_rate': 0.10,
    'terminal_growth_rate': 0.03,
    'years': 5
}

# --- Run Analysis ---
result_tcs = analyze_company("TCS.NS", "Tata Consultancy Services", assumptions_tcs)
result_wipro = analyze_company("WIPRO.NS", "Wipro Ltd", assumptions_wipro)

# --- Final Summary ---
print("Summary:")
if result_tcs and result_wipro:
    print(f"- {result_tcs['company']}: {result_tcs['status']}")
    print(f"- {result_wipro['company']}: {result_wipro['status']}")

    print("\nFinal Verdict:")
    if result_tcs['status'] == result_wipro['status']:
        print(f"Both companies are {result_tcs['status']}.")
    else:
        print(f"{result_tcs['company']} is {result_tcs['status']}, "
              f"and {result_wipro['company']} is {result_wipro['status']}.")
