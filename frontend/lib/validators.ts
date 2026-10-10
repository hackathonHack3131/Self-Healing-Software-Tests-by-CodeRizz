import { z } from "zod";

export const testCaseFormSchema = z.object({
  name: z.string().min(3, "Test name must be at least 3 characters").max(100, "Test name too long"),
  targetUrl: z.string().url("Please provide a valid URL (e.g. https://shop.demo.com or http://localhost:5173)"),
  intent: z.string().min(10, "Please describe the test intent with at least 10 characters (e.g., 'Complete checkout with a valid credit card')"),
  environment: z.enum(["local", "staging", "production"]),
  browser: z.enum(["chromium", "firefox", "webkit"]),
  selfHealingEnabled: z.boolean().default(true),
  maxHealingAttempts: z.number().min(1).max(10).default(3),
  expectedOutcome: z.string().min(5, "Expected outcome description is required"),
  testDataJson: z.string().optional(),
});

export type TestCaseFormValues = z.infer<typeof testCaseFormSchema>;

export const settingsFormSchema = z.object({
  backendUrl: z.string().url("Must be a valid URL"),
  defaultBrowser: z.enum(["chromium", "firefox", "webkit"]),
  defaultEnvironment: z.enum(["local", "staging", "production"]),
  selfHealingEnabled: z.boolean(),
  confidenceThreshold: z.number().min(0.5).max(1.0),
  maxHealingAttempts: z.number().min(1).max(10),
  captureScreenshots: z.boolean(),
  demoModeSimulation: z.boolean(),
});

export type SettingsFormValues = z.infer<typeof settingsFormSchema>;

// Custom lightweight Zod resolver for react-hook-form
export function createZodResolver<T extends z.ZodType<any, any>>(schema: T) {
  return async (values: any) => {
    const result = schema.safeParse(values);
    if (result.success) {
      return { values: result.data, errors: {} };
    }
    const errors: Record<string, any> = {};
    for (const issue of result.error.issues) {
      const field = issue.path[0] as string;
      if (!errors[field]) {
        errors[field] = { type: issue.code, message: issue.message };
      }
    }
    return { values: {}, errors };
  };
}
