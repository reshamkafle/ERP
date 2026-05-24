export type HcmFieldType = "text" | "number" | "date" | "textarea" | "select"

export type HcmFieldDef = {
  path: string
  label: string
  type?: HcmFieldType
  placeholder?: string
  options?: { value: string; label: string }[]
  colSpan?: 1 | 2
}

export type HcmRepeatableKey =
  | "emergency_contacts"
  | "salary_components"
  | "certifications"
  | "language_skills"
  | "previous_employment"
  | "internal_history"
  | "dependents"
  | "payslip_elements"
  | "interview_scores"
  | "leave_requests"
  | "training_certifications"
  | "benefits_dependents"

export type HcmSectionDef = {
  id: string
  title: string
  description?: string
  fields: HcmFieldDef[]
  isRepeatable?: boolean
  repeatableKey?: HcmRepeatableKey
}

const statusOptions = [
  { value: "DRAFT", label: "Draft" },
  { value: "ACTIVE", label: "Active" },
  { value: "ON_LEAVE", label: "On Leave" },
  { value: "IN_PROGRESS", label: "In Progress" },
  { value: "COMPLETED", label: "Completed" },
  { value: "APPROVED", label: "Approved" },
  { value: "TERMINATED", label: "Terminated" },
  { value: "RETIRED", label: "Retired" },
  { value: "REJECTED", label: "Rejected" },
  { value: "CANCELLED", label: "Cancelled" },
]

const coreRecordFields: HcmFieldDef[] = [
  { path: "reference", label: "Reference / ID" },
  { path: "title", label: "Title / Display name" },
  { path: "status", label: "Status", type: "select", options: statusOptions },
  { path: "description", label: "Description", type: "textarea", colSpan: 2 },
]

// --- Employee Records fields ---

const personalFields: HcmFieldDef[] = [
  { path: "employee.personal.employee_id", label: "Employee ID" },
  { path: "employee.personal.title_prefix", label: "Title (Mr., Ms., Dr.)" },
  { path: "employee.personal.first_name", label: "First name" },
  { path: "employee.personal.middle_name", label: "Middle name" },
  { path: "employee.personal.last_name", label: "Last name" },
  { path: "employee.personal.preferred_name", label: "Preferred / Nickname" },
  { path: "employee.personal.date_of_birth", label: "Date of birth", type: "date" },
  { path: "employee.personal.gender", label: "Gender" },
  { path: "employee.personal.marital_status", label: "Marital status" },
  { path: "employee.personal.nationality", label: "Nationality / Citizenship" },
  { path: "employee.personal.national_id", label: "National ID / Passport / SSN / Tax ID" },
  { path: "employee.personal.personal_email", label: "Personal email" },
  { path: "employee.personal.personal_phone", label: "Personal phone / Mobile" },
  { path: "employee.personal.blood_group", label: "Blood group (optional)" },
  { path: "employee.personal.religion_ethnicity", label: "Religion / Ethnicity" },
  { path: "employee.personal.disability_status", label: "Disability / Accommodation needs" },
  { path: "employee.personal.photo_url", label: "Photo URL", colSpan: 2 },
]

export const emergencyContactFields: HcmFieldDef[] = [
  { path: "name", label: "Contact name" },
  { path: "relationship", label: "Relationship" },
  { path: "phone", label: "Phone" },
]

const addressFields: HcmFieldDef[] = [
  { path: "employee.address.permanent_address", label: "Permanent address", type: "textarea", colSpan: 2 },
  { path: "employee.address.mailing_address", label: "Current / Mailing address", type: "textarea", colSpan: 2 },
  { path: "employee.address.city", label: "City" },
  { path: "employee.address.state", label: "State / Province" },
  { path: "employee.address.country", label: "Country" },
  { path: "employee.address.postal_code", label: "Postal code" },
  { path: "employee.address.emergency_address", label: "Emergency address", type: "textarea", colSpan: 2 },
]

