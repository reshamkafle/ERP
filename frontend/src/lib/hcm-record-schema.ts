import { z } from "zod"

import type { ModuleRecord } from "@/types/module"

const optionalStr = z.string()

export const HCM_MODULE_CODE = "hcm"

export const HCM_STATUS_OPTIONS = [
  "DRAFT",
  "ACTIVE",
  "ON_LEAVE",
  "IN_PROGRESS",
  "COMPLETED",
  "APPROVED",
  "TERMINATED",
  "RETIRED",
  "REJECTED",
  "CANCELLED",
] as const

// --- Repeatable row schemas ---

export const emergencyContactSchema = z.object({
  name: optionalStr,
  relationship: optionalStr,
  phone: optionalStr,
})

export const salaryComponentSchema = z.object({
  component_type: optionalStr,
  description: optionalStr,
  amount: optionalStr,
})

export const certificationSchema = z.object({
  name: optionalStr,
  issuer: optionalStr,
  expiry_date: optionalStr,
})

export const languageSkillSchema = z.object({
  language: optionalStr,
  proficiency: optionalStr,
})

export const previousEmploymentSchema = z.object({
  employer: optionalStr,
  job_title: optionalStr,
  start_date: optionalStr,
  end_date: optionalStr,
  notes: optionalStr,
})

export const internalHistorySchema = z.object({
  event_type: optionalStr,
  effective_date: optionalStr,
  from_value: optionalStr,
  to_value: optionalStr,
  notes: optionalStr,
})

export const dependentSchema = z.object({
  name: optionalStr,
  relationship: optionalStr,
  date_of_birth: optionalStr,
})

export const payrollLineSchema = z.object({
  element_code: optionalStr,
  description: optionalStr,
  amount: optionalStr,
  deduction: optionalStr,
})

export const interviewScoreSchema = z.object({
  interviewer: optionalStr,
  round: optionalStr,
  score: optionalStr,
  notes: optionalStr,
})

export const leaveRequestSchema = z.object({
  leave_type: optionalStr,
  start_date: optionalStr,
  end_date: optionalStr,
  days: optionalStr,
  status: optionalStr,
})

// --- Employee Records sections ---

export const employeePersonalSchema = z.object({
  employee_id: optionalStr,
  title_prefix: optionalStr,
  first_name: optionalStr,
  middle_name: optionalStr,
  last_name: optionalStr,
  preferred_name: optionalStr,
  date_of_birth: optionalStr,
  gender: optionalStr,
  marital_status: optionalStr,
  nationality: optionalStr,
  national_id: optionalStr,
  personal_email: optionalStr,
  personal_phone: optionalStr,
  blood_group: optionalStr,
  religion_ethnicity: optionalStr,
  disability_status: optionalStr,
  photo_url: optionalStr,
})

export const employeeAddressSchema = z.object({
  permanent_address: optionalStr,
  mailing_address: optionalStr,
  city: optionalStr,
  state: optionalStr,
  country: optionalStr,
  postal_code: optionalStr,
  emergency_address: optionalStr,
})

export const employeeEmploymentSchema = z.object({
  employment_type: optionalStr,
  employee_status: optionalStr,
  hire_date: optionalStr,
  confirmation_date: optionalStr,
  probation_end: optionalStr,
  department: optionalStr,
  job_title: optionalStr,
  job_code: optionalStr,
  grade: optionalStr,
  reporting_manager_id: optionalStr,
  reporting_manager_name: optionalStr,
  location: optionalStr,
  cost_center: optionalStr,
  legal_entity: optionalStr,
  business_unit: optionalStr,
  work_shift: optionalStr,
  union_membership: optionalStr,
})

export const employeeOrgPositionSchema = z.object({
  position_id: optionalStr,
  reports_to_position: optionalStr,
  job_family: optionalStr,
  org_unit: optionalStr,
  matrix_manager: optionalStr,
})

