#!/usr/bin/env python3
"""
Install Finance Libraries for VS Terminal
This script installs all required finance and data analysis libraries for the VS Terminal environment.
"""
import subprocess
import sys
import os

def install_package(package_name, description=""):
    """Install a Python package using pip"""
    try:
        print(f"📦 Installing {package_name}... {description}")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", package_name, "--upgrade"
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"✅ {package_name} installed successfully")
            return True
        else:
            print(f"❌ Failed to install {package_name}")
            print(f"Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ Timeout installing {package_name}")
        return False
    except Exception as e:
        print(f"❌ Exception installing {package_name}: {e}")
        return False

def main():
    print("🔧 Installing Finance Libraries for VS Terminal")
    print("=" * 60)
    
    # Core finance and data science libraries
    libraries = [
        # Core Data Science
        ("pandas", "Data manipulation and analysis"),
        ("numpy", "Numerical computing"),
        ("scipy", "Scientific computing"),
        
        # Visualization
        ("matplotlib", "Plotting library"),
        ("seaborn", "Statistical visualization"),
        ("plotly", "Interactive visualizations"),
        
        # Financial Data
        ("yfinance", "Yahoo Finance data"),
        ("pandas-datareader", "Financial data reader"),
        ("quandl", "Financial data platform"),
        
        # Technical Analysis
        ("ta", "Technical analysis indicators"),
        ("TA-Lib", "Technical analysis library"),
        ("mplfinance", "Financial plotting"),
        
        # Machine Learning
        ("scikit-learn", "Machine learning library"),
        ("xgboost", "Gradient boosting"),
        ("lightgbm", "Gradient boosting"),
        
        # Financial Analytics
        ("pyfolio", "Portfolio analysis"),
        ("empyrical", "Risk and performance metrics"),
        ("quantlib", "Quantitative finance"),
        ("zipline", "Algorithmic trading"),
        
        # Risk Management
        ("arch", "ARCH/GARCH models"),
        ("statsmodels", "Statistical modeling"),
        ("pymc3", "Bayesian modeling"),
        
        # Alternative Data
        ("fredapi", "Federal Reserve Economic Data"),
        ("alpha-vantage", "Alpha Vantage API"),
        ("iexfinance", "IEX Cloud financial data"),
        
        # Utilities
        ("requests", "HTTP library"),
        ("beautifulsoup4", "Web scraping"),
        ("lxml", "XML/HTML processing"),
        ("openpyxl", "Excel file processing"),
        ("xlrd", "Excel file reading"),
        
        # Performance
        ("numba", "JIT compilation"),
        ("cython", "C extensions for Python"),
        
        # Database
        ("sqlalchemy", "SQL toolkit"),
        ("psycopg2-binary", "PostgreSQL adapter"),
        ("pymongo", "MongoDB driver"),
        
        # Advanced Analytics
        ("networkx", "Network analysis"),
        ("geopandas", "Geographic data"),
        ("folium", "Interactive maps"),
    ]
    
    successful = 0
    failed = 0
    
    for package, description in libraries:
        if install_package(package, description):
            successful += 1
        else:
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Installation Summary:")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📦 Total: {len(libraries)}")
    
    if failed > 0:
        print("\n⚠️ Some packages failed to install. This might be due to:")
        print("   - Missing system dependencies")
        print("   - Platform compatibility issues")
        print("   - Network connectivity problems")
        print("   - Package name changes or deprecation")
        print("\n💡 Try installing failed packages manually:")
        print("   pip install <package_name>")
    
    print("\n🚀 VS Terminal Finance Environment Setup Complete!")
    print("You can now use advanced financial analysis in the VS Terminal.")

if __name__ == "__main__":
    main()