const employmentFields: HcmFieldDef[] = [
  { path: "employee.employment.employment_type", label: "Employment type" },
  { path: "employee.employment.employee_status", label: "Employee status" },
  { path: "employee.employment.hire_date", label: "Hire / Joining date", type: "date" },
  { path: "employee.employment.confirmation_date", label: "Confirmation date", type: "date" },
  { path: "employee.employment.probation_end", label: "Probation end date", type: "date" },
  { path: "employee.employment.department", label: "Department / Division" },
  { path: "employee.employment.job_title", label: "Job title / Position" },
  { path: "employee.employment.job_code", label: "Job code" },
  { path: "employee.employment.grade", label: "Grade / Band / Level" },
  { path: "employee.employment.reporting_manager_id", label: "Reporting manager ID" },
  { path: "employee.employment.reporting_manager_name", label: "Reporting manager name" },
  { path: "employee.employment.location", label: "Location / Branch / Site" },
  { path: "employee.employment.cost_center", label: "Cost center" },
  { path: "employee.employment.legal_entity", label: "Legal entity / Company code" },
  { path: "employee.employment.business_unit", label: "Business unit" },
  { path: "employee.employment.work_shift", label: "Work shift / Schedule" },
  { path: "employee.employment.union_membership", label: "Union membership" },
]

const orgPositionFields: HcmFieldDef[] = [
  { path: "employee.org_position.position_id", label: "Position ID" },
  { path: "employee.org_position.reports_to_position", label: "Reports to position" },
  { path: "employee.org_position.job_family", label: "Job family / Sub-family" },
  { path: "employee.org_position.org_unit", label: "Organizational unit" },
  { path: "employee.org_position.matrix_manager", label: "Matrix reporting manager" },
]

const compensationFields: HcmFieldDef[] = [
  { path: "employee.compensation.basic_salary", label: "Basic salary / Gross pay", type: "number" },
  { path: "employee.compensation.pay_frequency", label: "Pay frequency" },
  { path: "employee.compensation.currency", label: "Currency" },
  { path: "employee.compensation.bank_account_number", label: "Bank account number" },
  { path: "employee.compensation.bank_name", label: "Bank name" },
  { path: "employee.compensation.iban", label: "IBAN" },
  { path: "employee.compensation.swift", label: "SWIFT" },
  { path: "employee.compensation.payment_method", label: "Payment method" },
  { path: "employee.compensation.tax_withholding_status", label: "Tax / Withholding status" },
  { path: "employee.compensation.provident_fund_id", label: "Provident fund / Pension ID" },
  { path: "employee.compensation.bonus_eligibility", label: "Bonus / Incentive eligibility" },
  { path: "employee.compensation.last_raise_date", label: "Last pay raise date", type: "date" },
  { path: "employee.compensation.last_raise_amount", label: "Last raise amount", type: "number" },
]

export const salaryComponentFields: HcmFieldDef[] = [
  { path: "component_type", label: "Type (Allowance / Deduction)" },
  { path: "description", label: "Description" },
  { path: "amount", label: "Amount", type: "number" },
]

const educationFields: HcmFieldDef[] = [
  { path: "employee.education.highest_qualification", label: "Highest qualification" },
  { path: "employee.education.degree", label: "Degree / Diploma" },
  { path: "employee.education.field_of_study", label: "Field of study / Major" },
  { path: "employee.education.institution", label: "Institution / University" },
  { path: "employee.education.year_of_graduation", label: "Year of graduation" },
]

export const certificationFields: HcmFieldDef[] = [
  { path: "name", label: "Certification / License" },
  { path: "issuer", label: "Issuer" },
  { path: "expiry_date", label: "Expiry date", type: "date" },
]

export const languageSkillFields: HcmFieldDef[] = [
  { path: "language", label: "Language" },
  { path: "proficiency", label: "Proficiency level" },
]

const experienceFields: HcmFieldDef[] = [
  { path: "employee.experience.total_years_experience", label: "Total years of experience" },
]

