@echo off
echo Installing Portfolio Analysis Application...
echo.

echo Installing Python packages...
pip install flask flask_sqlalchemy yfinance requests pandas numpy textblob plotly flask-socketio

echo.
echo Downloading TextBlob corpora...
python -c "import nltk; nltk.download('punkt'); nltk.download('brown')"

echo.
echo Setup complete! 
echo.
echo To run the application:
echo   python app.py
echo.
echo Then open your browser to: http://localhost:5000
echo.
echo Available features:
echo   - Research Report Analysis: http://localhost:5000
echo   - Portfolio Dashboard: http://localhost:5000/portfolio  
echo   - Interactive Charts: http://localhost:5000/portfolio_charts
echo   - Real-time Alerts: http://localhost:5000/alerts
echo.
pause
