package com.aegistest.selfhealing.inspection;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.microsoft.playwright.Page;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

@Component
public class PageInspector {

    private static final Logger log = LoggerFactory.getLogger(PageInspector.class);
    private final ObjectMapper objectMapper;

    public PageInspector(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;
    }

    /**
     * Inspects the current Playwright page, introspecting all interactive elements.
     */
    public PageSnapshot inspect(Page page) {
        String url = page.url();
        String title = page.title();
        PageSnapshot snapshot = new PageSnapshot(url, title);

        try {
            // Script that extracts rich element semantics
            String extractionScript = """
                () => {
                    const elements = [];
                    const targets = document.querySelectorAll('button, input, select, textarea, a[href], [role="button"], [role="link"], [data-testid]');

                    targets.forEach((el, index) => {
                        const rect = el.getBoundingClientRect();
                        const isVisible = !!(rect.width || rect.height || el.getClientRects().length) && window.getComputedStyle(el).visibility !== 'hidden' && window.getComputedStyle(el).display !== 'none';
                        const isEnabled = !el.disabled;

                        // Find associated label
                        let labelText = '';
                        if (el.id) {
                            const lbl = document.querySelector('label[for="' + el.id + '"]');
                            if (lbl) labelText = lbl.innerText.trim();
                        }
                        if (!labelText && el.closest('label')) {
                            labelText = el.closest('label').innerText.trim();
                        }

                        // Collect attributes
                        const attrs = {};
                        for (let attr of el.attributes) {
                            attrs[attr.name] = attr.value;
                        }

                        // Parent hierarchy context
                        const parent = el.parentElement;
                        const parentTag = parent ? parent.tagName.toLowerCase() : '';
                        const containerClass = parent ? (parent.className || '') : '';

                        elements.push({
                            tag: el.tagName.toLowerCase(),
                            role: el.getAttribute('role') || (el.tagName.toLowerCase() === 'button' ? 'button' : (el.tagName.toLowerCase() === 'input' ? 'textbox' : '')),
                            accessibleName: el.getAttribute('aria-label') || el.title || labelText || el.innerText || el.value || '',
                            associatedLabel: labelText,
                            visibleText: (el.innerText || '').trim(),
                            inputType: el.getAttribute('type') || (el.tagName.toLowerCase() === 'input' ? 'text' : ''),
                            placeholder: el.getAttribute('placeholder') || '',
                            safeValue: (el.type === 'password' || el.name === 'cardNumber') ? '***' : (el.value || ''),
                            visible: isVisible,
                            enabled: isEnabled,
                            parentTag: parentTag,
                            containerClass: containerClass,
                            testId: el.getAttribute('data-testid') || el.getAttribute('data-test') || '',
                            id: el.id || '',
                            name: el.name || '',
                            cssClasses: el.className || '',
                            attributes: attrs,
                            x: rect.x,
                            y: rect.y,
                            width: rect.width,
                            height: rect.height
                        });
                    });

                    return {
                        domHtml: document.body ? document.body.innerHTML : '',
                        elements: elements
                    };
                }
            """;

            Object evalResult = page.evaluate(extractionScript);
            JsonNode rootNode = objectMapper.valueToTree(evalResult);

            if (rootNode.has("domHtml")) {
                snapshot.setDomHtml(rootNode.get("domHtml").asText());
            }

            if (rootNode.has("elements") && rootNode.get("elements").isArray()) {
                List<InspectedElement> inspectedList = new ArrayList<>();
                for (JsonNode elNode : rootNode.get("elements")) {
                    InspectedElement item = new InspectedElement();
                    item.setTag(elNode.path("tag").asText());
                    item.setRole(elNode.path("role").asText());
                    item.setAccessibleName(elNode.path("accessibleName").asText().trim());
                    item.setAssociatedLabel(elNode.path("associatedLabel").asText().trim());
                    item.setVisibleText(elNode.path("visibleText").asText().trim());
                    item.setInputType(elNode.path("inputType").asText());
                    item.setPlaceholder(elNode.path("placeholder").asText());
                    item.setSafeValue(elNode.path("safeValue").asText());
                    item.setVisible(elNode.path("visible").asBoolean(true));
                    item.setEnabled(elNode.path("enabled").asBoolean(true));
                    item.setParentTag(elNode.path("parentTag").asText());
                    item.setContainerClass(elNode.path("containerClass").asText());
                    item.setTestId(elNode.path("testId").asText());
                    item.setId(elNode.path("id").asText());
                    item.setName(elNode.path("name").asText());
                    item.setCssClasses(elNode.path("cssClasses").asText());
                    item.setX(elNode.path("x").asDouble());
                    item.setY(elNode.path("y").asDouble());
                    item.setWidth(elNode.path("width").asDouble());
                    item.setHeight(elNode.path("height").asDouble());

                    if (elNode.has("attributes")) {
                        Map<String, String> attrMap = new HashMap<>();
                        Iterator<Map.Entry<String, JsonNode>> fields = elNode.get("attributes").fields();
                        while (fields.hasNext()) {
                            Map.Entry<String, JsonNode> entry = fields.next();
                            attrMap.put(entry.getKey(), entry.getValue().asText());
                        }
                        item.setAttributes(attrMap);
                    }

                    // Compute locators in priority order
                    computeLocators(item);
                    inspectedList.add(item);
                }
                snapshot.setElements(inspectedList);
            }
        } catch (Exception e) {
            log.error("Error inspecting page: {}", e.getMessage(), e);
        }

        return snapshot;
    }

    private void computeLocators(InspectedElement item) {
        // 1. Stable test id
        if (item.getTestId() != null && !item.getTestId().isEmpty()) {
            item.setTestIdLocator("[data-testid=\"" + item.getTestId() + "\"]");
            item.setPrimaryLocator(item.getTestIdLocator());
            return;
        }

        // 2. ID
        if (item.getId() != null && !item.getId().isEmpty()) {
            item.setCssLocator("#" + item.getId());
            item.setPrimaryLocator("#" + item.getId());
            return;
        }

        // 3. Accessible role and name
        if (item.getAccessibleName() != null && !item.getAccessibleName().isEmpty() && item.getRole() != null && !item.getRole().isEmpty()) {
            item.setAccessibleLocator("role=" + item.getRole() + "[name=\"" + item.getAccessibleName() + "\"]");
            if (item.getPrimaryLocator() == null) item.setPrimaryLocator(item.getAccessibleLocator());
        }

        // 4. Visible text
        if (item.getVisibleText() != null && !item.getVisibleText().isEmpty() && item.getVisibleText().length() < 40) {
            item.setTextLocator("text=\"" + item.getVisibleText() + "\"");
            if (item.getPrimaryLocator() == null) item.setPrimaryLocator(item.getTextLocator());
        }

        // 5. Input name or placeholder
        if ("input".equalsIgnoreCase(item.getTag())) {
            if (item.getName() != null && !item.getName().isEmpty()) {
                item.setPrimaryLocator("input[name=\"" + item.getName() + "\"]");
            } else if (item.getPlaceholder() != null && !item.getPlaceholder().isEmpty()) {
                item.setPrimaryLocator("input[placeholder=\"" + item.getPlaceholder() + "\"]");
            }
        }

        // Fallback CSS
        if (item.getPrimaryLocator() == null) {
            if (item.getCssClasses() != null && !item.getCssClasses().isEmpty()) {
                String firstClass = item.getCssClasses().split("\\s+")[0];
                item.setPrimaryLocator(item.getTag() + "." + firstClass);
            } else {
                item.setPrimaryLocator(item.getTag());
            }
        }
    }
}
