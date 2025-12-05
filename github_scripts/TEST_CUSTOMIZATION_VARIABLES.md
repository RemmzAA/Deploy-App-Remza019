# 🧪 CUSTOMIZATION VARIABLES - COMPREHENSIVE TEST PLAN

**Date:** 2025-01-22
**Version:** 1.3.0

---

## 🎯 TEST OBJECTIVE

Verify ALL customization variables:
1. Save correctly to localStorage
2. Load correctly on page refresh
3. Apply correctly to UI elements
4. Handle edge cases gracefully
5. Security validation works

---

## 📋 TEST CASES

### TEST 1: USER NAME VARIABLE ✅

**Variable:** `customization.userName`

**Test Steps:**
1. Open Settings modal
2. Change name to "TestGamer123"
3. Save
4. Page reloads
5. Verify header shows "TestGamer123"

**Edge Cases:**
- [ ] Empty string → Should keep default "REMZA019 Gaming"
- [ ] 100 characters → Should truncate to 50
- [ ] `<script>alert(1)</script>` → Should sanitize to "scriptalert1script"
- [ ] Special chars (emoji 🎮) → Should allow
- [ ] SQL injection attempt → Should sanitize

**Expected Behavior:**
✅ Name appears in header `<h1>{customization.userName}</h1>`
✅ LocalStorage updated correctly
✅ XSS attempts blocked

---

### TEST 2: MATRIX COLOR VARIABLE ✅

**Variable:** `customization.matrixColor`

**Test Steps:**
1. Open Settings modal
2. Change Matrix color to RED `#ff0000`
3. Save
4. Page reloads
5. Verify Matrix Rain is RED

**Edge Cases:**
- [ ] Invalid hex `#GGGGGG` → Should fallback to `#00ff00`
- [ ] No # symbol `ff0000` → Should reject
- [ ] Short hex `#f00` → Should accept (valid)
- [ ] CSS code `red; display:none` → Should reject
- [ ] Empty value → Should fallback to `#00ff00`

**Expected Behavior:**
✅ CSS variable `--matrix-color` updated
✅ MatrixRain reads from CSS variable
✅ Hex-to-RGB conversion works
✅ Color applies with opacity variations

**Verification:**
```javascript
// Check CSS variable
const matrixColor = getComputedStyle(document.documentElement)
  .getPropertyValue('--matrix-color');
console.log('Matrix Color:', matrixColor); // Should be #ff0000
```

---

### TEST 3: TEXT COLOR VARIABLE ✅

**Variable:** `customization.textColor`

**Test Steps:**
1. Open Settings modal
2. Change Text color to BLUE `#0000ff`
3. Save
4. Page reloads
5. Verify text elements are BLUE

**Edge Cases:**
- [ ] Same as matrix color → Should allow
- [ ] Invalid format → Should fallback
- [ ] JavaScript injection → Should block

**Expected Behavior:**
✅ CSS variable `--text-color` updated
✅ Text elements use variable (if implemented)

**Note:** Currently text color might not be fully implemented in all components. This is for future use.

---

### TEST 4: LOGO URL VARIABLE ✅

**Variable:** `customization.logoUrl`

**Test Steps:**
1. Open Settings modal
2. Upload PNG image (500KB)
3. Preview appears
4. Save
5. Page reloads
6. Verify logo changed (if displayed)

**Edge Cases:**
- [ ] 5MB file → Should reject (2MB limit)
- [ ] .exe file → Should reject
- [ ] SVG file → Should reject (not in allowed types)
- [ ] Corrupted image → Should handle error
- [ ] No file selected → Should keep existing

**Expected Behavior:**
✅ Base64 data URL stored in localStorage
✅ Logo preview works
✅ File size validated
✅ File type validated

**LocalStorage Check:**
```javascript
const license = JSON.parse(localStorage.getItem('remza019_license'));
console.log('Logo URL length:', license.customization.logoUrl.length);
// Should be data:image/png;base64,... (long string)
```

---

### TEST 5: YOUTUBE CHANNEL ID VARIABLE ✅

