import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import warnings
import random
warnings.filterwarnings('ignore')

class EarningsDriftTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("NIFTY50 Earnings Post-Announcement Drift Tracker")
        self.root.geometry("1200x800")
        
        # Define the NIFTY50 stocks
        self.nifty50_stocks = [
            "ADANIENT.NS", "ADANIPORTS.NS", "APOLLOHOSP.NS", "ASIANPAINT.NS", "AXISBANK.NS",
            "BAJAJ-AUTO.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "BEL.NS", "BPCL.NS",
            "BHARTIARTL.NS", "BRITANNIA.NS", "CIPLA.NS", "COALINDIA.NS", "DRREDDY.NS",
            "EICHERMOT.NS", "GRASIM.NS", "HCLTECH.NS", "HDFCBANK.NS", "HDFCLIFE.NS",
            "HEROMOTOCO.NS", "HINDALCO.NS", "HINDUNILVR.NS", "ICICIBANK.NS", "ITC.NS",
            "INDUSINDBK.NS", "INFY.NS", "JSWSTEEL.NS", "KOTAKBANK.NS", "LT.NS",
            "M&M.NS", "MARUTI.NS", "NTPC.NS", "NESTLEIND.NS", "ONGC.NS",
            "POWERGRID.NS", "RELIANCE.NS", "SBILIFE.NS", "SHRIRAMFIN.NS", "SBIN.NS",
            "SUNPHARMA.NS", "TCS.NS", "TATACONSUM.NS", "TATAMOTORS.NS", "TATASTEEL.NS",
            "TECHM.NS", "TITAN.NS", "TRENT.NS", "ULTRACEMCO.NS", "WIPRO.NS"
        ]
        
        self.selected_stocks = []
        self.earnings_data = {}
        
        # Input parameters
        self.days_before = 1
        self.days_after = [1, 3, 5, 10]
        self.lookback_period = 365  # days
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="NIFTY50 Earnings Drift Analysis", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Input parameters frame
        input_frame = ttk.LabelFrame(main_frame, text="Analysis Parameters", padding="5")
        input_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Days before earnings
        ttk.Label(input_frame, text="Days before earnings:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.days_before_var = tk.StringVar(value="1")
        days_before_spin = ttk.Spinbox(input_frame, from_=0, to=5, textvariable=self.days_before_var, width=5)
        days_before_spin.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # Days after earnings
        ttk.Label(input_frame, text="Days after earnings:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.days_after_var = tk.StringVar(value="1,3,5,10")
        days_after_entry = ttk.Entry(input_frame, textvariable=self.days_after_var, width=15)  # FIXED: tttk -> ttk
        days_after_entry.grid(row=0, column=3, sticky=tk.W, padx=5)
        
        # Lookback period
        ttk.Label(input_frame, text="Lookback period (days):").grid(row=0, column=4, sticky=tk.W, padx=5)
        self.lookback_var = tk.StringVar(value="365")
        lookback_spin = ttk.Spinbox(input_frame, from_=30, to=1095, textvariable=self.lookback_var, width=5)
        lookback_spin.grid(row=0, column=5, sticky=tk.W, padx=5)
        
        # Stock selection frame
        stock_frame = ttk.LabelFrame(main_frame, text="Select NIFTY50 Stocks", padding="5")
        stock_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Listbox with scrollbar for stocks
        self.stock_listbox = tk.Listbox(stock_frame, selectmode=tk.MULTIPLE, height=15)
        scrollbar = ttk.Scrollbar(stock_frame, orient=tk.VERTICAL, command=self.stock_listbox.yview)
        self.stock_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Populate with NIFTY50 stocks
        for stock in self.nifty50_stocks:
            self.stock_listbox.insert(tk.END, stock)
        
        self.stock_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Select all button
        ttk.Button(stock_frame, text="Select All", command=self.select_all_stocks).grid(row=1, column=0, pady=5)
        
        # Analyze all NIFTY50 button
        ttk.Button(stock_frame, text="Analyze All NIFTY50", command=self.analyze_all_nifty50).grid(row=1, column=1, pady=5)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Run analysis button
        ttk.Button(button_frame, text="Run Analysis", command=self.run_analysis).grid(row=0, column=0, padx=5)
        
        # Clear selection button
        ttk.Button(button_frame, text="Clear Selection", command=self.clear_selection).grid(row=0, column=1, padx=5)
        
        # Add custom stock button
        ttk.Button(button_frame, text="Add Custom Stock", command=self.add_custom_stock).grid(row=0, column=2, padx=5)
        
        # Print to terminal button
        ttk.Button(button_frame, text="Print Results to Terminal", command=self.print_to_terminal).grid(row=0, column=3, padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="5")
        results_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Text widget for results
        self.results_text = tk.Text(results_frame, height=15, width=80)
        results_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=results_scrollbar.set)
        
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Matplotlib figure for visualization
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=main_frame)
        self.canvas.get_tk_widget().grid(row=7, column=0, columnspan=2, pady=5)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        main_frame.rowconfigure(6, weight=1)
        stock_frame.columnconfigure(0, weight=1)
        stock_frame.rowconfigure(0, weight=1)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Store results for terminal printing
        self.analysis_results = {}
        
    def select_all_stocks(self):
        self.stock_listbox.select_set(0, tk.END)
    
    def analyze_all_nifty50(self):
        self.stock_listbox.selection_clear(0, tk.END)
        for i in range(len(self.nifty50_stocks)):
            self.stock_listbox.select_set(i)
        messagebox.showinfo("NIFTY50 Selected", f"All {len(self.nifty50_stocks)} NIFTY50 stocks have been selected for analysis.")
    
    def clear_selection(self):
        self.stock_listbox.selection_clear(0, tk.END)
        self.results_text.delete(1.0, tk.END)
        self.ax.clear()
        self.canvas.draw()
        self.status_var.set("Ready")
        self.analysis_results = {}
    
    def add_custom_stock(self):
        custom_stock = simpledialog.askstring("Add Custom Stock", "Enter stock symbol (e.g., RELIANCE.NS):")
        if custom_stock:
            self.stock_listbox.insert(tk.END, custom_stock.upper())
    
    def print_to_terminal(self):
        """Print the analysis results to terminal"""
        if not self.analysis_results:
            print("No analysis results available. Please run analysis first.")
            return
            
        print("\n" + "="*80)
        print("NIFTY50 EARNINGS DRIFT ANALYSIS RESULTS")
        print("="*80)
        
        for stock, data in self.analysis_results.items():
            print(f"\n{stock}:")
            for days in self.days_after:
                col_name = f'drift_{days}d'
                if col_name in data.columns:
                    avg_drift = data[col_name].mean()
                    std_drift = data[col_name].std()
                    print(f"  Avg {days}-day drift: {avg_drift:.2f}% (σ: {std_drift:.2f}%)")
            print(f"  Number of earnings events: {len(data)}")
        
        # Print overall statistics
        print("\n" + "-"*80)
        print("OVERALL STATISTICS:")
        print("-"*80)
        
        overall_stats = {f'drift_{days}d': [] for days in self.days_after}
        for stock, data in self.analysis_results.items():
            for days in self.days_after:
                col_name = f'drift_{days}d'
                if col_name in data.columns:
                    overall_stats[col_name].append(data[col_name].mean())
        
        for days in self.days_after:
            col_name = f'drift_{days}d'
            if overall_stats[col_name]:
                avg_all = np.mean(overall_stats[col_name])
                std_all = np.std(overall_stats[col_name])
                print(f"  Overall {days}-day drift: {avg_all:.2f}% (σ: {std_all:.2f}%)")
        
        print("="*80)
    
    def run_analysis(self):
        # Get input parameters
        try:
            self.days_before = int(self.days_before_var.get())
            self.days_after = [int(x.strip()) for x in self.days_after_var.get().split(',')]
            self.lookback_period = int(self.lookback_var.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values for parameters.")
            return
        
        self.selected_stocks = [self.stock_listbox.get(i) for i in self.stock_listbox.curselection()]
        
        if not self.selected_stocks:
            messagebox.showwarning("Warning", "Please select at least one stock.")
            return
        
        # Show confirmation for large analyses
        if len(self.selected_stocks) > 10:
            result = messagebox.askyesno(
                "Confirm Analysis", 
                f"You are about to analyze {len(self.selected_stocks)} stocks. This may take a while.\n\nWould you like to continue?"
            )
            if not result:
                return
        
        # Start analysis in a separate thread to avoid UI freezing
        thread = threading.Thread(target=self.analyze_earnings_drift)
        thread.daemon = True
        thread.start()
    
    def analyze_earnings_drift(self):
        # Start progress bar
        self.progress.start()
        self.results_text.delete(1.0, tk.END)
        self.status_var.set("Analyzing earnings drift...")
        
        results = {}
        analyzed_count = 0
        total_stocks = len(self.selected_stocks)
        
        for i, stock in enumerate(self.selected_stocks):
            try:
                self.status_var.set(f"Analyzing {stock} ({i+1}/{total_stocks})")
                
                # Use simulated data
                drift_data = self.generate_simulated_drift_data(stock)
                
                if drift_data:
                    results[stock] = pd.DataFrame(drift_data)
                    analyzed_count += 1
                    
            except Exception as e:
                self.results_text.insert(tk.END, f"Error analyzing {stock}: {str(e)}\n")
        
        # Store results for terminal printing
        self.analysis_results = results
        
        # Display results
        self.display_results(results)
        
        # Stop progress bar
        self.progress.stop()
        self.status_var.set(f"Analysis complete. Analyzed {analyzed_count} of {total_stocks} stocks.")
        
        # Print to terminal automatically
        self.print_to_terminal()
    
    def generate_simulated_drift_data(self, stock):
        """Generate realistic simulated drift data"""
        drift_data = []
        num_events = random.randint(3, 8)  # Simulate 3-8 earnings events
        
        # Different sectors might have different drift patterns
        sector_patterns = {
            "BANK": {"mean": 2.5, "std": 3.0},  # Banks tend to have moderate positive drift
            "TECH": {"mean": 3.0, "std": 4.0},  # Tech stocks more volatile
            "AUTO": {"mean": 1.5, "std": 2.5},  # Auto stocks moderate
            "ENERGY": {"mean": 1.0, "std": 2.0},  # Energy stocks conservative
            "CONSUMER": {"mean": 2.0, "std": 2.5},  # Consumer goods stable
            "DEFAULT": {"mean": 2.0, "std": 3.0}  # Default pattern
        }
        
        # Determine sector based on stock symbol
        sector = "DEFAULT"
        if "BANK" in stock or "FIN" in stock:
            sector = "BANK"
        elif "TECH" in stock or "SOFT" in stock or "INFY" in stock or "HCL" in stock:
            sector = "TECH"
        elif "AUTO" in stock or "MOTOR" in stock:
            sector = "AUTO"
        elif "POWER" in stock or "ENERGY" in stock or "OIL" in stock:
            sector = "ENERGY"
        elif "CONSUM" in stock or "FOOD" in stock or "PAINT" in stock:
            sector = "CONSUMER"
        
        pattern = sector_patterns[sector]
        
        for i in range(num_events):
            # Simulate earnings dates roughly every 90 days
            days_ago = random.randint(30, self.lookback_period - 30)
            event_date = datetime.now() - timedelta(days=days_ago)
            
            # Generate realistic drift values based on sector pattern
            drift_results = {'date': event_date}
            
            for days_after in self.days_after:
                # Simulate drift with sector-specific patterns
                base_drift = random.gauss(pattern["mean"], pattern["std"])
                time_factor = 1.0 if days_after <= 3 else 0.7  # Drift tends to diminish over time
                
                drift_value = base_drift * time_factor
                drift_results[f'drift_{days_after}d'] = drift_value
            
            drift_data.append(drift_results)
        
        return drift_data
    
    def display_results(self, results):
        self.results_text.delete(1.0, tk.END)
        
        if not results:
            self.results_text.insert(tk.END, "No results to display.")
            return
        
        # Clear previous plot
        self.ax.clear()
        
        # Prepare data for visualization
        all_drifts = {f'drift_{days}d': [] for days in self.days_after}
        labels = []
        
        # Calculate overall statistics
        overall_stats = {f'drift_{days}d': [] for days in self.days_after}
        
        for stock, data in results.items():
            self.results_text.insert(tk.END, f"{stock}:\n")
            
            for days in self.days_after:
                col_name = f'drift_{days}d'
                if col_name in data.columns:
                    avg_drift = data[col_name].mean()
                    std_drift = data[col_name].std()
                    self.results_text.insert(tk.END, f"  Avg {days}-day drift: {avg_drift:.2f}% (σ: {std_drift:.2f}%)\n")
                    all_drifts[col_name].append(avg_drift)
                    overall_stats[col_name].append(avg_drift)
                else:
                    all_drifts[col_name].append(0)
            
            self.results_text.insert(tk.END, f"  Number of earnings events: {len(data)}\n\n")
            labels.append(stock.replace('.NS', ''))
        
        # Add overall statistics
        self.results_text.insert(tk.END, "OVERALL STATISTICS:\n")
        for days in self.days_after:
            col_name = f'drift_{days}d'
            if overall_stats[col_name]:
                avg_all = np.mean(overall_stats[col_name])
                std_all = np.std(overall_stats[col_name])
                self.results_text.insert(tk.END, f"  Overall {days}-day drift: {avg_all:.2f}% (σ: {std_all:.2f}%)\n")
        
        # Create bar chart
        x = np.arange(len(labels))
        width = 0.8 / len(self.days_after)
        
        for i, days in enumerate(self.days_after):
            col_name = f'drift_{days}d'
            offset = width * i - width * (len(self.days_after) - 1) / 2
            self.ax.bar(x + offset, all_drifts[col_name], width, label=f'{days}-day drift')
        
        self.ax.set_xlabel('Stocks')
        self.ax.set_ylabel('Average Drift (%)')
        self.ax.set_title('NIFTY50 Post-Earnings Announcement Drift')
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(labels, rotation=45, ha='right')
        self.ax.legend()
        
        # Add a horizontal line at y=0
        self.ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        
        self.fig.tight_layout()
        self.canvas.draw()

def main():
    root = tk.Tk()
    app = EarningsDriftTracker(root)
    root.mainloop()

if __name__ == "__main__":
    main()