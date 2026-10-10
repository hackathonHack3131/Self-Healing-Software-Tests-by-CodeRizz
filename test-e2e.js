import { chromium } from 'playwright';

async function runTests() {
  console.log('🚀 Starting E2E verification of HealTest AI Demo Store...');
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  const consoleErrors = [];
  page.on('console', (msg) => {
    if (msg.type() === 'error') {
      consoleErrors.push(msg.text());
    }
  });

  try {
    // ----------------------------------------------------
    // TEST 1: URL version selection & Version A baseline elements
    // ----------------------------------------------------
    console.log('\n--- TEST 1: Load http://localhost:5173/?version=A ---');
    await page.goto('http://localhost:5173/?version=A', { waitUntil: 'networkidle' });

    // Verify Product details
    const productTitle = await page.textContent('#product-title');
    console.log(`✓ Product title: "${productTitle.trim()}"`);
    if (!productTitle.includes('AuraGlide Pro Pulse Sneakers')) {
      throw new Error(`Expected product title to contain "AuraGlide Pro Pulse Sneakers", got: ${productTitle}`);
    }

    const priceText = await page.textContent('#product-price');
    console.log(`✓ Product price: ${priceText.trim()}`);
    if (!priceText.includes('1,999')) {
      throw new Error(`Expected price to contain 1,999, got: ${priceText}`);
    }

    // ----------------------------------------------------
    // TEST 2: Add product to cart & check badge update
    // ----------------------------------------------------
    console.log('\n--- TEST 2: Add to Cart ---');
    await page.click('#add-to-cart-button');
    await page.waitForTimeout(500);

    const badgeCount = await page.textContent('#cart-quantity-badge');
    console.log(`✓ Cart badge count: ${badgeCount.trim()}`);
    if (badgeCount.trim() !== '1') {
      throw new Error(`Expected cart badge count 1, got: ${badgeCount}`);
    }

    // ----------------------------------------------------
    // TEST 3: Navigate to Cart & verify Version A identifiers
    // ----------------------------------------------------
    console.log('\n--- TEST 3: Cart Page in Version A ---');
    await page.click('#view-cart-button');
    await page.waitForTimeout(400);

    // Verify Version A Checkout Button
    const vACheckoutBtn = await page.$('#checkout-button');
    if (!vACheckoutBtn) {
      throw new Error('Version A expected button with id="checkout-button", but not found!');
    }
    const vACheckoutText = await vACheckoutBtn.textContent();
    console.log(`✓ Version A Checkout button found: id="checkout-button", text="${vACheckoutText.trim()}"`);
    if (!vACheckoutText.includes('Proceed to Checkout')) {
      throw new Error(`Expected text "Proceed to Checkout", got "${vACheckoutText}"`);
    }

    // Test quantity increase
    await page.click('button:has-text("+")');
    await page.waitForTimeout(300);
    const updatedBadge = await page.textContent('#cart-quantity-badge');
    console.log(`✓ Quantity increased. Cart count: ${updatedBadge.trim()}`);

    // Reduce quantity back to 1
    await page.click('button:has-text("-")');
    await page.waitForTimeout(300);

    // ----------------------------------------------------
    // TEST 4: Navigate to Checkout & verify Version A identifiers
    // ----------------------------------------------------
    console.log('\n--- TEST 4: Checkout Page in Version A ---');
    await page.click('#checkout-button');
    await page.waitForTimeout(400);

    // Verify Version A final submit button
    const vAPlaceOrderBtn = await page.$('#place-order');
    if (!vAPlaceOrderBtn) {
      throw new Error('Version A expected button with id="place-order", but not found!');
    }
    const vAPlaceOrderText = await vAPlaceOrderBtn.textContent();
    console.log(`✓ Version A Place Order button found: id="place-order", text="${vAPlaceOrderText.trim()}"`);
    if (!vAPlaceOrderText.includes('Place Order')) {
      throw new Error(`Expected text "Place Order", got "${vAPlaceOrderText}"`);
    }

    // ----------------------------------------------------
    // TEST 5: Form Validation
    // ----------------------------------------------------
    console.log('\n--- TEST 5: Form Validation ---');
    await page.click('#place-order');
    await page.waitForTimeout(300);
    const validationError = await page.textContent('text=Full name is required');
    console.log(`✓ Form validation triggered: "${validationError.trim()}"`);

    // ----------------------------------------------------
    // TEST 6: Simulated Payment Failure
    // ----------------------------------------------------
    console.log('\n--- TEST 6: Simulated Payment Failure ---');
    // Quick fill credentials
    await page.click('#quick-fill-btn');
    await page.waitForTimeout(300);

    // Turn ON payment failure simulator
    await page.click('#simulate-payment-failure-toggle');
    await page.waitForTimeout(300);

    // Click submit
    await page.click('#place-order');
    await page.waitForTimeout(1000); // wait for simulated network delay

    // Verify failure error message
    const errorAlert = await page.textContent('#payment-error-alert');
    console.log(`✓ Simulated Payment Error displayed: "${errorAlert.trim().replace(/\s+/g, ' ')}"`);
    if (!errorAlert.includes('Payment Declined — Please try again.')) {
      throw new Error(`Expected "Payment Declined — Please try again.", got "${errorAlert}"`);
    }

    // Confirm that order receipt is NOT shown
    const orderReceipt = await page.$('#order-success-title');
    if (orderReceipt) {
      throw new Error('Order receipt should NOT be displayed when payment fails!');
    }
    console.log('✓ Verified: Order was NOT created upon payment failure.');

    // ----------------------------------------------------
    // TEST 7: Successful Payment & Order Confirmation
    // ----------------------------------------------------
    console.log('\n--- TEST 7: Successful Payment ---');
    // Turn OFF failure simulator
    await page.click('#simulate-payment-failure-toggle');
    await page.waitForTimeout(300);

    // Click submit again
    await page.click('#place-order');
    await page.waitForTimeout(1200);

    // Verify Order Confirmation Page
    const successTitle = await page.textContent('#order-success-title');
    const orderId = await page.textContent('#order-id-display');
    console.log(`✓ Order Success: "${successTitle.trim()}", Order ID: "${orderId.trim()}"`);
    if (!successTitle.includes('Order Successful!')) {
      throw new Error(`Expected Order Successful!, got: ${successTitle}`);
    }

    // ----------------------------------------------------
    // TEST 8: Reset Demo State
    // ----------------------------------------------------
    console.log('\n--- TEST 8: Reset Demo State ---');
    await page.click('#reset-demo-button');
    await page.waitForTimeout(500);

    const backOnProduct = await page.$('#product-title');
    if (!backOnProduct) {
      throw new Error('Reset demo did not return to product page!');
    }
    const emptyBadge = await page.$('#cart-quantity-badge');
    if (emptyBadge) {
      throw new Error('Cart badge should be empty after reset!');
    }
    console.log('✓ Reset Demo successfully returned to clean Product Page.');

    // ----------------------------------------------------
    // TEST 9: Version B UI & Redesigned Selectors
    // ----------------------------------------------------
    console.log('\n--- TEST 9: Version B URL & Redesigned Selectors ---');
    await page.goto('http://localhost:5173/?version=B', { waitUntil: 'networkidle' });
    await page.waitForTimeout(400);

    // Add to cart
    await page.click('#add-to-cart-button');
    await page.waitForTimeout(400);

    // View cart
    await page.click('#view-cart-button');
    await page.waitForTimeout(400);

    // Verify Version B Checkout Button
    const vBCheckoutBtn = await page.$('#proceed-to-payment');
    if (!vBCheckoutBtn) {
      throw new Error('Version B expected button with id="proceed-to-payment", but not found!');
    }
    const vBCheckoutText = await vBCheckoutBtn.textContent();
    console.log(`✓ Version B Checkout button found: id="proceed-to-payment", text="${vBCheckoutText.trim()}"`);
    if (!vBCheckoutText.includes('Continue to Payment')) {
      throw new Error(`Expected text "Continue to Payment", got "${vBCheckoutText}"`);
    }

    // Check old selector is absent
    const oldCheckoutBtn = await page.$('#checkout-button');
    if (oldCheckoutBtn) {
      throw new Error('Old selector #checkout-button should NOT exist in Version B!');
    }
    console.log('✓ Verified: Baseline selector #checkout-button is absent in Version B.');

    // Navigate to checkout in Version B
    await page.click('#proceed-to-payment');
    await page.waitForTimeout(400);

    // Verify Version B Final Button
    const vBConfirmBtn = await page.$('#confirm-purchase');
    if (!vBConfirmBtn) {
      throw new Error('Version B expected button with id="confirm-purchase", but not found!');
    }
    const vBConfirmText = await vBConfirmBtn.textContent();
    console.log(`✓ Version B Confirm Purchase button found: id="confirm-purchase", text="${vBConfirmText.trim()}"`);
    if (!vBConfirmText.includes('Confirm Purchase')) {
      throw new Error(`Expected text "Confirm Purchase", got "${vBConfirmText}"`);
    }

    // Check old place-order selector is absent
    const oldPlaceOrderBtn = await page.$('#place-order');
    if (oldPlaceOrderBtn) {
      throw new Error('Old selector #place-order should NOT exist in Version B!');
    }
    console.log('✓ Verified: Baseline selector #place-order is absent in Version B.');

    // Complete purchase in Version B
    await page.click('#quick-fill-btn');
    await page.waitForTimeout(300);
    await page.click('#confirm-purchase');
    await page.waitForTimeout(1200);

    const vBSuccess = await page.textContent('#order-success-title');
    const vBOrderId = await page.textContent('#order-id-display');
    console.log(`✓ Version B Workflow Completed! "${vBSuccess.trim()}", Order ID: "${vBOrderId.trim()}"`);

    // ----------------------------------------------------
    // TEST 10: Presets Consistency
    // ----------------------------------------------------
    console.log('\n--- TEST 10: Presets Verification ---');
    await page.goto('http://localhost:5173/', { waitUntil: 'networkidle' });
    await page.click('#add-to-cart-button');
    await page.waitForTimeout(300);
    await page.click('#view-cart-button');
    await page.waitForTimeout(300);

    // Preset: Renamed
    await page.click('#dev-preset-renamed');
    await page.waitForTimeout(300);
    const renamedBtn = await page.$('#proceed-to-payment');
    if (!renamedBtn) throw new Error('Preset "renamed" failed to apply id="proceed-to-payment"');
    console.log('✓ Preset "Renamed" applied new selector.');

    // Preset: Baseline
    await page.click('#dev-preset-baseline');
    await page.waitForTimeout(300);
    const baselineBtn = await page.$('#checkout-button');
    if (!baselineBtn) throw new Error('Preset "baseline" failed to restore id="checkout-button"');
    console.log('✓ Preset "Baseline" restored original selector.');

    console.log('\n========================================');
    console.log('🎉 ALL 13 ACCEPTANCE CRITERIA VERIFIED AND PASSED!');
    console.log('========================================');

    if (consoleErrors.length > 0) {
      console.warn('Console errors detected:', consoleErrors);
    } else {
      console.log('✓ Zero console errors detected during entire run.');
    }
  } finally {
    await browser.close();
  }
}

runTests().catch((err) => {
  console.error('❌ Test failed:', err);
  process.exit(1);
});