**Variable:** `customization.youtubeChannelId`

**Test Steps:**
1. Open Settings modal
2. Enter "UCabcdefg1234567890"
3. Save
4. Page reloads
5. Verify saved in localStorage

**Edge Cases:**
- [ ] Empty string → Should save as empty
- [ ] 200 characters → Should truncate to 100
- [ ] `<script>` tags → Should sanitize
- [ ] Special characters → Should allow (UC prefix)

**Expected Behavior:**
✅ Value sanitized and saved
✅ Max length enforced
✅ XSS blocked

**Future Use:**
This will be used to fetch videos from user's channel instead of REMZA019's channel.

---

### TEST 6: DISCORD LINK VARIABLE ✅

**Variable:** `customization.discordLink`

**Test Steps:**
1. Open Settings modal
2. Enter "discord.gg/myserver123"
3. Save
4. Page reloads
5. Verify saved

**Edge Cases:**
- [ ] Full URL `https://discord.gg/...` → Should allow
- [ ] Just invite code `myserver123` → Should allow
- [ ] Invalid URL → Should validate
- [ ] XSS attempt → Should block

**Expected Behavior:**
✅ URL validated
✅ Sanitized
✅ Saved correctly

---

### TEST 7: SOCIAL LINKS VARIABLES ✅

**Variables:**
- `customization.socialLinks.twitter`
- `customization.socialLinks.instagram`
- `customization.socialLinks.twitch`
- `customization.socialLinks.tiktok`

**Test Steps:**
1. Open Settings modal
2. Fill all social links:
   - Twitter: "@TestUser"
   - Instagram: "@TestInsta"
   - Twitch: "TestTwitch"
   - TikTok: "@TestTikTok"
3. Save
4. Page reloads
5. Verify all saved

**Edge Cases:**
- [ ] Mix of @ symbols and without → Should allow
- [ ] Empty values → Should save as empty
- [ ] HTML injection → Should sanitize
- [ ] 200 char handles → Should truncate to 100

**Expected Behavior:**
✅ All 4 links saved independently
✅ Each sanitized separately
✅ Object structure preserved

**LocalStorage Check:**
```javascript
const license = JSON.parse(localStorage.getItem('remza019_license'));
console.log(license.customization.socialLinks);
// Should show object with all 4 properties
```

---

## 🔄 PERSISTENCE TEST

**Test:** Save → Reload → Verify → Change → Reload → Verify

**Steps:**
1. Set all customizations
2. Save (page reload)
3. Verify all applied
4. Change userName only
5. Save (page reload)
6. Verify userName changed, others unchanged

**Expected:**
✅ All values persist correctly
✅ Partial updates work
✅ No data loss

---

## 💾 LOCALSTORAGE STRUCTURE VALIDATION

**Test:** Check localStorage structure

**Execute in Console:**
```javascript
const license = JSON.parse(localStorage.getItem('remza019_license'));
console.log(JSON.stringify(license, null, 2));
```

**Expected Structure:**
```json
{
  "licenseKey": "TRIAL-XXXXX-XXXXX",
  "licenseType": "TRIAL",
  "trialStartDate": "2025-01-22T10:00:00.000Z",
  "trialExpired": false,
  "customization": {
    "userName": "TestGamer123",
    "matrixColor": "#ff0000",
    "textColor": "#0000ff",
    "logoUrl": "data:image/png;base64,...",
    "youtubeChannelId": "UCabcdefg1234567890",
    "discordLink": "discord.gg/myserver123",
    "socialLinks": {
      "twitter": "@TestUser",
      "instagram": "@TestInsta",
      "twitch": "TestTwitch",
      "tiktok": "@TestTikTok"
    }
  }
}
```

**Validation Checks:**
- ✅ All fields present
- ✅ Correct data types
- ✅ No undefined values
- ✅ Valid JSON format

---

## 🚨 ERROR HANDLING TESTS

### TEST: Corrupted localStorage

**Steps:**
1. Manually corrupt localStorage:
```javascript
localStorage.setItem('remza019_license', 'INVALID_JSON{{{');
```
2. Reload page
3. Check console

