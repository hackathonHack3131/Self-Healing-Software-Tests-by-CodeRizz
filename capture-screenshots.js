import { chromium } from 'playwright';
import path from 'path';

const ARTIFACT_DIR = 'C:/Users/ratho/.gemini/antigravity-ide/brain/79a494a4-4317-425e-93ce-915a68f4dafb';

async function capture() {
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  const context = await browser.newContext({ viewport: { width: 1280, height: 850 } });
  const page = await context.newPage();

  // 1. Product Page Version A
  await page.goto('http://localhost:5173/?version=A', { waitUntil: 'networkidle' });
  await page.screenshot({ path: path.join(ARTIFACT_DIR, 'screen_01_product_page_va.png'), fullPage: false });
  console.log('Captured screen_01_product_page_va.png');

  // Add to cart and view Cart
  await page.click('#add-to-cart-button');
  await page.waitForTimeout(400);
  await page.click('#view-cart-button');
  await page.waitForTimeout(400);
  await page.screenshot({ path: path.join(ARTIFACT_DIR, 'screen_02_cart_page_va.png'), fullPage: false });
  console.log('Captured screen_02_cart_page_va.png');

  // Checkout Page Version A
  await page.click('#checkout-button');
  await page.waitForTimeout(400);
  await page.click('#quick-fill-btn');
  await page.waitForTimeout(400);
  await page.screenshot({ path: path.join(ARTIFACT_DIR, 'screen_03_checkout_va.png'), fullPage: false });
  console.log('Captured screen_03_checkout_va.png');

  // Payment Failure Banner
  await page.click('#simulate-payment-failure-toggle');
  await page.waitForTimeout(300);
  await page.click('#place-order');
  await page.waitForTimeout(1000);
  await page.screenshot({ path: path.join(ARTIFACT_DIR, 'screen_04_payment_failure.png'), fullPage: false });
  console.log('Captured screen_04_payment_failure.png');

  // Order Confirmation
  await page.click('#simulate-payment-failure-toggle');
  await page.waitForTimeout(300);
  await page.click('#place-order');
  await page.waitForTimeout(1200);
  await page.screenshot({ path: path.join(ARTIFACT_DIR, 'screen_05_order_confirmation.png'), fullPage: false });
  console.log('Captured screen_05_order_confirmation.png');

  // Version B Cart & Checkout
  await page.goto('http://localhost:5173/?version=B', { waitUntil: 'networkidle' });
  await page.click('#add-to-cart-button');
  await page.waitForTimeout(400);
  await page.click('#view-cart-button');
  await page.waitForTimeout(400);
  await page.screenshot({ path: path.join(ARTIFACT_DIR, 'screen_06_cart_page_vb.png'), fullPage: false });
  console.log('Captured screen_06_cart_page_vb.png');

  await page.click('#proceed-to-payment');
  await page.waitForTimeout(400);
  await page.click('#quick-fill-btn');
  await page.waitForTimeout(400);
  await page.screenshot({ path: path.join(ARTIFACT_DIR, 'screen_07_checkout_vb.png'), fullPage: false });
  console.log('Captured screen_07_checkout_vb.png');

  await browser.close();
  console.log('All screenshots captured successfully!');
}

capture().catch(console.error);