export const employeeCompensationSchema = z.object({
  basic_salary: optionalStr,
  pay_frequency: optionalStr,
  currency: optionalStr,
  bank_account_number: optionalStr,
  bank_name: optionalStr,
  iban: optionalStr,
  swift: optionalStr,
  payment_method: optionalStr,
  tax_withholding_status: optionalStr,
  provident_fund_id: optionalStr,
  bonus_eligibility: optionalStr,
  last_raise_date: optionalStr,
  last_raise_amount: optionalStr,
})

export const employeeEducationSchema = z.object({
  highest_qualification: optionalStr,
  degree: optionalStr,
  field_of_study: optionalStr,
  institution: optionalStr,
  year_of_graduation: optionalStr,
})

export const employeeExperienceSchema = z.object({
  total_years_experience: optionalStr,
})

export const employeePerformanceTalentSchema = z.object({
  performance_rating_current: optionalStr,
  performance_rating_historical: optionalStr,
  last_appraisal_date: optionalStr,
  next_appraisal_due: optionalStr,
  talent_category: optionalStr,
  succession_plan: optionalStr,
  skills_competencies: optionalStr,
  training_history: optionalStr,
  development_plan: optionalStr,
})

export const employeeTimeAttendanceSchema = z.object({
  leave_entitlement_annual: optionalStr,
  leave_entitlement_sick: optionalStr,
  leave_entitlement_maternity: optionalStr,
  leave_balance: optionalStr,
  attendance_tracking_method: optionalStr,
  shift_roster: optionalStr,
})

export const employeeBenefitsEntitlementsSchema = z.object({
  health_insurance_plan_id: optionalStr,
  life_insurance: optionalStr,
  benefit_enrollment_status: optionalStr,
  company_car_asset: optionalStr,
})

export const employeeTerminationSchema = z.object({
  termination_date: optionalStr,
  separation_reason: optionalStr,
  notice_period: optionalStr,
  exit_interview_date: optionalStr,
  exit_interview_notes: optionalStr,
  final_settlement_date: optionalStr,
  final_settlement_amount: optionalStr,
})

export const employeeSystemComplianceSchema = z.object({
  approval_workflow_status: optionalStr,
  data_privacy_consent: optionalStr,
  audit_change_log: optionalStr,
  integration_active_directory: optionalStr,
  integration_payroll: optionalStr,
  integration_benefits: optionalStr,
})

export const employeeCountrySpecificSchema = z.object({
  visa_work_permit: optionalStr,
  visa_expiry: optionalStr,
  dependent_visa_info: optionalStr,
  tax_residency_status: optionalStr,
  local_id_number: optionalStr,
  race_ethnicity_compliance: optionalStr,
  military_service: optionalStr,
})

export const employeeRecordsSchema = z.object({
  personal: employeePersonalSchema,
  emergency_contacts: z.array(emergencyContactSchema),
  address: employeeAddressSchema,
  employment: employeeEmploymentSchema,
  org_position: employeeOrgPositionSchema,
  compensation: employeeCompensationSchema,
  salary_components: z.array(salaryComponentSchema),
  education: employeeEducationSchema,
  certifications: z.array(certificationSchema),
  language_skills: z.array(languageSkillSchema),
  experience: employeeExperienceSchema,
  previous_employment: z.array(previousEmploymentSchema),
  internal_history: z.array(internalHistorySchema),
  performance_talent: employeePerformanceTalentSchema,
  time_attendance: employeeTimeAttendanceSchema,
  benefits_entitlements: employeeBenefitsEntitlementsSchema,
  dependents: z.array(dependentSchema),
  termination: employeeTerminationSchema,
  system_compliance: employeeSystemComplianceSchema,
  country_specific: employeeCountrySpecificSchema,
})

// --- Other feature schemas ---

export const payrollFeatureSchema = z.object({
  employee_reference: optionalStr,
  pay_period: optionalStr,
  pay_run_id: optionalStr,
  gross_pay: optionalStr,
  net_pay: optionalStr,
  currency: optionalStr,
  payment_status: optionalStr,
  statutory_deductions: optionalStr,
  tax_calculations: optionalStr,
  payslip_elements: z.array(payrollLineSchema),
})