export const previousEmploymentFields: HcmFieldDef[] = [
  { path: "employer", label: "Employer" },
  { path: "job_title", label: "Job title" },
  { path: "start_date", label: "Start date", type: "date" },
  { path: "end_date", label: "End date", type: "date" },
  { path: "notes", label: "Notes", colSpan: 2 },
]

export const internalHistoryFields: HcmFieldDef[] = [
  { path: "event_type", label: "Event (Promotion, Transfer, etc.)" },
  { path: "effective_date", label: "Effective date", type: "date" },
  { path: "from_value", label: "From" },
  { path: "to_value", label: "To" },
  { path: "notes", label: "Notes", colSpan: 2 },
]

const performanceTalentFields: HcmFieldDef[] = [
  { path: "employee.performance_talent.performance_rating_current", label: "Performance rating (current)" },
  { path: "employee.performance_talent.performance_rating_historical", label: "Historical ratings" },
  { path: "employee.performance_talent.last_appraisal_date", label: "Last appraisal date", type: "date" },
  { path: "employee.performance_talent.next_appraisal_due", label: "Next appraisal due", type: "date" },
  { path: "employee.performance_talent.talent_category", label: "Talent category" },
  { path: "employee.performance_talent.succession_plan", label: "Succession plan details" },
  { path: "employee.performance_talent.skills_competencies", label: "Skills / Competencies", type: "textarea", colSpan: 2 },
  { path: "employee.performance_talent.training_history", label: "Training history", type: "textarea", colSpan: 2 },
  { path: "employee.performance_talent.development_plan", label: "Development plan", type: "textarea", colSpan: 2 },
]

const employeeTimeFields: HcmFieldDef[] = [
  { path: "employee.time_attendance.leave_entitlement_annual", label: "Annual leave entitlement" },
  { path: "employee.time_attendance.leave_entitlement_sick", label: "Sick leave entitlement" },
  { path: "employee.time_attendance.leave_entitlement_maternity", label: "Maternity leave entitlement" },
  { path: "employee.time_attendance.leave_balance", label: "Leave balance" },
  { path: "employee.time_attendance.attendance_tracking_method", label: "Attendance tracking method" },
  { path: "employee.time_attendance.shift_roster", label: "Shift roster assignment" },
]

const employeeBenefitsFields: HcmFieldDef[] = [
  { path: "employee.benefits_entitlements.health_insurance_plan_id", label: "Health insurance plan ID" },
  { path: "employee.benefits_entitlements.life_insurance", label: "Life insurance" },
  { path: "employee.benefits_entitlements.benefit_enrollment_status", label: "Benefit enrollment status" },
  { path: "employee.benefits_entitlements.company_car_asset", label: "Company car / Asset assignment" },
]

export const dependentFields: HcmFieldDef[] = [
  { path: "name", label: "Name" },
  { path: "relationship", label: "Relationship" },
  { path: "date_of_birth", label: "Date of birth", type: "date" },
]

const terminationFields: HcmFieldDef[] = [
  { path: "employee.termination.termination_date", label: "Termination date", type: "date" },
  { path: "employee.termination.separation_reason", label: "Reason for separation" },
  { path: "employee.termination.notice_period", label: "Notice period" },
  { path: "employee.termination.exit_interview_date", label: "Exit interview date", type: "date" },
  { path: "employee.termination.exit_interview_notes", label: "Exit interview notes", type: "textarea", colSpan: 2 },
  { path: "employee.termination.final_settlement_date", label: "Final settlement date", type: "date" },
  { path: "employee.termination.final_settlement_amount", label: "Final settlement amount", type: "number" },
]

const systemComplianceFields: HcmFieldDef[] = [
  { path: "employee.system_compliance.approval_workflow_status", label: "Approval workflow status" },
  { path: "employee.system_compliance.data_privacy_consent", label: "Data privacy consent (GDPR, PDPA)" },
  { path: "employee.system_compliance.audit_change_log", label: "Audit trail / Change log", type: "textarea", colSpan: 2 },
  { path: "employee.system_compliance.integration_active_directory", label: "Active Directory integration" },
  { path: "employee.system_compliance.integration_payroll", label: "Payroll integration" },
  { path: "employee.system_compliance.integration_benefits", label: "Benefits integration" },
]

