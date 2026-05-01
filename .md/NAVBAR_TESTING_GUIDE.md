# Navbar Dropdown Testing Guide

Step-by-step guide to test the role-based navbar dropdown.

---

## Prerequisites

- VitalBook application running
- Test users with different roles
- Browser with developer tools

---

## Test Users

### Admin User
- Username: `admin`
- Password: `admin123`
- Role: Superuser/Staff

### Doctor User
- Create a doctor user in admin panel
- Link Doctor model to user account
- Role: Doctor (non-staff)

### Patient User
- Any registered patient
- Username: (any patient username)
- Password: `password123`
- Role: Regular user

---

## Test Cases

### Test 1: Admin User Dropdown

**Steps:**
1. Login as admin (admin/admin123)
2. Click on username in navbar (top right)
3. Observe dropdown menu

**Expected Result:**
```
┌─────────────────────────────┐
│ ADMIN                       │
│ ⚙️  Admin Panel             │
│ 📊 Doctor Dashboard         │
├─────────────────────────────┤
│ 👤 Profile                  │
│ 📅 My Appointments          │
│ 📋 Dashboard                │
├─────────────────────────────┤
│ 🚪 Logout (red)             │
└─────────────────────────────┘
```

**Verify:**
- ✅ "ADMIN" section title appears (gray, uppercase)
- ✅ "Admin Panel" link present
- ✅ "Doctor Dashboard" link present
- ✅ Divider line after admin section
- ✅ Common links (Profile, My Appointments, Dashboard)
- ✅ Logout button is red
- ✅ All icons aligned properly
- ✅ Hover effect shows blue background

**Click Tests:**
- Click "Admin Panel" → Should open Django admin
- Click "Doctor Dashboard" → Should open doctor dashboard
- Click "Profile" → Should open profile page
- Click "My Appointments" → Should open appointments page
- Click "Dashboard" → Should open patient dashboard
- Click "Logout" → Should logout and redirect to home

---

### Test 2: Doctor User Dropdown

**Steps:**
1. Login as a doctor user
2. Click on username in navbar
3. Observe dropdown menu

**Expected Result:**
```
┌─────────────────────────────┐
│ DOCTOR                      │
│ 🩺 My Dashboard             │
├─────────────────────────────┤
│ 👤 Profile                  │
│ 📅 My Appointments          │
│ 📋 Dashboard                │
├─────────────────────────────┤
│ 🚪 Logout (red)             │
└─────────────────────────────┘
```

**Verify:**
- ✅ "DOCTOR" section title appears
- ✅ "My Dashboard" link present (with stethoscope icon)
- ✅ NO "Admin Panel" link
- ✅ Divider line after doctor section
- ✅ Common links present
- ✅ Logout button is red

**Click Tests:**
- Click "My Dashboard" → Should open doctor dashboard
- Click "Profile" → Should open profile page
- Click "My Appointments" → Should open appointments page
- Click "Dashboard" → Should open patient dashboard
- Click "Logout" → Should logout

---

### Test 3: Patient User Dropdown

**Steps:**
1. Login as a regular patient
2. Click on username in navbar
3. Observe dropdown menu

**Expected Result:**
```
┌─────────────────────────────┐
│ 👤 Profile                  │
│ 📅 My Appointments          │
│ 📋 Dashboard                │
├─────────────────────────────┤
│ 🚪 Logout (red)             │
└─────────────────────────────┘
```

**Verify:**
- ✅ NO "Admin" section
- ✅ NO "Doctor" section
- ✅ Only common links visible
- ✅ Logout button is red
- ✅ Clean, simple menu

**Click Tests:**
- Click "Profile" → Should open profile page
- Click "My Appointments" → Should open appointments page
- Click "Dashboard" → Should open patient dashboard
- Click "Logout" → Should logout

---

### Test 4: Visual Styling

**Steps:**
1. Login as any user
2. Open dropdown
3. Inspect visual elements

