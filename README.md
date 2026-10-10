# AuraKicks — HealTest AI Target E-Commerce Application

A modern, responsive e-commerce web application built as the target platform for **HealTest AI** (Self-Healing Automated Software Testing).

This platform provides a controlled, deterministic testing environment where automated testing engines execute complete shopping workflows, encounter intentional UI locators and layout redesigns, and validate self-healing test recovery.

---

## ⚡ Tech Stack

- **Frontend:** React 19 + Vite
- **Styling:** Tailwind CSS v4
- **Icons:** Lucide React
- **State Management:** React Context API + SessionStorage
- **Testing:** Playwright E2E

---

## 🛒 Shopping Flow States

1. **Product Page:**
   - Product showcase for *AuraGlide Pro Pulse Sneakers* (₹1,999)
   - Size & quantity selection
   - Dynamic cart badge updates and feedback
   - "Add to Cart" and "View Cart" navigation

2. **Cart Page:**
   - Real-time quantity adjustment & item removal
   - Subtotal, shipping, and total calculations
   - Navigation to checkout with cart validation

3. **Checkout Page:**
   - Customer details: Name, Email, Address, Postal Code
   - Simulated payment credentials (`4242 4242 4242 4242`, `12/30`, `123`)
   - Comprehensive inline form validation
   - "⚡ Fill Dummy Credentials" one-click test autofill
   - Order summary preview

4. **Order Confirmation Page:**
   - Success banner with generated order ID (`ORD-HT-XXXXXX`)
   - Order summary breakdown
   - Simulated environment disclaimer
   - "Continue Shopping" and "Reset Demo" actions

---

## 🔄 Version A vs Version B Switcher

Switch between baseline and redesigned versions via URL parameters or the developer toolbar:

- **Version A (Baseline):** `http://localhost:5173/?version=A`
  - Checkout Button ID: `checkout-button` | Text: `"Proceed to Checkout"`
  - Final Submit ID: `place-order` | Text: `"Place Order"`
  - Predictable standard layout

- **Version B (Redesigned):** `http://localhost:5173/?version=B`
  - Checkout Button ID: `proceed-to-payment` | Text: `"Continue to Payment"`
  - Final Submit ID: `confirm-purchase` | Text: `"Confirm Purchase"`
  - Rearranged layout and relocated buttons

---

## 🛠️ Testing Features (Developer Toolbar)

- **Controlled UI Presets:**
  - `Baseline`: Version A with original selectors and layout
  - `Renamed Elements`: Modified IDs & labels with baseline layout
  - `Layout Changed`: Rearranged layout with baseline IDs
  - `Combined Redesign`: Full Version B changes
- **Simulate Payment Failure:** Predictably triggers `"Payment Declined — Please try again."` without creating an order.
- **Reset Demo State:** Wipes cart, inputs, and order receipts back to a clean state.

---

## 🚀 Getting Started

### 1. Install Dependencies
```bash
npm install
```

### 2. Start Local Development Server
```bash
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

### 3. Run Automated E2E Verification
```bash
node test-e2e.js
```
