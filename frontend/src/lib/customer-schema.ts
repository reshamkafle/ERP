import { z } from "zod"

export const customerFormSchema = z.object({
  name: z.string().min(1, "Name is required").max(255),
  phone: z.string().max(64).optional(),
  email: z
    .string()
    .email("Enter a valid email")
    .optional()
    .or(z.literal("")),
  notes: z.string().optional(),
})

export type CustomerFormValues = z.infer<typeof customerFormSchema>
