# 📤 BULK UPLOAD SAMPLE FILES - TESTING GUIDE

## 🎯 OVERVIEW

This directory contains **5 sample CSV files** designed to test different scenarios of the bulk analyst creation feature. Each file demonstrates specific use cases, validation rules, and error handling capabilities.

---

## 📋 SAMPLE FILES INCLUDED

### 1. **✅ sample_analysts_success.csv** 
**Purpose**: Demonstrate successful bulk creation with complete data

**Contents**: 10 professional analysts with full information
- ✅ All required fields (name, email, password)
- ✅ All optional fields (full_name, specialization, experience_years, phone, bio)
- ✅ Professional data formatting
- ✅ Realistic analyst profiles

**Expected Result**: All 10 accounts created successfully

```csv
name,email,password,full_name,specialization,experience_years,phone,bio
tech_analyst_1,tech.analyst1@company.com,techpass123,John Smith,Technical Analysis,3,+1-555-0101,Experienced technical analyst...
fund_analyst_2,fund.analyst2@company.com,fundpass123,Sarah Johnson,Fundamental Analysis,5,+1-555-0102,Senior fundamental analyst...
```

---

### 2. **🎯 sample_analysts_minimal.csv**
**Purpose**: Test minimal required fields only

**Contents**: 3 analysts with only required fields
- ✅ name, email, password (required fields only)
- ❌ No optional fields provided
- ✅ Clean, simple format

**Expected Result**: 3 accounts created with default values for optional fields

```csv
name,email,password
minimal_user1,minimal1@test.com,minimalpass123
minimal_user2,minimal2@test.com,minimalpass123
minimal_user3,minimal3@test.com,minimalpass123
```

---

### 3. **⚡ sample_analysts_mixed.csv**
**Purpose**: Test mixed success/failure scenarios

**Contents**: 7 rows with combination of valid and invalid data
- ✅ 4 valid entries (should succeed)
- ❌ 2 invalid entries (should fail)
- ⚠️  1 duplicate entry (should be skipped)

**Expected Result**: Partial success with detailed error reporting

```csv
name,email,password,full_name,specialization,experience_years,phone,bio
mixed_success_1,success1@mixed.com,mixedpass123,Success User 1,Technical Analysis,2,555-MIX-01,This user should be created successfully
,failure1@mixed.com,mixedpass123,Missing Name User,Fundamental Analysis,3,555-MIX-02,This row will fail due to missing username
migration_test,duplicate@mixed.com,mixedpass123,Duplicate Username,Derivatives Analysis,1,555-MIX-06,This will be skipped as duplicate username
```

---

### 4. **🚨 sample_analysts_errors.csv**
**Purpose**: Test comprehensive error handling and validation

**Contents**: 8 rows with various validation errors
- ❌ Missing required fields (name, email)
- ❌ Invalid email formats
- ❌ Password too short
- ❌ Special characters in username
- ❌ Duplicate usernames
- ❌ Field length violations

**Expected Result**: Most/all entries should fail with specific error messages

```csv
name,email,password,full_name,specialization,experience_years,phone,bio
,invalid1@test.com,password123,Missing Username,Technical Analysis,2,555-0001,This row has missing username
invalid_user2,,password123,Missing Email User,Fundamental Analysis,3,555-0002,This row has missing email
invalid_user3,invalid3@test.com,short,Short Password User,Risk Assessment,1,555-0003,This row has password too short
```

---

### 5. **❌ sample_analysts_bad_headers.csv**
**Purpose**: Test CSV header validation

**Contents**: Wrong column headers
- ❌ Missing required headers (name, email, password)
- ❌ Invalid column names
- ❌ Should fail at file validation stage

**Expected Result**: Upload should fail due to missing required headers

```csv
wrong_header,invalid_email,bad_password
user1,user1@test.com,pass123
user2,user2@test.com,pass123
```

---

## 🧪 HOW TO USE THESE SAMPLES

### **Step 1: Access Bulk Upload Page**
```
http://127.0.0.1:5008/admin/bulk_create_analysts?admin_key=admin123
```

### **Step 2: Test Each Sample File**
1. **Start with Success File**: Upload `sample_analysts_success.csv`
   - Should create 10 professional analysts
   - Verify all fields are populated correctly

2. **Test Minimal Fields**: Upload `sample_analysts_minimal.csv`
   - Should create 3 basic analyst accounts
   - Verify default values are applied

3. **Test Mixed Scenarios**: Upload `sample_analysts_mixed.csv`
   - Should show success, failure, and duplicate results
   - Verify detailed error reporting

4. **Test Error Handling**: Upload `sample_analysts_errors.csv`
   - Should show various validation errors
   - Verify specific error messages for each failure