export const recruitmentFeatureSchema = z.object({
  requisition_id: optionalStr,
  candidate_name: optionalStr,
  candidate_email: optionalStr,
  candidate_profile: optionalStr,
  stage: optionalStr,
  offer_letter_ref: optionalStr,
  onboarding_checklist: optionalStr,
  documents_assigned: optionalStr,
  training_assigned: optionalStr,
  interview_scores: z.array(interviewScoreSchema),
})

export const performanceFeatureSchema = z.object({
  employee_reference: optionalStr,
  review_cycle: optionalStr,
  goals: optionalStr,
  kpis: optionalStr,
  review_rating: optionalStr,
  feedback_360: optionalStr,
  last_appraisal_date: optionalStr,
  next_appraisal_due: optionalStr,
  talent_category: optionalStr,
  succession_readiness: optionalStr,
  career_path: optionalStr,
})

export const trainingFeatureSchema = z.object({
  employee_reference: optionalStr,
  course_catalog_id: optionalStr,
  course_name: optionalStr,
  enrollment_date: optionalStr,
  completion_status: optionalStr,
  completion_date: optionalStr,
  development_plan: optionalStr,
  certifications: z.array(certificationSchema),
})

export const timeAttendanceFeatureSchema = z.object({
  employee_reference: optionalStr,
  timesheet_period: optionalStr,
  overtime_hours: optionalStr,
  absences: optionalStr,
  leave_balance_snapshot: optionalStr,
  shift_roster: optionalStr,
  tracking_method: optionalStr,
  leave_requests: z.array(leaveRequestSchema),
})

export const benefitsFeatureSchema = z.object({
  employee_reference: optionalStr,
  health_plan_id: optionalStr,
  life_insurance_plan: optionalStr,
  enrollment_status: optionalStr,
  effective_date: optionalStr,
  company_car_asset: optionalStr,
  dependents_summary: optionalStr,
  dependents: z.array(dependentSchema),
})

export const hcmFormSchema = z.object({
  feature_code: z.string().min(1),
  reference: z.string().min(1).max(64),
  title: z.string().min(1).max(255),
  status: z.string().min(1).max(32),
  description: optionalStr,
  party_name: optionalStr,
  amount: optionalStr,
  quantity: optionalStr,
  start_date: optionalStr,
  end_date: optionalStr,
  employee: employeeRecordsSchema,
  payroll: payrollFeatureSchema,
  recruitment: recruitmentFeatureSchema,
  performance: performanceFeatureSchema,
  training: trainingFeatureSchema,
  time_attendance: timeAttendanceFeatureSchema,
  benefits: benefitsFeatureSchema,
})

export type HcmFormValues = z.infer<typeof hcmFormSchema>
export type EmergencyContact = z.infer<typeof emergencyContactSchema>
export type SalaryComponent = z.infer<typeof salaryComponentSchema>
export type Certification = z.infer<typeof certificationSchema>
export type LanguageSkill = z.infer<typeof languageSkillSchema>
export type PreviousEmployment = z.infer<typeof previousEmploymentSchema>
export type InternalHistory = z.infer<typeof internalHistorySchema>
export type Dependent = z.infer<typeof dependentSchema>
export type PayrollLine = z.infer<typeof payrollLineSchema>
export type InterviewScore = z.infer<typeof interviewScoreSchema>
export type LeaveRequest = z.infer<typeof leaveRequestSchema>

export const emptyEmergencyContact = (): EmergencyContact => ({
  name: "",
  relationship: "",
  phone: "",
})

export const emptySalaryComponent = (): SalaryComponent => ({
  component_type: "",
  description: "",
  amount: "",
})

export const emptyCertification = (): Certification => ({
  name: "",
  issuer: "",
  expiry_date: "",
})

export const emptyLanguageSkill = (): LanguageSkill => ({
  language: "",
  proficiency: "",
})

export const emptyPreviousEmployment = (): PreviousEmployment => ({
  employer: "",
  job_title: "",
  start_date: "",
  end_date: "",
  notes: "",
})

export const emptyInternalHistory = (): InternalHistory => ({
  event_type: "",
  effective_date: "",
  from_value: "",
  to_value: "",
  notes: "",
})

export const emptyDependent = (): Dependent => ({
  name: "",
  relationship: "",
  date_of_birth: "",
})

