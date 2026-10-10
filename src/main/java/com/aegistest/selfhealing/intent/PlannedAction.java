package com.aegistest.selfhealing.intent;

public class PlannedAction {
    public enum ActionType {
        NAVIGATE,
        CLICK,
        FILL,
        SELECT,
        ASSERT_VISIBLE,
        ASSERT_TEXT
    }

    private int stepNumber;
    private ActionType actionType;
    private String targetDescription;
    private String locatorHint; // Primary suggested locator (e.g. #checkout-button)
    private String value; // Value to fill or select
    private String valueReference; // Data reference like testCustomer.email

    public PlannedAction() {}

    public PlannedAction(int stepNumber, ActionType actionType, String targetDescription, String locatorHint, String value) {
        this.stepNumber = stepNumber;
        this.actionType = actionType;
        this.targetDescription = targetDescription;
        this.locatorHint = locatorHint;
        this.value = value;
    }

    public int getStepNumber() { return stepNumber; }
    public void setStepNumber(int stepNumber) { this.stepNumber = stepNumber; }

    public ActionType getActionType() { return actionType; }
    public void setActionType(ActionType actionType) { this.actionType = actionType; }

    public String getTargetDescription() { return targetDescription; }
    public void setTargetDescription(String targetDescription) { this.targetDescription = targetDescription; }

    public String getLocatorHint() { return locatorHint; }
    public void setLocatorHint(String locatorHint) { this.locatorHint = locatorHint; }

    public String getValue() { return value; }
    public void setValue(String value) { this.value = value; }

    public String getValueReference() { return valueReference; }
    public void setValueReference(String valueReference) { this.valueReference = valueReference; }
}