const countrySpecificFields: HcmFieldDef[] = [
  { path: "employee.country_specific.visa_work_permit", label: "Visa / Work permit" },
  { path: "employee.country_specific.visa_expiry", label: "Visa expiry", type: "date" },
  { path: "employee.country_specific.dependent_visa_info", label: "Dependent visa information" },
  { path: "employee.country_specific.tax_residency_status", label: "Tax residency status" },
  { path: "employee.country_specific.local_id_number", label: "Local ID (HKID, NRIC, Aadhaar, etc.)" },
  { path: "employee.country_specific.race_ethnicity_compliance", label: "Race / Ethnicity (compliance)" },
  { path: "employee.country_specific.military_service", label: "Military service" },
]

// --- Payroll ---

const payrollFields: HcmFieldDef[] = [
  { path: "payroll.employee_reference", label: "Employee reference" },
  { path: "payroll.pay_period", label: "Pay period" },
  { path: "payroll.pay_run_id", label: "Pay run ID" },
  { path: "payroll.gross_pay", label: "Gross pay", type: "number" },
  { path: "payroll.net_pay", label: "Net pay", type: "number" },
  { path: "payroll.currency", label: "Currency" },
  { path: "payroll.payment_status", label: "Payment status" },
  { path: "payroll.statutory_deductions", label: "Statutory deductions", type: "textarea", colSpan: 2 },
  { path: "payroll.tax_calculations", label: "Tax calculations", type: "textarea", colSpan: 2 },
]

export const payslipElementFields: HcmFieldDef[] = [
  { path: "element_code", label: "Element code" },
  { path: "description", label: "Description" },
  { path: "amount", label: "Amount", type: "number" },
  { path: "deduction", label: "Deduction flag" },
]

// --- Recruitment ---

const recruitmentFields: HcmFieldDef[] = [
  { path: "recruitment.requisition_id", label: "Requisition ID" },
  { path: "recruitment.candidate_name", label: "Candidate name" },
  { path: "recruitment.candidate_email", label: "Candidate email" },
  { path: "recruitment.candidate_profile", label: "Candidate profile", type: "textarea", colSpan: 2 },
  { path: "recruitment.stage", label: "Stage / Status" },
  { path: "recruitment.offer_letter_ref", label: "Offer letter reference" },
  { path: "recruitment.onboarding_checklist", label: "Onboarding checklist", type: "textarea", colSpan: 2 },
  { path: "recruitment.documents_assigned", label: "Documents assigned" },
  { path: "recruitment.training_assigned", label: "Training assigned" },
]

export const interviewScoreFields: HcmFieldDef[] = [
  { path: "interviewer", label: "Interviewer" },
  { path: "round", label: "Round" },
  { path: "score", label: "Score" },
  { path: "notes", label: "Notes" },
]

// --- Performance ---

const performanceFields: HcmFieldDef[] = [
  { path: "performance.employee_reference", label: "Employee reference" },
  { path: "performance.review_cycle", label: "Review cycle" },
  { path: "performance.goals", label: "Goals", type: "textarea", colSpan: 2 },
  { path: "performance.kpis", label: "KPIs", type: "textarea", colSpan: 2 },
  { path: "performance.review_rating", label: "Review rating" },
  { path: "performance.feedback_360", label: "360 feedback", type: "textarea", colSpan: 2 },
  { path: "performance.last_appraisal_date", label: "Last appraisal date", type: "date" },
  { path: "performance.next_appraisal_due", label: "Next appraisal due", type: "date" },
  { path: "performance.talent_category", label: "Talent category" },
  { path: "performance.succession_readiness", label: "Succession readiness" },
  { path: "performance.career_path", label: "Career path", type: "textarea", colSpan: 2 },
]

// --- Training ---