export const emptyPayrollLine = (): PayrollLine => ({
  element_code: "",
  description: "",
  amount: "",
  deduction: "",
})

export const emptyInterviewScore = (): InterviewScore => ({
  interviewer: "",
  round: "",
  score: "",
  notes: "",
})

export const emptyLeaveRequest = (): LeaveRequest => ({
  leave_type: "",
  start_date: "",
  end_date: "",
  days: "",
  status: "",
})

export const defaultHcmFormValues: HcmFormValues = {
  feature_code: "employee_records",
  reference: "",
  title: "",
  status: "DRAFT",
  description: "",
  party_name: "",
  amount: "",
  quantity: "",
  start_date: "",
  end_date: "",
  employee: {
    personal: {
      employee_id: "",
      title_prefix: "",
      first_name: "",
      middle_name: "",
      last_name: "",
      preferred_name: "",
      date_of_birth: "",
      gender: "",
      marital_status: "",
      nationality: "",
      national_id: "",
      personal_email: "",
      personal_phone: "",
      blood_group: "",
      religion_ethnicity: "",
      disability_status: "",
      photo_url: "",
    },
    emergency_contacts: [],
    address: {
      permanent_address: "",
      mailing_address: "",
      city: "",
      state: "",
      country: "",
      postal_code: "",
      emergency_address: "",
    },
    employment: {
      employment_type: "",
      employee_status: "",
      hire_date: "",
      confirmation_date: "",
      probation_end: "",
      department: "",
      job_title: "",
      job_code: "",
      grade: "",
      reporting_manager_id: "",
      reporting_manager_name: "",
      location: "",
      cost_center: "",
      legal_entity: "",
      business_unit: "",
      work_shift: "",
      union_membership: "",
    },
    org_position: {
      position_id: "",
      reports_to_position: "",
      job_family: "",
      org_unit: "",
      matrix_manager: "",
    },
    compensation: {
      basic_salary: "",
      pay_frequency: "",
      currency: "",
      bank_account_number: "",
      bank_name: "",
      iban: "",
      swift: "",
      payment_method: "",
      tax_withholding_status: "",
      provident_fund_id: "",
      bonus_eligibility: "",
      last_raise_date: "",
      last_raise_amount: "",
    },
    salary_components: [],
    education: {
      highest_qualification: "",
      degree: "",
      field_of_study: "",
      institution: "",
      year_of_graduation: "",
    },
    certifications: [],
    language_skills: [],
    experience: { total_years_experience: "" },
    previous_employment: [],
    internal_history: [],
    performance_talent: {
      performance_rating_current: "",
      performance_rating_historical: "",
      last_appraisal_date: "",
      next_appraisal_due: "",
      talent_category: "",
      succession_plan: "",
      skills_competencies: "",
      training_history: "",
      development_plan: "",
    },
    time_attendance: {
      leave_entitlement_annual: "",
      leave_entitlement_sick: "",
      leave_entitlement_maternity: "",
      leave_balance: "",
      attendance_tracking_method: "",
      shift_roster: "",
    },
    benefits_entitlements: {
      health_insurance_plan_id: "",
      life_insurance: "",
      benefit_enrollment_status: "",
      company_car_asset: "",
    },
    dependents: [],
    termination: {
      termination_date: "",
      separation_reason: "",
      notice_period: "",
      exit_interview_date: "",
      exit_interview_notes: "",
      final_settlement_date: "",
      final_settlement_amount: "",
    },
    system_compliance: {
      approval_workflow_status: "",
      data_privacy_consent: "",
      audit_change_log: "",
      integration_active_directory: "",
      integration_payroll: "",
      integration_benefits: "",
    },
    country_specific: {
      visa_work_permit: "",
      visa_expiry: "",
      dependent_visa_info: "",
      tax_residency_status: "",
      local_id_number: "",
      race_ethnicity_compliance: "",
      military_service: "",
    },
  },
  payroll: {
    employee_reference: "",
    pay_period: "",
    pay_run_id: "",
    gross_pay: "",
    net_pay: "",
    currency: "",
    payment_status: "",
    statutory_deductions: "",
    tax_calculations: "",
    payslip_elements: [],
  },
  recruitment: {
    requisition_id: "",
    candidate_name: "",
    candidate_email: "",
    candidate_profile: "",
    stage: "",
    offer_letter_ref: "",
    onboarding_checklist: "",
    documents_assigned: "",
    training_assigned: "",
    interview_scores: [],
  },
  performance: {
    employee_reference: "",
    review_cycle: "",
    goals: "",
    kpis: "",
    review_rating: "",
    feedback_360: "",
    last_appraisal_date: "",
    next_appraisal_due: "",
    talent_category: "",
    succession_readiness: "",
    career_path: "",
  },
  training: {
    employee_reference: "",
    course_catalog_id: "",
    course_name: "",
    enrollment_date: "",
    completion_status: "",
    completion_date: "",
    development_plan: "",
    certifications: [],
  },
  time_attendance: {
    employee_reference: "",
    timesheet_period: "",
    overtime_hours: "",
    absences: "",
    leave_balance_snapshot: "",
    shift_roster: "",
    tracking_method: "",
    leave_requests: [],
  },
  benefits: {
    employee_reference: "",
    health_plan_id: "",
    life_insurance_plan: "",
    enrollment_status: "",
    effective_date: "",
    company_car_asset: "",
    dependents_summary: "",
    dependents: [],
  },
}

