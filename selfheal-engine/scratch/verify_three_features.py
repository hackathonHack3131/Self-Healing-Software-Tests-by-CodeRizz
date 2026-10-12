import asyncio
from playwright.async_api import async_playwright

async def verify_three_features():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1366, "height": 900})

        print("Navigating to http://127.0.0.1:8080/ ...")
        await page.goto("http://127.0.0.1:8080/")
        await page.wait_for_timeout(1000)

        # ----------------------------------------------------
        # FEATURE 1: INTERACTIVE TESTING LAB
        # ----------------------------------------------------
        print("\n--- Verifying Feature 1: Interactive Testing Lab ---")
        scenarios_sec = await page.query_selector("#scenarios-section")
        assert scenarios_sec is not None, "Feature 1 section #scenarios-section not found"

        # Check all 4 scenario cards exist
        card_a = await page.query_selector('.scenario-interactive-card[data-version="a"]')
        card_b = await page.query_selector('.scenario-interactive-card[data-version="b"]')
        card_c = await page.query_selector('.scenario-interactive-card[data-version="c"]')
        card_d = await page.query_selector('.scenario-interactive-card[data-version="d"]')
        assert card_a and card_b and card_c and card_d, "One or more scenario cards missing"

        # Check default selection is A
        selected_card = await page.evaluate('document.querySelector(".scenario-interactive-card.selected").dataset.version')
        assert selected_card == 'a', f"Expected default 'a', got {selected_card}"

        # Invariants populated for A
        invariants_a = await page.inner_text("#detailInvariants")
        print(f"Version A Invariants text:\n{invariants_a.strip()}")
        assert "ORD-[0-9]{5}" in invariants_a, "Expected order ID invariant in Version A"
        assert "$36.50" in invariants_a, "Expected total $36.50 in Version A"

        # Select Version B
        await card_b.click()
        await page.wait_for_timeout(200)
        title_b = await page.inner_text("#detailPanelTitle")
        badge_b = await page.inner_text("#detailPanelBadge")
        invariants_b = await page.inner_text("#detailInvariants")
        print(f"Version B Title: {title_b}")
        print(f"Version B Badge: {badge_b}")
        assert "PASS_AFTER_HEAL" in badge_b
        assert "4 wizard steps" in invariants_b

        # Select Version C
        await card_c.click()
        await page.wait_for_timeout(200)
        badge_c = await page.inner_text("#detailPanelBadge")
        invariants_c = await page.inner_text("#detailInvariants")
        print(f"Version C Badge: {badge_c}")
        assert "FAIL_FUNCTIONAL" in badge_c
        assert "APP_BUG" in invariants_c

        # Select Version D
        await card_d.click()
        await page.wait_for_timeout(200)
        badge_d = await page.inner_text("#detailPanelBadge")
        invariants_d = await page.inner_text("#detailInvariants")
        print(f"Version D Badge: {badge_d}")
        assert "FAIL_FUNCTIONAL" in badge_d
        assert "$32.50 != $36.50" in invariants_d

        # Filter pills for scenarios
        await page.click('.scenario-filter-bar button[data-filter="pass"]')
        await page.wait_for_timeout(200)
        count_pass = await page.inner_text("#scenarioFilterCount")
        print(f"Pass filter count: {count_pass}")
        assert "Showing 2 of 4" in count_pass

        await page.click('.scenario-filter-bar button[data-filter="all"]')
        await page.wait_for_timeout(200)
        count_all = await page.inner_text("#scenarioFilterCount")
        assert "Showing 4 of 4" in count_all

        # Screenshot Feature 1
        await scenarios_sec.scroll_into_view_if_needed()
        await page.screenshot(path="scratch/feature1_lab.png")
        print("Feature 1 screenshot captured: scratch/feature1_lab.png")

        # ----------------------------------------------------
        # FEATURE 2: UI DRIFT VISUALIZER
        # ----------------------------------------------------
        print("\n--- Verifying Feature 2: UI Drift Visualizer ---")
        drift_sec = await page.query_selector("#drift-visualizer-section")
        assert drift_sec is not None, "Feature 2 section #drift-visualizer-section not found"

        # Check default layout: side-by-side
        orig_card = await page.query_selector("#driftOriginalCard")
        redesign_card = await page.query_selector("#driftRedesignedCard")
        assert await orig_card.is_visible(), "Version A card should be visible in side-by-side"
        assert await redesign_card.is_visible(), "Version B card should be visible in side-by-side"

        # Step navigation in Version B mockup
        # Step 1: Cart
        step1_fields = await page.inner_text("#wizardStepFields")
        print(f"Wizard Step 1 fields:\n{step1_fields.strip()}")
        assert "$30.00" in step1_fields

        # Step 2: Shipping
        await page.click("#stepShippingPill")
        await page.wait_for_timeout(200)
        step2_fields = await page.inner_text("#wizardStepFields")
        print(f"Wizard Step 2 fields:\n{step2_fields.strip()}")
        assert "Recipient Full Name" in step2_fields

        # Step 3: Payment
        await page.click("#stepPaymentPill")
        await page.wait_for_timeout(200)
        step3_fields = await page.inner_text("#wizardStepFields")
        print(f"Wizard Step 3 fields:\n{step3_fields.strip()}")
        assert "4242" in step3_fields

        # Step 4: Review
        await page.click("#stepReviewPill")
        await page.wait_for_timeout(200)
        step4_fields = await page.inner_text("#wizardStepFields")
        print(f"Wizard Step 4 fields:\n{step4_fields.strip()}")
        assert "Place Order" in step4_fields

        # Layout switching
        # View Version A only
        await page.click("#btnViewVersionA")
        await page.wait_for_timeout(200)
        assert await orig_card.is_visible(), "Version A card should be visible"
        assert not await redesign_card.is_visible(), "Version B card should be hidden in Version A view"

        # View Version B only
        await page.click("#btnViewVersionB")
        await page.wait_for_timeout(200)
        assert not await orig_card.is_visible(), "Version A card should be hidden in Version B view"
        assert await redesign_card.is_visible(), "Version B card should be visible"

        # Return to side-by-side
        await page.click("#btnViewSideBySide")
        await page.wait_for_timeout(200)
        assert await orig_card.is_visible() and await redesign_card.is_visible(), "Both cards should be visible again"

        # Screenshot Feature 2
        await drift_sec.scroll_into_view_if_needed()
        await page.screenshot(path="scratch/feature2_drift.png")
        print("Feature 2 screenshot captured: scratch/feature2_drift.png")

        # ----------------------------------------------------
        # FEATURE 3: FAILURE DIAGNOSIS CENTER
        # ----------------------------------------------------
        print("\n--- Verifying Feature 3: Failure Diagnosis Center ---")
        diag_sec = await page.query_selector("#diagnosis-center-section")
        assert diag_sec is not None, "Feature 3 section #diagnosis-center-section not found"

        # Verify all 9 cards exist
        diag_cards = await page.query_selector_all(".diagnosis-card")
        print(f"Number of diagnosis cards found: {len(diag_cards)}")
        assert len(diag_cards) == 9, f"Expected 9 cards, found {len(diag_cards)}"

        # Default card: PASS_NO_HEAL
        default_diag = await page.evaluate('document.querySelector(".diagnosis-card.selected").dataset.code')
        assert default_diag == "PASS_NO_HEAL", f"Expected PASS_NO_HEAL, got {default_diag}"

        # Click FAIL_FUNCTIONAL
        card_ff = await page.query_selector('.diagnosis-card[data-code="FAIL_FUNCTIONAL"]')
        await card_ff.click()
        await page.wait_for_timeout(200)
        diag_badge = await page.inner_text("#diagDetailBadge")
        diag_rule = await page.inner_text("#diagDetailRule")
        diag_safety = await page.inner_text("#diagDetailSafety")
        print(f"Selected FAIL_FUNCTIONAL Badge: {diag_badge}")
        print(f"Rule: {diag_rule}")
        print(f"Safety: {diag_safety}")
        assert "FAIL_FUNCTIONAL" in diag_badge
        assert "Rules 1 & 3" in diag_rule
        assert "refused" in diag_safety.lower()

        # Click BLOCKED_CONFIG
        card_bc = await page.query_selector('.diagnosis-card[data-code="BLOCKED_CONFIG"]')
        await card_bc.click()
        await page.wait_for_timeout(200)
        bc_badge = await page.inner_text("#diagDetailBadge")
        print(f"Selected BLOCKED_CONFIG Badge: {bc_badge}")
        assert "BLOCKED_CONFIG" in bc_badge

        # Filter Pills for Diagnosis
        await page.click('button[data-diag-filter="defect"]')
        await page.wait_for_timeout(200)
        count_defect = await page.inner_text("#diagFilterCount")
        print(f"Defect filter count: {count_defect}")
        assert "Showing 3 of 9" in count_defect

        await page.click('button[data-diag-filter="safety"]')
        await page.wait_for_timeout(200)
        count_safety = await page.inner_text("#diagFilterCount")
        print(f"Safety filter count: {count_safety}")
        assert "Showing 4 of 9" in count_safety

        await page.click('button[data-diag-filter="all"]')
        await page.wait_for_timeout(200)
        count_all_diag = await page.inner_text("#diagFilterCount")
        assert "Showing 9 of 9" in count_all_diag

        # Screenshot Feature 3
        await diag_sec.scroll_into_view_if_needed()
        await page.screenshot(path="scratch/feature3_diagnosis.png")
        print("Feature 3 screenshot captured: scratch/feature3_diagnosis.png")

        # ----------------------------------------------------
        # RESPONSIVE OVERFLOW CHECK
        # ----------------------------------------------------
        print("\n--- Verifying Responsive Overflow ---")
        has_h_overflow_desktop = await page.evaluate('document.documentElement.scrollWidth > window.innerWidth')
        print(f"Desktop (1366px) horizontal overflow: {has_h_overflow_desktop}")
        assert not has_h_overflow_desktop, "Desktop has horizontal overflow"

        await page.set_viewport_size({"width": 375, "height": 812})
        await page.wait_for_timeout(300)

        f1_overflow = await page.evaluate('document.getElementById("scenarios-section").scrollWidth > document.getElementById("scenarios-section").clientWidth')
        f2_overflow = await page.evaluate('document.getElementById("drift-visualizer-section").scrollWidth > document.getElementById("drift-visualizer-section").clientWidth')
        f3_overflow = await page.evaluate('document.getElementById("diagnosis-center-section").scrollWidth > document.getElementById("diagnosis-center-section").clientWidth')
        f1_width_overflow = await page.evaluate('document.getElementById("scenarios-section").scrollWidth > 375')
        f2_width_overflow = await page.evaluate('document.getElementById("drift-visualizer-section").scrollWidth > 375')
        f3_width_overflow = await page.evaluate('document.getElementById("diagnosis-center-section").scrollWidth > 375')
        print(f"Feature 1 mobile internal overflow: {f1_overflow}, width overflow: {f1_width_overflow}")
        print(f"Feature 2 mobile internal overflow: {f2_overflow}, width overflow: {f2_width_overflow}")
        print(f"Feature 3 mobile internal overflow: {f3_overflow}, width overflow: {f3_width_overflow}")
        assert not f1_overflow and not f1_width_overflow, "Feature 1 has horizontal overflow on mobile"
        assert not f2_overflow and not f2_width_overflow, "Feature 2 has horizontal overflow on mobile"
        assert not f3_overflow and not f3_width_overflow, "Feature 3 has horizontal overflow on mobile"

        await browser.close()
        print("\n==========================================")
        print("ALL VERIFICATIONS COMPLETED SUCCESSFULLY!")
        print("==========================================")

if __name__ == "__main__":
    asyncio.run(verify_three_features())
