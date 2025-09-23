# Fyers API Integration - Quick Reference Guide

## 🚀 Quick Deployment Checklist

### ✅ Pre-Deployment Verification

- [ ] Flask application starts successfully
- [ ] Environment detection working (`🧪 Development` shown in logs)
- [ ] VS Terminal ML Class accessible at `/vs_terminal_MLClass`
- [ ] Admin panel accessible at `/admin/fyers_api`
- [ ] Database tables created successfully

### ✅ AWS EC2 Deployment Steps

1. **Deploy Application**

   ```bash
   # Upload code to EC2 instance
   # Install dependencies: pip install -r requirements.txt
   # Start application: python app.py
   ```

2. **Verify Environment Detection**

   ```bash
   # Check logs for: "🏭 AWS EC2 environment detected"
   # Admin panel should show "Production Environment"
   ```

3. **Configure Fyers API**

   ```bash
   # Access: http://your-ec2-ip:80/admin/fyers_api
   # Enter App ID and App Secret
   # Test API connectivity
   ```

4. **Verify VS Terminal ML Class**
   ```bash
   # Access: http://your-ec2-ip:80/vs_terminal_MLClass
   # Check data source indicator shows "🏭 Production: Fyers API"
   # Test stock analysis features
   ```

## 🔧 Quick Troubleshooting

### Environment Detection Issues

**Symptom**: Shows "Development" instead of "Production" on AWS EC2
**Solution**:

```bash
# Set environment variable manually
export ENVIRONMENT=production
# Restart application
```

### API Configuration Issues

**Symptom**: "API Not Configured" in admin panel
**Solution**:

1. Go to `/admin/fyers_api`
2. Enter valid App ID and App Secret
3. Click "Test API Connection"
4. Save configuration if test passes

### Data Source Issues

**Symptom**: VS Terminal shows "YFinance" in production
**Solution**:

1. Check environment detection
2. Verify Fyers API configuration
3. Test API connectivity in admin panel
4. Check error logs for API failures

## 📊 Key Monitoring Points

### Health Check URLs

- Application Health: `http://your-server:80/health/fyers_api`
- Data Source Status: `http://your-server:80/api/data_source_status`
- Admin Panel: `http://your-server:80/admin/fyers_api`

### Log Monitoring

```bash
# Key log messages to monitor:
✅ "Fyers API configuration system loaded"
✅ "AWS EC2 environment detected"
✅ "Fyers API connection verified"
⚠️ "Fallback to YFinance due to API error"
❌ "Fyers API authentication failed"
```

### Performance Metrics

- API Response Time: < 500ms
- Success Rate: > 95%
- Environment Detection: 100% accurate
- Data Source Switching: Instant

## 🎯 Success Indicators

### Development Environment ✅

- Log shows: `🧪 Development environment detected`
- Admin panel shows: "Development Environment"
- VS Terminal shows: "🧪 Development: YFinance"
- Data source indicator: Orange/Warning badge

### Production Environment ✅

- Log shows: `🏭 AWS EC2 environment detected`
- Admin panel shows: "Production Environment"
- VS Terminal shows: "🏭 Production: Fyers API"
- Data source indicator: Green/Success badge

### API Configuration ✅

- Admin panel shows: "✅ API Configured"
- Test connection shows: "✅ Connection Successful"
- Usage stats show: Recent API calls
- Error rate: < 5%

## 🔄 Common Admin Tasks

### Configure New API Credentials

1. Access `/admin/fyers_api`
2. Update App ID and App Secret
3. Test connection
4. Save configuration

### Monitor API Usage

1. Check admin panel statistics
2. Review error rates
3. Monitor response times
4. Analyze usage patterns

### Troubleshoot API Issues

1. Test API connection in admin panel
2. Check error logs
3. Verify credentials
4. Test individual endpoints

## 📞 Quick Support Commands

### Check Environment

```python
# In Python shell
from fyers_api_config import FyersAPIConfig
config = FyersAPIConfig()
print(f"Environment: {config.get_current_environment()}")
print(f"Data Source: {config.get_current_data_source()}")
```

### Test API Connection

```bash
# Via curl
curl -X POST http://127.0.0.1:80/admin/fyers_api/test
```

### Check Data Source Status

```bash
# Via curl
curl http://127.0.0.1:80/api/data_source_status
```

---

## 🎉 Production Deployment Success Criteria

Your Fyers API integration is successful when:

✅ **Environment Detection**: Correctly identifies AWS EC2 vs Local  
✅ **Data Source Switching**: Uses Fyers API in production, YFinance in development  
✅ **Admin Interface**: Functional configuration and monitoring panel  
✅ **VS Terminal Integration**: All ML features work with production data  
✅ **Error Handling**: Graceful fallback when API issues occur  
✅ **Performance**: Fast response times and high success rates  
✅ **Security**: Secure credential storage and API protection

**Ready for Production! 🚀**