function asString(v: unknown): string {
  if (v == null) return ""
  return String(v)
}

function mergeSection<T extends Record<string, string>>(
  defaults: T,
  source: Record<string, unknown> | undefined,
): T {
  const out = { ...defaults }
  if (!source) return out
  for (const key of Object.keys(defaults) as (keyof T)[]) {
    if (key in source) out[key] = asString(source[key as string]) as T[keyof T]
  }
  return out
}

function mergeArray<T extends Record<string, string>>(
  empty: () => T,
  source: unknown,
): T[] {
  if (!Array.isArray(source)) return []
  return source.map((row) => mergeSection(empty(), row as Record<string, unknown>))
}

function parseExtra(extra: Record<string, unknown> | null | undefined) {
  const emp = (extra?.employee as Record<string, unknown>) ?? {}
  const pay = (extra?.payroll as Record<string, unknown>) ?? {}
  const rec = (extra?.recruitment as Record<string, unknown>) ?? {}
  const perf = (extra?.performance as Record<string, unknown>) ?? {}
  const train = (extra?.training as Record<string, unknown>) ?? {}
  const time = (extra?.time_attendance as Record<string, unknown>) ?? {}
  const ben = (extra?.benefits as Record<string, unknown>) ?? {}

  return {
    employee: {
      personal: mergeSection(defaultHcmFormValues.employee.personal, emp.personal as Record<string, unknown>),
      emergency_contacts: mergeArray(emptyEmergencyContact, emp.emergency_contacts),
      address: mergeSection(defaultHcmFormValues.employee.address, emp.address as Record<string, unknown>),
      employment: mergeSection(defaultHcmFormValues.employee.employment, emp.employment as Record<string, unknown>),
      org_position: mergeSection(defaultHcmFormValues.employee.org_position, emp.org_position as Record<string, unknown>),
      compensation: mergeSection(defaultHcmFormValues.employee.compensation, emp.compensation as Record<string, unknown>),
      salary_components: mergeArray(emptySalaryComponent, emp.salary_components),
      education: mergeSection(defaultHcmFormValues.employee.education, emp.education as Record<string, unknown>),
      certifications: mergeArray(emptyCertification, emp.certifications),
      language_skills: mergeArray(emptyLanguageSkill, emp.language_skills),
      experience: mergeSection(defaultHcmFormValues.employee.experience, emp.experience as Record<string, unknown>),
      previous_employment: mergeArray(emptyPreviousEmployment, emp.previous_employment),
      internal_history: mergeArray(emptyInternalHistory, emp.internal_history),
      performance_talent: mergeSection(
        defaultHcmFormValues.employee.performance_talent,
        emp.performance_talent as Record<string, unknown>,
      ),
      time_attendance: mergeSection(
        defaultHcmFormValues.employee.time_attendance,
        emp.time_attendance as Record<string, unknown>,
      ),
      benefits_entitlements: mergeSection(
        defaultHcmFormValues.employee.benefits_entitlements,
        emp.benefits_entitlements as Record<string, unknown>,
      ),
      dependents: mergeArray(emptyDependent, emp.dependents),
      termination: mergeSection(defaultHcmFormValues.employee.termination, emp.termination as Record<string, unknown>),
      system_compliance: mergeSection(
        defaultHcmFormValues.employee.system_compliance,
        emp.system_compliance as Record<string, unknown>,
      ),
      country_specific: mergeSection(
        defaultHcmFormValues.employee.country_specific,
        emp.country_specific as Record<string, unknown>,
      ),
    },
    payroll: {
      ...mergeSection(
        {
          employee_reference: "",
          pay_period: "",
          pay_run_id: "",
          gross_pay: "",
          net_pay: "",
          currency: "",
          payment_status: "",
          statutory_deductions: "",
          tax_calculations: "",
        },
        pay,
      ),
      payslip_elements: mergeArray(emptyPayrollLine, pay.payslip_elements),
    },
    recruitment: {
      ...mergeSection(
        {
          requisition_id: "",
          candidate_name: "",
          candidate_email: "",
          candidate_profile: "",
          stage: "",
          offer_letter_ref: "",
          onboarding_checklist: "",
          documents_assigned: "",
          training_assigned: "",
        },
        rec,
      ),
      interview_scores: mergeArray(emptyInterviewScore, rec.interview_scores),
    },
    performance: mergeSection(defaultHcmFormValues.performance, perf),
    training: {
      ...mergeSection(
        {
          employee_reference: "",
          course_catalog_id: "",
          course_name: "",
          enrollment_date: "",
          completion_status: "",
          completion_date: "",
          development_plan: "",
        },
        train,
      ),
      certifications: mergeArray(emptyCertification, train.certifications),
    },
    time_attendance: {
      ...mergeSection(
        {
          employee_reference: "",
          timesheet_period: "",
          overtime_hours: "",
          absences: "",
          leave_balance_snapshot: "",
          shift_roster: "",
          tracking_method: "",
        },
        time,
      ),
      leave_requests: mergeArray(emptyLeaveRequest, time.leave_requests),
    },
    benefits: {
      ...mergeSection(
        {
          employee_reference: "",
          health_plan_id: "",
          life_insurance_plan: "",
          enrollment_status: "",
          effective_date: "",
          company_car_asset: "",
          dependents_summary: "",
        },
        ben,
      ),
      dependents: mergeArray(emptyDependent, ben.dependents),
    },
  }
}