**Verify:**
- ✅ Dropdown has rounded corners (12px)
- ✅ Dropdown has shadow (visible but not too dark)
- ✅ Dropdown has subtle border
- ✅ Min width is 220px
- ✅ Section titles are uppercase and gray
- ✅ Dividers are thin gray lines
- ✅ Icons are 16px wide (aligned)
- ✅ Hover effect shows blue background (#f0f4ff)
- ✅ Hover effect changes icon color to blue
- ✅ Logout text and icon are red

---

### Test 5: Hover Effects

**Steps:**
1. Login as any user
2. Open dropdown
3. Hover over each menu item

**Verify:**
- ✅ Background changes to light blue (#f0f4ff)
- ✅ Text color changes to blue (#0d6efd)
- ✅ Icon color changes to blue
- ✅ Transition is smooth (0.2s)
- ✅ Cursor changes to pointer
- ✅ No layout shift on hover

---

### Test 6: Dropdown Animation

**Steps:**
1. Login as any user
2. Hover over username in navbar
3. Observe dropdown appearance

**Verify:**
- ✅ Dropdown fades in (opacity 0 → 1)
- ✅ Dropdown slides down (translateY)
- ✅ Animation is smooth (0.3s)
- ✅ Dropdown appears below username
- ✅ Dropdown is right-aligned

**Steps (hide):**
1. Move mouse away from dropdown
2. Observe dropdown disappearance

**Verify:**
- ✅ Dropdown fades out
- ✅ Dropdown slides up
- ✅ Animation is smooth

---

### Test 7: Responsive Design

**Desktop (> 1024px):**
- ✅ Dropdown appears on hover
- ✅ Full width (220px)
- ✅ All features visible

**Tablet (768px - 1024px):**
- ✅ Dropdown works same as desktop
- ✅ No layout issues

**Mobile (< 768px):**
- ✅ Navbar collapses to hamburger menu
- ✅ Dropdown works within mobile menu
- ✅ Touch-friendly (no hover required)

---

### Test 8: Browser Compatibility

**Chrome/Edge:**
- ✅ All features working
- ✅ Animations smooth
- ✅ Styling correct

**Firefox:**
- ✅ All features working
- ✅ Animations smooth
- ✅ Styling correct

**Safari:**
- ✅ All features working
- ✅ Animations smooth
- ✅ Styling correct

---

### Test 9: Accessibility

**Keyboard Navigation:**
1. Tab to username link
2. Press Enter to open dropdown
3. Tab through menu items
4. Press Enter to select

**Verify:**
- ✅ Can navigate with keyboard
- ✅ Focus states visible
- ✅ Can activate links with Enter

**Screen Reader:**
- ✅ Links are announced correctly
- ✅ Icons have proper labels
- ✅ Section titles are announced

---

### Test 10: Edge Cases

**No Doctor Profile:**
1. Login as user without doctor profile
2. Open dropdown

**Verify:**
- ✅ No "Doctor" section appears
- ✅ No errors in console
- ✅ Common links still work

**Staff User with Doctor Profile:**
1. Login as staff user who is also a doctor
2. Open dropdown

**Verify:**
- ✅ "Admin" section appears
- ✅ "Doctor" section may or may not appear (based on is_staff check)
- ✅ All links work correctly

---

## Troubleshooting

### Dropdown not showing
**Check:**
- User is logged in
- CSS file is loaded (check Network tab)
- No JavaScript errors (check Console)
- Hover is working (try clicking)

**Fix:**
- Clear browser cache
- Hard refresh (Ctrl+F5)
- Check CSS file path in base.html

### Wrong sections showing
**Check:**
- User role in admin panel
- is_staff flag
- Doctor model linked to user

**Fix:**
- Update user role in admin
- Link doctor to user account
- Restart server

### Styling issues
**Check:**
- CSS file loaded
- No CSS conflicts
- Browser compatibility

**Fix:**
- Run `python manage.py collectstatic`
- Clear browser cache
- Check for CSS overrides

### Links not working
**Check:**
- URL patterns in urls.py
- View functions exist
- User has permissions

**Fix:**
- Verify URL names match
- Check view permissions
- Review error logs

---

## Test Checklist

- [ ] Admin user sees admin section
- [ ] Doctor user sees doctor section
- [ ] Patient user sees only common links
- [ ] All links navigate correctly
- [ ] Hover effects work
- [ ] Animations are smooth
- [ ] Styling is correct
- [ ] Icons are aligned
- [ ] Logout button is red
- [ ] Dividers are visible
- [ ] Section titles are styled
- [ ] Responsive on mobile
- [ ] Works in all browsers
- [ ] Keyboard accessible
- [ ] No console errors

---

## Success Criteria

✅ All test cases pass
✅ No visual bugs
✅ No console errors
✅ Works across browsers
✅ Responsive design works
✅ Accessibility requirements met

---

**Status:** Ready for testing
**Estimated Time:** 15-20 minutes
**Priority:** High