**Expected:**
✅ Error logged
✅ localStorage cleared
✅ Auto re-initialization
✅ No app crash

---

### TEST: Missing customization object

**Steps:**
1. Remove customization:
```javascript
const license = JSON.parse(localStorage.getItem('remza019_license'));
delete license.customization;
localStorage.setItem('remza019_license', JSON.stringify(license));
```
2. Reload page

**Expected:**
✅ Validation fails
✅ localStorage cleared
✅ Re-initialized with defaults
✅ No crash

---

### TEST: Invalid license type

**Steps:**
1. Set invalid type:
```javascript
const license = JSON.parse(localStorage.getItem('remza019_license'));
license.licenseType = 'HACKED';
localStorage.setItem('remza019_license', JSON.stringify(license));
```
2. Reload page

**Expected:**
✅ Validation fails
✅ Data rejected
✅ Re-initialized

---

## 🎨 CSS VARIABLE APPLICATION TEST

**Test:** Verify CSS variables propagate

**Execute in Console:**
```javascript
// Check if variables are set
const root = document.documentElement;
const matrixColor = getComputedStyle(root).getPropertyValue('--matrix-color');
const textColor = getComputedStyle(root).getPropertyValue('--text-color');

console.log('Matrix Color:', matrixColor);
console.log('Text Color:', textColor);
```

**Expected:**
✅ Variables match localStorage values
✅ Variables accessible globally
✅ MatrixRain uses these variables

---

## 📊 TEST RESULTS TEMPLATE

### Test Session: [DATE/TIME]

| Test Case | Status | Notes |
|-----------|--------|-------|
| User Name - Normal | ⏳ | |
| User Name - XSS | ⏳ | |
| User Name - Length | ⏳ | |
| Matrix Color - Valid | ⏳ | |
| Matrix Color - Invalid | ⏳ | |
| Matrix Color - CSS Injection | ⏳ | |
| Text Color - Valid | ⏳ | |
| Logo Upload - Valid | ⏳ | |
| Logo Upload - Size Limit | ⏳ | |
| Logo Upload - Type Validation | ⏳ | |
| YouTube ID - Normal | ⏳ | |
| YouTube ID - XSS | ⏳ | |
| Discord Link - Normal | ⏳ | |
| Social Links - All 4 | ⏳ | |
| Persistence - Reload | ⏳ | |
| Persistence - Partial Update | ⏳ | |
| Error - Corrupted Data | ⏳ | |
| Error - Missing Fields | ⏳ | |
| CSS Variables - Application | ⏳ | |

**Legend:**
- ⏳ Not Tested
- ✅ Passed
- ❌ Failed
- ⚠️ Partial/Warning

---

## 🔧 DEBUGGING COMMANDS

**View License Data:**
```javascript
console.log(JSON.parse(localStorage.getItem('remza019_license')));
```

**Check CSS Variables:**
```javascript
const style = getComputedStyle(document.documentElement);
console.log('--matrix-color:', style.getPropertyValue('--matrix-color'));
console.log('--text-color:', style.getPropertyValue('--text-color'));
```

**Clear and Reset:**
```javascript
localStorage.removeItem('remza019_license');
window.location.reload();
```

**Test XSS:**
```javascript
// Try to inject script (should be sanitized)
const testData = {
  userName: '<script>alert("XSS")</script>',
  matrixColor: '#00ff00'
};
// Save and check if script tag is removed
```

---

## ✅ FINAL VALIDATION CHECKLIST

Before declaring PRODUCTION READY:

- [ ] All variables save correctly
- [ ] All variables load correctly
- [ ] All variables apply to UI
- [ ] XSS attempts blocked
- [ ] File upload security works
- [ ] Color validation works
- [ ] Error recovery works
- [ ] localStorage structure valid
- [ ] CSS variables propagate
- [ ] No console errors
- [ ] No memory leaks
- [ ] Performance acceptable

---

**Test Status:** ⏳ READY FOR TESTING
**Next Step:** Execute tests and mark results