export function buildEmployeeFullName(personal: {
  first_name: string
  middle_name: string
  last_name: string
  preferred_name: string
}): string {
  const parts = [personal.first_name, personal.middle_name, personal.last_name]
    .map((s) => s.trim())
    .filter(Boolean)
  if (parts.length) return parts.join(" ")
  return personal.preferred_name.trim()
}

export function recordToForm(record: ModuleRecord): HcmFormValues {
  const extra = parseExtra(record.extra_data)
  return {
    feature_code: record.feature_code,
    reference: record.reference,
    title: record.title,
    status: record.status,
    description: record.description ?? "",
    party_name: record.party_name ?? "",
    amount: record.amount != null ? String(record.amount) : "",
    quantity: record.quantity != null ? String(record.quantity) : "",
    start_date: record.start_date ?? "",
    end_date: record.end_date ?? "",
    ...extra,
  }
}

function parseOptionalNumber(value: string): number | null {
  const t = value.trim()
  if (!t) return null
  const n = Number(t)
  return Number.isFinite(n) ? n : null
}

function deriveTopLevelFromForm(values: HcmFormValues) {
  let party = values.party_name.trim()
  let amount = parseOptionalNumber(values.amount)
  let startDate = values.start_date.trim() || null
  let endDate = values.end_date.trim() || null
  let title = values.title.trim()
  let reference = values.reference.trim()

  switch (values.feature_code) {
    case "employee_records": {
      const p = values.employee.personal
      const e = values.employee.employment
      const c = values.employee.compensation
      const t = values.employee.termination
      reference = reference || p.employee_id.trim() || reference
      title = title || buildEmployeeFullName(p) || title
      party = party || e.reporting_manager_name.trim()
      amount = amount ?? parseOptionalNumber(c.basic_salary)
      startDate = startDate || e.hire_date.trim() || null
      endDate = endDate || t.termination_date.trim() || null
      break
    }
    case "payroll": {
      const pay = values.payroll
      party = party || pay.employee_reference.trim()
      amount = amount ?? parseOptionalNumber(pay.gross_pay)
      startDate = startDate || pay.pay_period.trim() || null
      break
    }
    case "recruitment": {
      const rec = values.recruitment
      title = title || rec.candidate_name.trim() || title
      reference = reference || rec.requisition_id.trim() || reference
      break
    }
    case "performance": {
      const perf = values.performance
      party = party || perf.employee_reference.trim()
      break
    }
    case "training": {
      const train = values.training
      party = party || train.employee_reference.trim()
      title = title || train.course_name.trim() || title
      break
    }
    case "time_attendance": {
      const time = values.time_attendance
      party = party || time.employee_reference.trim()
      startDate = startDate || time.timesheet_period.trim() || null
      break
    }
    case "benefits": {
      const ben = values.benefits
      party = party || ben.employee_reference.trim()
      startDate = startDate || ben.effective_date.trim() || null
      break
    }
    default:
      break
  }

  return {
    reference,
    title,
    party_name: party || null,
    amount,
    quantity: parseOptionalNumber(values.quantity),
    start_date: startDate,
    end_date: endDate,
  }
}