const trainingFields: HcmFieldDef[] = [
  { path: "training.employee_reference", label: "Employee reference" },
  { path: "training.course_catalog_id", label: "Course catalog ID" },
  { path: "training.course_name", label: "Course name" },
  { path: "training.enrollment_date", label: "Enrollment date", type: "date" },
  { path: "training.completion_status", label: "Completion status" },
  { path: "training.completion_date", label: "Completion date", type: "date" },
  { path: "training.development_plan", label: "Development plan", type: "textarea", colSpan: 2 },
]

// --- Time & Attendance ---

const timeAttendanceFields: HcmFieldDef[] = [
  { path: "time_attendance.employee_reference", label: "Employee reference" },
  { path: "time_attendance.timesheet_period", label: "Timesheet period" },
  { path: "time_attendance.overtime_hours", label: "Overtime hours" },
  { path: "time_attendance.absences", label: "Absences" },
  { path: "time_attendance.leave_balance_snapshot", label: "Leave balance snapshot" },
  { path: "time_attendance.shift_roster", label: "Shift roster" },
  { path: "time_attendance.tracking_method", label: "Tracking method" },
]

export const leaveRequestFields: HcmFieldDef[] = [
  { path: "leave_type", label: "Leave type" },
  { path: "start_date", label: "Start date", type: "date" },
  { path: "end_date", label: "End date", type: "date" },
  { path: "days", label: "Days" },
  { path: "status", label: "Status" },
]

// --- Benefits ---

const benefitsFields: HcmFieldDef[] = [
  { path: "benefits.employee_reference", label: "Employee reference" },
  { path: "benefits.health_plan_id", label: "Health plan ID" },
  { path: "benefits.life_insurance_plan", label: "Life insurance plan" },
  { path: "benefits.enrollment_status", label: "Enrollment status" },
  { path: "benefits.effective_date", label: "Effective date", type: "date" },
  { path: "benefits.company_car_asset", label: "Company car / Asset" },
  { path: "benefits.dependents_summary", label: "Dependents summary", type: "textarea", colSpan: 2 },
]

export const REPEATABLE_FIELD_MAP: Record<HcmRepeatableKey, HcmFieldDef[]> = {
  emergency_contacts: emergencyContactFields,
  salary_components: salaryComponentFields,
  certifications: certificationFields,
  language_skills: languageSkillFields,
  previous_employment: previousEmploymentFields,
  internal_history: internalHistoryFields,
  dependents: dependentFields,
  payslip_elements: payslipElementFields,
  interview_scores: interviewScoreFields,
  leave_requests: leaveRequestFields,
  training_certifications: certificationFields,
  benefits_dependents: dependentFields,
}

export const REPEATABLE_ARRAY_PATH: Record<HcmRepeatableKey, string> = {
  emergency_contacts: "employee.emergency_contacts",
  salary_components: "employee.salary_components",
  certifications: "employee.certifications",
  language_skills: "employee.language_skills",
  previous_employment: "employee.previous_employment",
  internal_history: "employee.internal_history",
  dependents: "employee.dependents",
  payslip_elements: "payroll.payslip_elements",
  interview_scores: "recruitment.interview_scores",
  leave_requests: "time_attendance.leave_requests",
  training_certifications: "training.certifications",
  benefits_dependents: "benefits.dependents",
}