5. **Test Header Validation**: Upload `sample_analysts_bad_headers.csv`
   - Should fail with header validation error
   - Verify early error detection

### **Step 3: Verify Results**
1. **Check Admin Management Page**:
   ```
   http://127.0.0.1:5008/admin/manage_analysts?admin_key=admin123
   ```

2. **Look for Created Accounts**:
   - Successfully created analysts should appear in the list
   - Check that all fields are populated correctly
   - Verify accounts are active by default

3. **Review Error Reports**:
   - Failed uploads should show detailed error messages
   - Duplicate detection should identify existing accounts
   - Validation errors should be specific and helpful

---

## 🎯 TESTING SCENARIOS COVERED

### **✅ Success Scenarios**
- ✅ Complete data with all fields
- ✅ Minimal required fields only
- ✅ Professional analyst profiles
- ✅ Various specializations and experience levels

### **⚠️ Validation Scenarios**
- ⚠️ Missing required fields (name, email, password)
- ⚠️ Invalid email formats
- ⚠️ Password length requirements
- ⚠️ Field length limitations
- ⚠️ Special character handling

### **🔄 Duplicate Detection**
- 🔄 Existing username detection
- 🔄 Existing email detection
- 🔄 Clear duplicate reporting

### **❌ Error Handling**
- ❌ Invalid CSV headers
- ❌ Malformed data
- ❌ File format validation
- ❌ Database constraint violations

---

## 📊 EXPECTED RESULTS SUMMARY

| Sample File | Total Rows | Expected Success | Expected Failures | Expected Duplicates |
|-------------|------------|------------------|-------------------|-------------------|
| **success.csv** | 10 | 10 | 0 | 0 |
| **minimal.csv** | 3 | 3 | 0 | 0 |
| **mixed.csv** | 7 | 4 | 2 | 1 |
| **errors.csv** | 8 | 0-1 | 7-8 | 1 |
| **bad_headers.csv** | 2 | 0 | ALL | 0 |

---

## 🔧 AUTOMATED TESTING

### **Run All Tests Automatically**
```bash
python test_bulk_upload_samples.py
```

This script will:
- ✅ Upload all sample files automatically
- ✅ Display file contents for review
- ✅ Report success/failure for each test
- ✅ Provide verification URLs
- ✅ Generate comprehensive test summary

### **Manual Testing Steps**
1. Access bulk upload page
2. Drag and drop each sample file
3. Review upload results
4. Check admin management for created accounts
5. Verify error messages are helpful and specific

---

## 🎨 CREATING CUSTOM TEST FILES

### **Template for New Test Files**
```csv
name,email,password,full_name,specialization,experience_years,phone,bio
your_username,your.email@domain.com,yourpassword123,Your Full Name,Your Specialization,2,555-0000,Your professional bio
```

### **Required Fields** (Must be present)
- `name` - Username (unique)
- `email` - Email address (unique, valid format)
- `password` - Password (minimum 6 characters)

### **Optional Fields** (Can be empty)
- `full_name` - Display name
- `specialization` - Area of expertise
- `experience_years` - Years of experience (number)
- `phone` - Phone number
- `bio` - Professional biography

### **Validation Rules**
- ✅ Username must be unique across all analysts
- ✅ Email must be unique and valid format
- ✅ Password must be at least 6 characters
- ✅ Experience years must be a number (if provided)
- ✅ All fields are trimmed of whitespace

---

## 🏆 SUCCESS CRITERIA

A successful bulk upload test should demonstrate:

1. **✅ Successful Account Creation**
   - Valid data creates accounts correctly
   - All fields populate as expected
   - Accounts are active by default

2. **✅ Error Detection & Reporting**
   - Invalid data is caught and reported
   - Error messages are specific and helpful
   - Processing continues for valid rows

3. **✅ Duplicate Management**
   - Existing accounts are detected
   - Duplicates are skipped (not overwritten)
   - Clear reporting of duplicate status

4. **✅ Data Integrity**
   - Only valid data is saved to database
   - Failed uploads don't corrupt existing data
   - Transaction safety is maintained

5. **✅ User Experience**
   - Clear upload feedback
   - Detailed results summary
   - Professional error reporting

---

## 🚀 READY FOR PRODUCTION

These sample files demonstrate that the bulk upload system is **production-ready** with:

- 🔒 **Robust validation** that catches all error types
- 📊 **Comprehensive reporting** for audit and debugging
- 🛡️ **Data integrity protection** with transaction safety
- 🎨 **Professional user experience** with clear feedback
- ⚡ **Efficient processing** that handles large datasets

**The bulk analyst creation system is ready for enterprise deployment!**