function extraDataFromForm(values: HcmFormValues) {
  return {
    employee: values.employee,
    payroll: values.payroll,
    recruitment: values.recruitment,
    performance: values.performance,
    training: values.training,
    time_attendance: values.time_attendance,
    benefits: values.benefits,
  }
}

export function formToCreatePayload(values: HcmFormValues) {
  const top = deriveTopLevelFromForm(values)
  return {
    feature_code: values.feature_code,
    reference: top.reference,
    title: top.title,
    status: values.status,
    description: values.description.trim() || null,
    party_name: top.party_name,
    amount: top.amount,
    quantity: top.quantity,
    start_date: top.start_date,
    end_date: top.end_date,
    extra_data: extraDataFromForm(values),
  }
}

export function formToUpdatePayload(values: HcmFormValues) {
  const top = deriveTopLevelFromForm(values)
  return {
    title: top.title,
    status: values.status,
    description: values.description.trim() || null,
    party_name: top.party_name,
    amount: top.amount,
    quantity: top.quantity,
    start_date: top.start_date,
    end_date: top.end_date,
    extra_data: extraDataFromForm(values),
  }
}

export function newHcmReference(featureCode?: string): string {
  const prefix =
    featureCode === "employee_records"
      ? "EMP"
      : featureCode === "payroll"
        ? "PAY"
        : featureCode === "recruitment"
          ? "REQ"
          : "HCM"
  return `${prefix}-${Date.now().toString(36).toUpperCase()}`
}

function extraObj(record: ModuleRecord): Record<string, unknown> {
  if (!record.extra_data || typeof record.extra_data !== "object") return {}
  return record.extra_data as Record<string, unknown>
}

export function employeeIdFromRecord(record: ModuleRecord): string {
  const emp = extraObj(record).employee as Record<string, unknown> | undefined
  const personal = emp?.personal as Record<string, unknown> | undefined
  const id = personal?.employee_id
  if (typeof id === "string" && id.trim()) return id
  return record.reference
}

export function fullNameFromRecord(record: ModuleRecord): string {
  const emp = extraObj(record).employee as Record<string, unknown> | undefined
  const personal = emp?.personal as Record<string, unknown> | undefined
  if (personal) {
    const name = buildEmployeeFullName({
      first_name: asString(personal.first_name),
      middle_name: asString(personal.middle_name),
      last_name: asString(personal.last_name),
      preferred_name: asString(personal.preferred_name),
    })
    if (name) return name
  }
  return record.title
}