const FEATURE_SECTIONS: Record<string, HcmSectionDef[]> = {
  employee_records: [
    { id: "core", title: "Record identity", fields: coreRecordFields },
    { id: "personal", title: "Personal information", fields: personalFields },
    {
      id: "emergency",
      title: "Emergency contacts",
      fields: [],
      isRepeatable: true,
      repeatableKey: "emergency_contacts",
    },
    { id: "address", title: "Address & contact", fields: addressFields },
    { id: "employment", title: "Employment / job information", fields: employmentFields },
    { id: "org", title: "Organizational & position", fields: orgPositionFields },
    { id: "comp", title: "Compensation & payroll", fields: compensationFields },
    {
      id: "salary_lines",
      title: "Salary structure components",
      fields: [],
      isRepeatable: true,
      repeatableKey: "salary_components",
    },
    { id: "education", title: "Education & qualifications", fields: educationFields },
    {
      id: "certs",
      title: "Certifications & licenses",
      fields: [],
      isRepeatable: true,
      repeatableKey: "certifications",
    },
    {
      id: "languages",
      title: "Language skills",
      fields: [],
      isRepeatable: true,
      repeatableKey: "language_skills",
    },
    { id: "experience", title: "Work experience summary", fields: experienceFields },
    {
      id: "prev_jobs",
      title: "Previous employment",
      fields: [],
      isRepeatable: true,
      repeatableKey: "previous_employment",
    },
    {
      id: "internal",
      title: "Internal work history",
      fields: [],
      isRepeatable: true,
      repeatableKey: "internal_history",
    },
    { id: "perf", title: "Performance & talent", fields: performanceTalentFields },
    { id: "time", title: "Time & attendance (employee)", fields: employeeTimeFields },
    { id: "ben_emp", title: "Benefits & entitlements (employee)", fields: employeeBenefitsFields },
    {
      id: "deps",
      title: "Dependents",
      fields: [],
      isRepeatable: true,
      repeatableKey: "dependents",
    },
    { id: "term", title: "Termination / exit", fields: terminationFields },
    { id: "system", title: "System & compliance", fields: systemComplianceFields },
    { id: "country", title: "Country-specific", fields: countrySpecificFields },
  ],
  payroll: [
    { id: "core", title: "Record identity", fields: coreRecordFields },
    { id: "payroll", title: "Payroll processing", fields: payrollFields },
    {
      id: "payslip",
      title: "Payslip elements",
      fields: [],
      isRepeatable: true,
      repeatableKey: "payslip_elements",
    },
  ],
  recruitment: [
    { id: "core", title: "Record identity", fields: coreRecordFields },
    { id: "recruitment", title: "Recruitment & onboarding", fields: recruitmentFields },
    {
      id: "interviews",
      title: "Interview scores",
      fields: [],
      isRepeatable: true,
      repeatableKey: "interview_scores",
    },
  ],
  performance: [
    { id: "core", title: "Record identity", fields: coreRecordFields },
    { id: "performance", title: "Performance management", fields: performanceFields },
  ],
  training: [
    { id: "core", title: "Record identity", fields: coreRecordFields },
    { id: "training", title: "Training & development", fields: trainingFields },
    {
      id: "certs_train",
      title: "Certifications",
      fields: [],
      isRepeatable: true,
      repeatableKey: "training_certifications",
    },
  ],
  time_attendance: [
    { id: "core", title: "Record identity", fields: coreRecordFields },
    { id: "time", title: "Time & attendance", fields: timeAttendanceFields },
    {
      id: "leave_req",
      title: "Leave requests",
      fields: [],
      isRepeatable: true,
      repeatableKey: "leave_requests",
    },
  ],
  benefits: [
    { id: "core", title: "Record identity", fields: coreRecordFields },
    { id: "benefits", title: "Benefits administration", fields: benefitsFields },
    {
      id: "ben_deps",
      title: "Dependents",
      fields: [],
      isRepeatable: true,
      repeatableKey: "benefits_dependents",
    },
  ],
}

export const HCM_FEATURE_OPTIONS = [
  { value: "payroll", label: "Payroll Processing" },
  { value: "recruitment", label: "Recruitment & Onboarding" },
  { value: "employee_records", label: "Employee Records" },
  { value: "performance", label: "Performance Management" },
  { value: "training", label: "Training & Development" },
  { value: "time_attendance", label: "Time & Attendance" },
  { value: "benefits", label: "Benefits Administration" },
] as const

export function getHcmSectionsForFeature(featureCode: string): HcmSectionDef[] {
  return FEATURE_SECTIONS[featureCode] ?? FEATURE_SECTIONS.employee_records
}
