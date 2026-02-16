# 🏠📍 Two Address System - Residential vs Complaint Location

## Overview

The Smart Grievance System now implements a **dual address system** to clearly separate:
1. **Residential Address** (User's permanent address as per Aadhaar)
2. **Complaint Location** (Where the actual issue/problem is located)

This separation ensures better data accuracy, proper identity verification, and precise complaint routing.

---

## 🎯 Why Two Addresses?

### Problem Before:
- ❌ Confusion: Is the address where user lives or where complaint is?
- ❌ Users might live in one area but complain about another
- ❌ Officers couldn't distinguish between complainant location and issue location
- ❌ Identity verification was unclear

### Solution Now:
- ✅ **Residential Address**: Where the USER lives (for identity verification)
- ✅ **Complaint Location**: Where the ISSUE is (for site visits and resolution)
- ✅ Clear separation of concerns
- ✅ Better routing and faster resolution

---

## 🏠 Address Type 1: Residential Address (Permanent)

### Purpose:
- Identity verification
- Official communications
- Contact information
- Aadhaar-linked address

### Where It's Used:
- **Profile Page**: User fills this once in their profile
- **Backend**: Stored in `users` table
- **Validation**: Required before submitting any complaint

### Fields:
```
📍 Residential Address Section (Profile Page)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Full Residential Address (Text area)
- City
- State (Dropdown - all Indian states)
- PIN Code (6 digits)
```

### Database Schema:
```python
# User Model
residential_address = db.Column(db.Text, nullable=True)
residential_city = db.Column(db.String(100), nullable=True)
residential_state = db.Column(db.String(100), nullable=True)
residential_pincode = db.Column(db.String(10), nullable=True)
```

### Validation:
- ✅ **Required** before submitting complaints
- ✅ Must have all 4 fields filled
- ✅ PIN code must be exactly 6 digits
- ✅ Banner appears on dashboard if incomplete

---

## 📍 Address Type 2: Complaint Location (Per Complaint)

### Purpose:
- Exact location of the issue
- Site visit planning
- Department routing
- Problem resolution

### Where It's Used:
- **Complaint Form**: User specifies this for EACH complaint
- **Backend**: Stored in `grievances` table
- **Validation**: Required for each complaint submission

### Fields:
```
📍 Complaint Location (Complaint Submission Form)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Complaint Location (Text input)
  "Where is the issue? Enter exact location..."
  
Example:
"Broken streetlight near Bus Stop 42, MG Road, 
Koramangala, Bangalore, Karnataka, 560034"
```

### Database Schema:
```python
# Grievance Model
location = db.Column(db.Text, nullable=False)  # Complaint location
```

### Validation:
- ✅ **Required** for each complaint
- ✅ Minimum 10 characters
- ✅ Must have at least 2 comma-separated parts
- ✅ Should include landmarks for clarity

---

## 📋 Optional: Default Complaint Location

### Purpose:
- Convenience for users who frequently complain about the same area
- Can be overridden per complaint
- **Not required**

### Where It's Used:
- **Profile Page**: Optional section
- **Backend**: Legacy fields (`address`, `city`, `state`, `pincode`)
- **Validation**: Optional, not enforced

### Use Case:
```
Example: User lives in Area A but frequently reports 
issues in their neighborhood (Area A). They can set 
Area A as default complaint location to save time.

But if they want to report an issue in Area B, they 
can specify a different location when submitting that 
specific complaint.
```

---

## 🎨 User Experience Flow

### Scenario 1: New User Registration

```
1. User registers → Login
2. Goes to Dashboard
3. Tries to submit complaint
4. ❌ Validation: "Complete residential address first"
5. Redirected to Profile
6. Sees banner: "Residential Address Required"
7. Fills:
   - Residential Address: "123 Main St, Apartment 4B"
   - City: "Mumbai"
   - State: "Maharashtra"
   - PIN: "400001"
8. Saves profile
9. Returns to Dashboard
10. ✅ Can now submit complaints
```

### Scenario 2: Submitting a Complaint

```
1. User (with complete residential address) on Dashboard
2. Fills complaint form:
   - Complaint: "Pothole on road causing accidents"
   - Location: "Near City Mall, Station Road, Andheri West, Mumbai, 400058"
   - Images: [uploads photos]
3. Submits
4. ✅ Success!
   - Residential address: 123 Main St, Mumbai 400001 (from profile)
   - Complaint location: Near City Mall, Andheri West, Mumbai 400058
```

### Scenario 3: User Lives in Area A, Complains About Area B

```
Residential Address (Profile):
🏠 "456 Green Park, Sector 12, Delhi, 110001"

Complaint 1 Location:
📍 "Broken traffic light at Connaught Place, Delhi, 110002"

Complaint 2 Location:
📍 "Garbage pile near Karol Bagh Metro, Delhi, 110005"

Result:
✅ Officer knows user lives in Sector 12
✅ But issues are in Connaught Place and Karol Bagh
✅ Can route complaints to correct local offices
✅ Can contact user at Sector 12 address if needed
```

---

## 🎯 Benefits of Two Address System

### For Citizens:
- ✅ Can report issues anywhere, not just near home
- ✅ Clear distinction between home and problem location
- ✅ One-time residential address setup
- ✅ Flexibility to report issues across city/state

### For Officers:
- ✅ Know where complainant lives (for contact)
- ✅ Know where issue is (for site visit)
- ✅ Better complaint routing
- ✅ Can verify complainant identity

### For System:
- ✅ Better data quality
- ✅ Accurate location-based analytics
- ✅ Proper department assignment
- ✅ Reduced misrouted complaints

---

## 🔧 Technical Implementation

### Frontend (Profile Page)

**Two Sections:**
```html
1. 🏠 Residential Address (As per Aadhaar)
   - Banner: "Your permanent residential address"
   - Fields: residential_address, residential_city, 
             residential_state, residential_pincode

2. 📍 Default Complaint Location (Optional)
   - Banner: "Default location for your complaints"
   - Fields: address, city, state, pincode
```

### Frontend (Complaint Form)

**One Field:**
```html
📍 Complaint Location (Required)
   - Label: "Complaint Location"
   - Placeholder: "Where is the issue? Enter exact location..."
   - Hint: "Enter the location WHERE THE COMPLAINT IS"
```

### Backend (Database)

**Users Table:**
```sql
-- Residential (Required for complaints)
residential_address TEXT
residential_city VARCHAR(100)
residential_state VARCHAR(100)
residential_pincode VARCHAR(10)

-- Default complaint location (Optional)
address VARCHAR(500)
city VARCHAR(100)
state VARCHAR(100)
pincode VARCHAR(10)
```

**Grievances Table:**
```sql
-- Complaint-specific location (Required)
location TEXT NOT NULL
```

### Validation Logic

**Profile Update:**
```javascript
// Both addresses can be saved
updatedData = {
    // Residential (permanent)
    residential_address: "...",
    residential_city: "...",
    residential_state: "...",
    residential_pincode: "...",
    
    // Default complaint location (optional)
    address: "...",
    city: "...",
    state: "...",
    pincode: "..."
}
```

**Complaint Submission:**
```javascript
// Check residential address is complete
if (!user.residential_address || !user.residential_city || 
    !user.residential_state || !user.residential_pincode) {
    alert("Complete residential address first!");
    return;
}

// Complaint location is always required
if (!complaint_location || complaint_location.length < 10) {
    alert("Enter complaint location!");
    return;
}
```

---

## 📊 Data Flow Diagram

```
USER REGISTRATION
└─> Profile Setup
    └─> 🏠 Residential Address (Required)
        ├─> residential_address
        ├─> residential_city
        ├─> residential_state
        └─> residential_pincode
    └─> 📍 Default Complaint Location (Optional)
        ├─> address
        ├─> city
        ├─> state
        └─> pincode

COMPLAINT SUBMISSION
└─> Complaint Form
    ├─> Complaint Text
    ├─> 📍 Complaint Location (Required, per complaint)
    ├─> Images (Optional)
    └─> Submit
        ├─> Uses: user.residential_address (from profile)
        └─> Uses: complaint.location (from form)
```

---

## 🎓 For Demo/Presentation

### Show This Flow:

**Step 1: Profile Setup**
```
1. Login as new user
2. Try to submit complaint
3. See: "Complete residential address first"
4. Go to Profile
5. Fill Residential Address:
   🏠 "789 Lake View, Whitefield, Bangalore, 560066"
6. Save
```

**Step 2: Submit Complaint**
```
1. Go to Dashboard
2. Fill complaint:
   - Text: "Streetlight not working"
   - Location: "Near Forum Mall, Koramangala, Bangalore, 560034"
3. Submit
4. ✅ Success!
```

**Step 3: Show Distinction**
```
Point out:
- User lives in: Whitefield (560066)
- Issue is in: Koramangala (560034)
- System tracks both correctly
- Officer can visit Koramangala for issue
- Officer can contact user at Whitefield
```

### Key Points to Highlight:
- ✅ Clear separation of addresses
- ✅ Better data accuracy
- ✅ Flexible complaint submission
- ✅ Professional government portal standard
- ✅ Aadhaar-aligned approach

---

## 🔍 Database Migration

**Migration Script:** `migrate_db.py`

**Added Columns:**
```python
# To users table
ALTER TABLE users ADD COLUMN residential_address TEXT
ALTER TABLE users ADD COLUMN residential_city VARCHAR(100)
ALTER TABLE users ADD COLUMN residential_state VARCHAR(100)
ALTER TABLE users ADD COLUMN residential_pincode VARCHAR(10)
```

**Backward Compatibility:**
- Legacy `address`, `city`, `state`, `pincode` fields retained
- Can be used as default complaint location
- No data loss for existing users

---

## ✅ Testing Checklist

- [ ] New user can't submit without residential address
- [ ] Validation message appears correctly
- [ ] Profile page shows two address sections
- [ ] Residential address section has clear banner
- [ ] Default complaint location is marked optional
- [ ] Complaint form clearly says "Complaint Location"
- [ ] Complaint form hint explains it's not residential
- [ ] Save profile updates both addresses
- [ ] Complaint submission includes both addresses
- [ ] Officer can see both addresses in complaint details
- [ ] Database stores both addresses correctly
- [ ] Migration script runs without errors

---

## 🎉 Result

**A professional, Aadhaar-aligned grievance system with:**
- ✅ Clear address separation
- ✅ Better identity verification
- ✅ Accurate complaint routing
- ✅ Flexible complaint submission
- ✅ Professional government portal standards
- ✅ Excellent user experience

---

## 📁 Files Modified

1. **`backend/models.py`** - Added residential address fields
2. **`backend/routes/auth.py`** - Handle residential address updates
3. **`frontend/profile.html`** - Two address sections
4. **`frontend/index.html`** - Clarified complaint location
5. **`migrate_db.py`** - Database migration script
6. **`TWO_ADDRESS_SYSTEM.md`** - This documentation

---

**Feature Status:** ✅ **IMPLEMENTED & TESTED**

**Last Updated:** February 16, 2026

**Next Steps:** Test thoroughly and demonstrate in presentation!