export function departmentFromRecord(record: ModuleRecord): string {
  const emp = extraObj(record).employee as Record<string, unknown> | undefined
  const employment = emp?.employment as Record<string, unknown> | undefined
  const dept = employment?.department
  return typeof dept === "string" && dept.trim() ? dept : "—"
}

export function managerFromRecord(record: ModuleRecord): string {
  if (record.party_name?.trim()) return record.party_name
  const emp = extraObj(record).employee as Record<string, unknown> | undefined
  const employment = emp?.employment as Record<string, unknown> | undefined
  const mgr = employment?.reporting_manager_name
  return typeof mgr === "string" && mgr.trim() ? mgr : "—"
}

export function payPeriodFromRecord(record: ModuleRecord): string {
  const pay = extraObj(record).payroll as Record<string, unknown> | undefined
  const period = pay?.pay_period
  return typeof period === "string" && period.trim() ? period : record.start_date ?? "—"
}

export function payrollEmployeeFromRecord(record: ModuleRecord): string {
  const pay = extraObj(record).payroll as Record<string, unknown> | undefined
  const ref = pay?.employee_reference
  return typeof ref === "string" && ref.trim() ? ref : record.party_name ?? "—"
}

export function recruitmentRequisitionFromRecord(record: ModuleRecord): string {
  const rec = extraObj(record).recruitment as Record<string, unknown> | undefined
  const id = rec?.requisition_id
  return typeof id === "string" && id.trim() ? id : record.reference
}

export function recruitmentCandidateFromRecord(record: ModuleRecord): string {
  const rec = extraObj(record).recruitment as Record<string, unknown> | undefined
  const name = rec?.candidate_name
  return typeof name === "string" && name.trim() ? name : record.title
}

export function recruitmentStageFromRecord(record: ModuleRecord): string {
  const rec = extraObj(record).recruitment as Record<string, unknown> | undefined
  const stage = rec?.stage
  return typeof stage === "string" && stage.trim() ? stage : record.status
}

export function performanceEmployeeFromRecord(record: ModuleRecord): string {
  const perf = extraObj(record).performance as Record<string, unknown> | undefined
  const ref = perf?.employee_reference
  return typeof ref === "string" && ref.trim() ? ref : record.party_name ?? "—"
}

export function performanceRatingFromRecord(record: ModuleRecord): string {
  const perf = extraObj(record).performance as Record<string, unknown> | undefined
  const rating = perf?.review_rating
  return typeof rating === "string" && rating.trim() ? rating : "—"
}

export function trainingCourseFromRecord(record: ModuleRecord): string {
  const train = extraObj(record).training as Record<string, unknown> | undefined
  const name = train?.course_name
  return typeof name === "string" && name.trim() ? name : record.title
}

export function trainingStatusFromRecord(record: ModuleRecord): string {
  const train = extraObj(record).training as Record<string, unknown> | undefined
  const status = train?.completion_status
  return typeof status === "string" && status.trim() ? status : record.status
}

export function timeEmployeeFromRecord(record: ModuleRecord): string {
  const time = extraObj(record).time_attendance as Record<string, unknown> | undefined
  const ref = time?.employee_reference
  return typeof ref === "string" && ref.trim() ? ref : record.party_name ?? "—"
}

export function timePeriodFromRecord(record: ModuleRecord): string {
  const time = extraObj(record).time_attendance as Record<string, unknown> | undefined
  const period = time?.timesheet_period
  return typeof period === "string" && period.trim() ? period : record.start_date ?? "—"
}

export function benefitsPlanFromRecord(record: ModuleRecord): string {
  const ben = extraObj(record).benefits as Record<string, unknown> | undefined
  const plan = ben?.health_plan_id
  return typeof plan === "string" && plan.trim() ? plan : "—"
}

export function benefitsEnrollmentFromRecord(record: ModuleRecord): string {
  const ben = extraObj(record).benefits as Record<string, unknown> | undefined
  const status = ben?.enrollment_status
  return typeof status === "string" && status.trim() ? status : record.status
}
