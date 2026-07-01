# Requirements Document

## Introduction

NBK Salary Management Software is a full-stack web application for Trường THCS Nguyễn Bỉnh Khiêm (NBK School) that calculates teacher salaries from timetable and pricing data, manages office staff attendance-based salary, and produces payslips and reports. The system supports two staff groups: Teachers (GV) with period-based salary calculation and Office Staff (VP) with attendance-based salary calculation.

## Glossary

- **System**: The NBK Salary Management Software web application
- **Teacher (GV)**: An employee whose salary is calculated from teaching periods multiplied by unit price per Teacher×Subject×Grade combination
- **Office_Staff (VP)**: An employee whose salary is calculated from daily attendance multiplied by salary grade
- **Timetable (TKB)**: The school's unified teaching schedule that assigns teachers to classes, subjects, and periods across all grade levels
- **Change_Log**: A record of substitute teacher assignments replacing originally scheduled teachers
- **BCC_Summary**: The "BCC tổng tiết" report consolidating teaching periods across four column groups (Theo TKB, Thay đổi, Phát sinh, Thực tế)
- **Unit_Price**: The monetary value per teaching period for a specific Teacher×Subject×Grade combination
- **Payslip**: The salary statement for an employee containing six sections (Employee Info, Total Income, Bonuses Received, Deductions, Tax Settlement, Net Pay)
- **Attendance_Record**: A daily log of office staff presence using predefined attendance symbols for each day of the month
- **Salary_Grade**: A coefficient-based classification determining base salary for office staff
- **External_Teaching**: Teaching activities outside regular timetable with multiple rate types and coefficients
- **PIT**: Personal Income Tax (Thuế thu nhập cá nhân)
- **Misa_Format**: The standardized export format compatible with Misa accounting software
- **Admin**: A user with full system access including configuration and user management
- **Accountant**: A user responsible for salary calculation, verification, and payslip generation
- **Viewer**: A user with read-only access to approved reports
- **Chức_Vụ**: Position title held by an employee (e.g., GVCN, PCN, GVu), each with its own contracted salary unit price (đơn giá lương khoán)
- **Cấp_Bậc_QL**: Management level classification for an employee, each with its own contracted salary unit price
- **Nghiệp_Vụ**: Professional duty assigned to an employee; each duty adds a fixed supplement of 2,000,000 VND to contracted salary
- **Kiêm_Nhiệm**: Concurrent role assigned to an employee; each concurrent role adds a fixed supplement of 3,000,000 VND to contracted salary
- **Lương_Khoán**: Contracted salary calculated as: đơn_giá_chức_vụ + đơn_giá_cấp_bậc + (số_nghiệp_vụ × 2,000,000) + (số_kiêm_nhiệm × 3,000,000)
- **Tên_Gọi**: A display nickname used within the school to identify teachers (GV group only), distinct from their legal name
- **Unified_TKB_Form**: A single timetable input form covering all grade levels, from which the System reads and writes data into the standardized TKB structure
- **External_Period_Table**: "Bảng nhập dữ liệu phát sinh theo tiết" — a single consolidated input table for all external/supplementary teaching periods (Vĩnh Yên, Bồi dưỡng, IELTS, Luyện thi, Âm nhạc, and other types)
- **Support_Allowance_Table**: "Các khoản hỗ trợ khác theo lương" — a dedicated input table for salary-related support allowances (meal allowance, parking, ChatGPT subscription, etc.)
- **Misa_Attendance_Import**: The process of importing VP attendance data (working days, overtime, paid leave, unpaid leave) from Misa accounting software Excel export
- **MISA_HR_Import**: The standardized process of importing HR data (employee profiles, family/dependents, salary history, work history, qualifications, leave balances, organization structure, job positions) from MISA AMIS Excel templates
- **Gia_Đình**: Family member or dependent information linked to an employee, used for tax dependent deduction (giảm trừ người phụ thuộc)
- **Lịch_Sử_Lương**: Historical salary records including base salary, allowances, and deductions with effective dates
- **Quá_Trình_Công_Tác**: Employee work history tracking transfers, promotions, and status changes
- **Bảng_Cấp**: Employee qualification/degree records including training institution, major, and graduation details
- **Nghỉ_Phép_Balance**: Annual leave balance summary per employee including current year, carried over, seniority-based, and used leave days

## Requirements

### Requirement 1: Master Data Management

**User Story:** As an Accountant, I want to manage catalog data (departments, position titles, management levels, professional duties, concurrent roles, grades, classes, subjects, employees, salary grades, attendance symbols, unit prices, and contract history), so that the system has accurate reference data for salary calculations.

#### Acceptance Criteria

1. THE System SHALL provide CRUD operations for departments, grades, classes, and subjects, where each entity has a unique name within its category with a maximum length of 100 characters
2. THE System SHALL store Chức_Vụ records with a unique code (e.g., GVCN, PCN, GVu), a name (maximum 100 characters), and an associated đơn_giá_lương_khoán value in the range of 0 to 999,999,999 VND
3. THE System SHALL store Cấp_Bậc_QL records with a unique code, a name (maximum 100 characters), and an associated đơn_giá_lương_khoán value in the range of 0 to 999,999,999 VND
4. THE System SHALL store Nghiệp_Vụ records with a unique code and a name (maximum 100 characters), where each Nghiệp_Vụ adds a fixed supplement of 2,000,000 VND to contracted salary calculation
5. THE System SHALL store Kiêm_Nhiệm records with a unique code and a name (maximum 100 characters), where each Kiêm_Nhiệm adds a fixed supplement of 3,000,000 VND to contracted salary calculation
6. THE System SHALL store a Mô_Tả (description) field for each employee position assignment for explanation purposes only; this field SHALL NOT participate in any salary calculation
7. THE System SHALL calculate Lương_Khoán for each employee using the formula: đơn_giá_chức_vụ + đơn_giá_cấp_bậc + (số_nghiệp_vụ × 2,000,000) + (số_kiêm_nhiệm × 3,000,000)
8. THE System SHALL store employee records including legal name (maximum 100 characters), a unique employee code, staff group (GV or VP), department, Chức_Vụ assignment, Cấp_Bậc_QL assignment, Nghiệp_Vụ assignments (zero or more), Kiêm_Nhiệm assignments (zero or more), contract type (definite-term, indefinite-term, or probationary), and employment status (active, resigned, or suspended)
9. WHEN an employee record is created, THE System SHALL require designation as either Teacher (GV) or Office_Staff (VP)
10. WHEN an employee is designated as Teacher (GV), THE System SHALL store an optional Tên_Gọi field (maximum 50 characters) representing the teacher's display nickname within the school
11. WHEN an employee is designated as Office_Staff (VP), THE System SHALL NOT display or store the Tên_Gọi field
12. THE System SHALL store Unit_Price records as a unique combination of Teacher, Subject, and Grade with a monetary value per period in the range of 1 to 999,999,999 VND, ensuring only one active Unit_Price exists per Teacher×Subject×Grade combination at any point in time
13. WHEN a Unit_Price record is updated, THE System SHALL retain the previous value with its effective date range for historical reference
14. THE System SHALL store Salary_Grade records with coefficient values in the range of 0.01 to 99.99 and effective dates
15. THE System SHALL store attendance symbol definitions with corresponding numeric workday values (where full day equals 1.0, half day equals 0.5, and overtime and leave types each have a defined multiplier) used in workday calculations
16. THE System SHALL store task definitions and task unit prices for external teaching activities with monetary values in the range of 1 to 999,999,999 VND
17. WHEN a contract or salary change is recorded, THE System SHALL maintain a history log with effective start and end dates
18. IF a user attempts to create a record with a duplicate unique identifier (employee code, entity name within category, Chức_Vụ code, Cấp_Bậc_QL code, Nghiệp_Vụ code, Kiêm_Nhiệm code, or active Unit_Price for the same Teacher×Subject×Grade), THEN THE System SHALL reject the operation and display an error message indicating the duplicate conflict
19. IF a user attempts to delete a catalog record that is referenced by existing salary calculations, employee records, or Unit_Price records, THEN THE System SHALL prevent the deletion and display an error message indicating the record is in use
20. IF a required field is left empty or a value falls outside its permitted range during a create or update operation, THEN THE System SHALL reject the operation and indicate which field failed validation

### Requirement 2: Timetable Import and Validation (Unified TKB Form)

**User Story:** As an Accountant, I want to import the school timetable from a single unified form covering all grade levels, so that teaching period data is available for salary calculation without managing separate forms per grade.

#### Acceptance Criteria

1. WHEN an Excel or CSV file (maximum 10 MB) is uploaded from the Unified_TKB_Form, THE System SHALL parse timetable data including teacher, subject, grade, class, and period assignments for all grade levels from this single form
2. WHEN timetable data is imported, THE System SHALL validate each record against existing master data (teacher, subject, grade, class) and reject records with unmatched references while displaying specific validation errors per row
3. IF a timetable record references a non-existent teacher, subject, grade, or class, THEN THE System SHALL reject that record and display the specific validation error indicating the unmatched field and value
4. WHEN validation succeeds for all records, THE System SHALL store the timetable for the specified month and academic period, where the month is derived from user selection and confirmed before import
5. IF a timetable already exists for the specified month, THEN THE System SHALL prompt the user to confirm replacement or cancellation before overwriting
6. WHEN a timetable is successfully imported, THE System SHALL calculate the total scheduled periods per Teacher×Subject×Grade combination (Theo TKB columns: K6, K7, K8, K9, GD lối sống, Tổng tiết chính, KH bằng TA, Ielts) and display a summary of imported records
7. IF only some records pass validation, THEN THE System SHALL allow the user to choose between importing only valid records or cancelling the entire import
8. WHEN a timetable import completes successfully, THE System SHALL display a confirmation showing the number of records imported and the period covered
9. THE System SHALL read data from the Unified_TKB_Form and write it automatically into the standardized internal TKB data structure, mapping columns from the unified form to the appropriate grade, class, subject, and period fields

### Requirement 3: Change Log Management

**User Story:** As an Accountant, I want to record substitute teacher assignments and schedule changes, so that actual teaching periods reflect real classroom activity.

#### Acceptance Criteria

1. WHEN a teaching change is recorded, THE System SHALL capture the original teacher, substitute teacher, date, period (valid values: 1–10), class, subject, and reason (maximum 200 characters), and SHALL reject the entry with a validation error indicating which fields are missing or invalid if any required field is empty or out of range
2. THE System SHALL calculate change totals per teacher in categories: Nghỉ K6-8, Nghỉ K9, Nghỉ KH TA, Nghỉ Ielts, Thay K6-8, Thay K9, Thay KH TA, Thay Ielts
3. WHEN a change is recorded, THE System SHALL subtract the period from the original teacher's count and add the period to the substitute teacher's count for the corresponding Subject×Grade category
4. IF a change references a teacher not in the current timetable, THEN THE System SHALL display a warning indicating which teacher is unrecognized and require confirmation before saving
5. THE System SHALL support bulk import of changes from Excel/CSV files (maximum 500 rows per file) with the same validation rules as individual entry; IF one or more rows fail validation, THEN THE System SHALL reject the entire file and display a list of invalid rows with their corresponding error reasons
6. IF a change is recorded for the same original teacher, date, period, and class as an existing record, THEN THE System SHALL display a duplicate warning and require confirmation before saving
7. WHEN the user edits or deletes an existing change record, THE System SHALL reverse the original period adjustment and apply the new adjustment (or no adjustment on deletion) to the affected teachers' counts

### Requirement 4: BCC Summary Calculation

**User Story:** As an Accountant, I want the system to automatically generate the BCC tổng tiết report, so that I can verify actual teaching periods before salary calculation.

#### Acceptance Criteria

1. WHEN a BCC Summary is generated for a selected month, THE System SHALL calculate and display four column groups: Theo TKB (scheduled), Thay đổi (changes), Phát sinh (adjustments), and Thực tế (actual), with one row per teacher
2. THE System SHALL calculate each teacher's Thực tế sub-columns as follows: Tiết chính HS1 = (Theo TKB Tổng tiết chính) minus (Nghỉ K6-8) minus (Nghỉ K9) plus (Thay K6-8) plus (Thay K9) plus (Phát sinh net adjustments for tiết chính); TNST VY (HS1.3) = periods classified as TNST VY from schedule minus absences plus substitutions for TNST VY; K9 luyện thi (HS1.5) = K9 luyện thi periods from schedule minus absences plus substitutions for K9 luyện thi; KH TA = (Theo TKB KH bằng TA) minus (Nghỉ KH TA) plus (Thay KH TA) plus (Phát sinh net adjustments for KH TA); Ielts = (Theo TKB Ielts) minus (Nghỉ Ielts) plus (Thay Ielts) plus (Phát sinh net adjustments for Ielts)
3. THE System SHALL display Thực tế columns: Tiết chính HS1, TNST VY (HS1.3), K9 luyện thi (HS1.5), KH TA, Ielts, and Tổng, with all period values displayed as numbers rounded to 1 decimal place
4. WHEN adjustments (Cộng tiết or Trừ tiết) are entered, THE System SHALL include them in the Phát sinh column group with a mandatory reason description of up to 200 characters
5. THE System SHALL allow manual entry of special adjustments (values from -50.0 to +50.0 periods) in the Phát sinh group and record an audit trail containing the user who entered, the timestamp of entry, and the reason
6. WHEN the BCC Summary is generated, THE System SHALL calculate the Tổng in the Thực tế group using the formula: Tổng = (Tiết chính HS1 × 1.0) + (TNST VY × 1.3) + (K9 luyện thi × 1.5) + (KH TA × 1.0) + (Ielts × 1.0)
7. IF any Thay đổi or Phát sinh data has not been entered for a teacher in the selected month, THEN THE System SHALL mark that teacher's row as incomplete and exclude it from salary export until all data is provided
8. WHEN a BCC Summary is generated, THE System SHALL recalculate all Thực tế values from current source data, ensuring that any subsequent changes to Thay đổi or Phát sinh entries are reflected upon the next generation
9. WHEN calculating Phát sinh for a teacher, THE System SHALL source external period data from the consolidated External_Period_Table, summing periods by type (Vĩnh Yên, Bồi dưỡng, IELTS, Luyện thi, Âm nhạc, and other types) for the selected month

### Requirement 5: External Period Data Entry (Consolidated Table)

**User Story:** As an Accountant, I want to enter all external/supplementary teaching periods in one consolidated table, so that I do not need to manage separate input forms for each teaching type.

#### Acceptance Criteria

1. THE System SHALL provide a single External_Period_Table ("Bảng nhập dữ liệu phát sinh theo tiết") for entering all external and supplementary teaching period data
2. THE System SHALL require each External_Period_Table entry to include: teacher, month, year, loại (type), number of periods, unit price, coefficient, and calculated amount (số_tiết × đơn_giá × hệ_số)
3. THE System SHALL support at minimum the following loại (type) values in the External_Period_Table: Vĩnh Yên, Bồi dưỡng, IELTS, Luyện thi, Âm nhạc, and allow Admin users to configure additional type values
4. WHEN a new entry is added to the External_Period_Table, THE System SHALL validate that the teacher exists in master data and the loại value is a recognized type
5. IF an entry references a non-existent teacher or unrecognized loại value, THEN THE System SHALL reject the entry and display a validation error indicating the invalid field
6. THE System SHALL support bulk import of External_Period_Table data from Excel/CSV files with the same validation rules as individual entry
7. WHEN External_Period_Table data is used in BCC Summary or salary calculation, THE System SHALL aggregate periods by teacher and loại for the specified month

### Requirement 6: Support Allowance Management

**User Story:** As an Accountant, I want a dedicated input table for salary-related support allowances, so that items like meal allowance, parking, and subscriptions are managed consistently rather than being scattered or hardcoded.

#### Acceptance Criteria

1. THE System SHALL provide a dedicated Support_Allowance_Table ("Các khoản hỗ trợ khác theo lương") for entering and managing salary-related support allowances per employee per month
2. THE System SHALL require each Support_Allowance_Table entry to include: employee, month, year, allowance type, and monetary amount in the range of 0 to 999,999,999 VND
3. THE System SHALL support at minimum the following allowance types: ăn trưa (meal allowance), gửi xe (parking), ChatGPT (subscription), and allow Admin users to configure additional allowance types
4. WHEN allowance data is entered or updated, THE System SHALL validate that the employee exists in master data and the allowance type is a recognized type
5. IF an entry references a non-existent employee or unrecognized allowance type, THEN THE System SHALL reject the entry and display a validation error indicating the invalid field
6. THE System SHALL support bulk entry of allowances for multiple employees in a single operation (batch entry by allowance type for a given month)
7. WHEN payslip Section II item 4 (Support allowances) is calculated, THE System SHALL sum all Support_Allowance_Table entries for that employee in the specified month
8. THE System SHALL support import of Support_Allowance_Table data from Excel/CSV files with validation rules consistent with individual entry

### Requirement 7: Teacher Salary Calculation

**User Story:** As an Accountant, I want the system to calculate teacher salary from actual teaching periods, unit prices, and contracted salary components, so that teachers are paid accurately based on their workload and position.

#### Acceptance Criteria

1. WHEN salary calculation is triggered for a teacher, THE System SHALL multiply each actual period count from BCC Summary by the corresponding Unit_Price for that Teacher×Subject×Grade combination, applying the coefficient: standard periods × Unit_Price × 1.0, TNST VY periods × Unit_Price × 1.3, K9 luyện thi periods × Unit_Price × 1.5
2. THE System SHALL calculate total regular teaching income as the sum of all (period_count × Unit_Price × coefficient) products across all Subject×Grade combinations for that teacher
3. THE System SHALL calculate External_Teaching income by summing entries from the External_Period_Table for that teacher in the calculation month, where each entry contributes: số_tiết × đơn_giá × hệ_số
4. IF a Unit_Price is not defined for a Teacher×Subject×Grade combination that appears in the BCC Summary, THEN THE System SHALL flag the missing price with the specific Teacher, Subject, and Grade details, and prevent salary finalization for that teacher until all prices are resolved
5. THE System SHALL apply weighted coefficients to period counts: standard periods at coefficient 1.0, TNST VY at coefficient 1.3, K9 exam prep at coefficient 1.5, where the coefficient multiplies the Unit_Price for the payment calculation
6. THE System SHALL calculate Lương_Khoán for the teacher using: đơn_giá_chức_vụ + đơn_giá_cấp_bậc + (số_nghiệp_vụ × 2,000,000) + (số_kiêm_nhiệm × 3,000,000), and use this as the contracted salary base for payslip Section II item 1
7. THE System SHALL calculate the total teacher salary for payslip Section II item 2 (Tiền giảng dạy) as the sum of regular teaching income plus external teaching income
8. IF a teacher has both regular and external teaching data, THEN THE System SHALL display a breakdown showing each component separately before presenting the total

### Requirement 8: Office Staff Salary Calculation

**User Story:** As an Accountant, I want the system to calculate office staff salary from attendance records (imported from Misa) and salary grades, so that office staff are paid according to their working days.

#### Acceptance Criteria

1. THE System SHALL accept Misa accounting software Excel export files containing VP attendance data including working days, overtime days, paid leave days, and unpaid leave days per Office_Staff member per month
2. WHEN a Misa Excel export file is uploaded for VP attendance import, THE System SHALL parse the file and map each row to the corresponding Office_Staff member using employee code or name matching
3. IF the Misa import file contains rows with unmatched employee identifiers or unrecognizable data format, THEN THE System SHALL reject those rows and display validation errors indicating which rows failed and why, while allowing valid rows to be imported
4. WHEN Misa attendance data is successfully imported, THE System SHALL auto-calculate total working days, overtime days, paid leave days, and unpaid leave days per Office_Staff member for that month
5. THE System SHALL calculate Office_Staff salary as: (Salary_Grade coefficient × base salary) × (actual working days / standard working days in month), where standard working days defaults to 26 and is configurable per month by an administrator
6. WHILE an Office_Staff member is in probation status, THE System SHALL apply a configurable probation salary percentage (default: 85%) to the calculated salary
7. WHEN an Office_Staff member transitions from probation to official status mid-month, THE System SHALL calculate salary pro-rata: probation percentage applied to working days before the effective date, and full salary applied to working days from the effective date onward
8. THE System SHALL also support manual entry or editing of VP attendance data for cases where Misa import data needs correction
9. IF attendance data for an Office_Staff member is incomplete (fewer recorded days than working days in the month), THEN THE System SHALL flag the record for review and exclude it from salary calculation until the attendance is completed or confirmed by an authorized user
10. THE System SHALL calculate Lương_Khoán for Office_Staff using: đơn_giá_chức_vụ + đơn_giá_cấp_bậc + (số_nghiệp_vụ × 2,000,000) + (số_kiêm_nhiệm × 3,000,000), and use this as the contracted salary base for payslip Section II item 1

### Requirement 9: Payslip Generation

**User Story:** As an Accountant, I want to generate complete payslips with all income and deduction components, so that each employee receives a detailed salary breakdown.

#### Acceptance Criteria

1. WHEN a payslip is generated for an employee, THE System SHALL populate Section I (Employee Info) with: employee name, Tên_Gọi (for GV only), Chức_Vụ, Cấp_Bậc_QL, Nghiệp_Vụ assignments, Kiêm_Nhiệm assignments, base salary (Mức lương chính - insurance base), efficiency bonus rate (Thưởng hiệu quả), and total Lương_Khoán calculated from the position component formula
2. WHEN a payslip is generated, THE System SHALL display the paid working days (Ngày công hưởng lương) and remaining leave balance (Tổng số ngày phép tồn) for the payslip period
3. WHEN a payslip is generated, THE System SHALL calculate Section II (Total Income) as the sum of 9 line items: 1-Contracted salary (Lương_Khoán) prorated by actual paid working days divided by standard working days in the month, 2-Teaching income (tiết tại trường, TNST, ôn K9, khoa học TA, Ielts, luyện thi), 3-Exam fees (ra đề/duyệt đề/chấm thi), 4-Support allowances from Support_Allowance_Table (ăn trưa, gửi xe, ChatGPT, etc.), 5-Birthday bonus, 6-Overtime/efficiency bonus, 7-Event/recruitment/year-end bonus, 8-Salary supplement, 9-Tet bonus
4. WHEN a payslip is generated, THE System SHALL record Section III (Bonuses Already Received) as manually entered amounts representing bonuses previously paid to the employee during the same payslip period
5. WHEN a payslip is generated, THE System SHALL calculate Section IV (Deductions) as the sum of 5 line items: 1-Insurance and union fees (BH+CĐ), 2-Đoàn phí, 3-Accumulation deductions (Tích lũy), 4-Personal Income Tax (Thuế TNCN), 5-Recovery amounts (Truy thu)
6. IF the payslip period is the year-end tax settlement month, THEN THE System SHALL calculate Section V (Tax Settlement Adjustments) as the difference between annual PIT liability and total PIT already deducted during the year
7. WHEN all payslip sections are calculated, THE System SHALL calculate Section VI (Net Pay) as: Total Income (Section II) minus Bonuses Already Received (Section III) minus Deductions (Section IV) plus or minus Tax Settlement Adjustments (Section V, zero if not applicable)
8. WHEN all payslip sections are calculated, THE System SHALL display the complete payslip with all six sections for review before finalization
9. IF any required input data is missing for payslip generation (including employee master data, Chức_Vụ/Cấp_Bậc_QL assignment, paid working days, or unit prices for assigned teaching), THEN THE System SHALL list each missing item by name and section, and prevent payslip generation until all items are provided

### Requirement 10: Report Generation and Export

**User Story:** As an Accountant, I want to generate reports and export data to Misa accounting software, so that salary data integrates with the school's financial systems.

#### Acceptance Criteria

1. THE System SHALL generate individual payslip documents containing the employee name, employee ID, pay period, salary breakdown by component, deductions, and net pay amount
2. THE System SHALL export salary data in Misa_Format compatible with Misa accounting software import, producing a file that matches the column structure required by Misa's bulk import function
3. THE System SHALL generate monthly attendance summary reports showing all Office_Staff attendance records for a user-specified calendar month
4. THE System SHALL generate monthly salary summary reports aggregating salary data across all employees, including totals by salary component and total net pay for a user-specified calendar month
5. THE System SHALL generate yearly attendance and salary summary reports for a user-specified calendar year (January to December)
6. WHEN a report is generated, THE System SHALL include the generation date, period covered, and the user who generated the report
7. THE System SHALL support exporting reports in PDF and Excel formats for payslip, attendance summary, and salary summary reports
8. THE System SHALL generate a teacher period summary report (BCC tổng tiết GV) showing total teaching periods per teacher for a user-specified month or year
9. IF report generation fails due to missing data for the specified period, THEN THE System SHALL display an error message indicating which data is unavailable and shall not produce a partial report

### Requirement 11: Data Import from Excel/CSV

**User Story:** As an Accountant, I want to import data from Excel and CSV files, so that I can efficiently transfer existing data into the system without manual re-entry.

#### Acceptance Criteria

1. THE System SHALL accept Excel (.xlsx, .xls) and CSV file formats for data import, with a maximum file size of 10 MB per upload
2. WHEN a file is uploaded for import, THE System SHALL validate the file structure against the expected template for the target data type (timetable, Misa attendance export, unit prices, changes, employee master data, external period data, support allowances)
3. IF the uploaded file structure does not match the expected template, THEN THE System SHALL display the list of missing or mismatched columns and reject the import without modifying existing data
4. WHEN data validation passes, THE System SHALL display a preview of the first 20 records to be imported along with the total row count, and require explicit user confirmation before committing
5. IF individual rows contain validation errors, THEN THE System SHALL list all errors (up to a maximum of 100 error entries) with corresponding row numbers and column names, and allow the user to fix the file and re-upload
6. THE System SHALL provide downloadable import templates for each data type (timetable, Misa attendance, unit prices, changes, employee master data, external period data, support allowances) in both .xlsx and .csv formats
7. WHEN an import is confirmed and committed successfully, THE System SHALL display a summary indicating the number of records inserted, the number of records updated, and the number of records skipped due to duplicates
8. IF a file contains records that duplicate existing data based on the natural key of the target data type, THEN THE System SHALL flag duplicate rows in the preview and allow the user to choose whether to skip duplicates or overwrite existing records

### Requirement 12: User Authentication and Access Control

**User Story:** As an Admin, I want role-based access control, so that users can only access features appropriate to their role.

#### Acceptance Criteria

1. WHEN a user attempts to access the System, THE System SHALL require authentication with username (4–50 characters) and password (minimum 8 characters, containing at least one uppercase letter, one lowercase letter, and one digit) before granting access
2. THE System SHALL support three roles: Admin (access to all system features including user management and system configuration), Accountant (access to salary data entry, salary calculations, and salary reports), and Viewer (read-only access to salary reports without ability to create, modify, or delete any data)
3. WHEN a user with Viewer role attempts to modify data, THE System SHALL deny the operation and display an access denied message indicating the action is not permitted for their role
4. WHEN a user with Accountant role attempts to manage users or system configuration, THE System SHALL deny the operation and display an access denied message indicating the action is not permitted for their role
5. THE System SHALL allow Admin users to create, modify, and deactivate user accounts, where each account requires at minimum a username, password, full name, and assigned role
6. WHEN a user session is inactive for more than 30 minutes, THE System SHALL require re-authentication and preserve no unsaved data from the expired session
7. THE System SHALL log all user login attempts (successful and failed), logout events, and access denied events with timestamps and the associated username
8. IF a user fails authentication 5 consecutive times, THEN THE System SHALL lock the account for 15 minutes and display a message indicating the account is temporarily locked
9. IF a deactivated user attempts to log in, THEN THE System SHALL deny access and display a message indicating the account is inactive
10. IF an Admin attempts to deactivate their own account while it is the only active Admin account, THEN THE System SHALL deny the operation and display a message indicating at least one Admin account must remain active

### Requirement 13: Multi-User Concurrent Access

**User Story:** As an Admin, I want the system to support multiple simultaneous users, so that the accounting team can work collaboratively without conflicts.

#### Acceptance Criteria

1. THE System SHALL support at least 5 concurrent users accessing the application simultaneously with no degradation in response time beyond 2 seconds per action
2. WHEN two users attempt to save changes to the same record concurrently, THE System SHALL reject the second save and notify the second user that a conflict has occurred
3. WHEN a conflict is detected, THE System SHALL display the current saved values to the conflicted user and preserve their unsaved input, allowing the user to reload the latest data and re-apply their changes
4. THE System SHALL maintain data consistency across all concurrent sessions such that no partial writes are visible and all reads reflect the last committed state
5. WHEN multiple users edit different records simultaneously, THE System SHALL process each save independently without triggering false conflict notifications
6. THE System SHALL detect conflicts at the individual record level, where a record corresponds to a single teacher's salary data for a given month

### Requirement 14: Salary Calculation Audit Trail

**User Story:** As an Admin, I want a complete audit trail of salary calculations, so that any salary figure can be traced back to its source data and the person who approved it.

#### Acceptance Criteria

1. WHEN a salary calculation is finalized, THE System SHALL record the calculation date, the user who performed the calculation, the user who approved it, and a snapshot of all input data used including employee Salary_Grade, Unit_Price, Lương_Khoán components (Chức_Vụ, Cấp_Bậc_QL, Nghiệp_Vụ, Kiêm_Nhiệm), allowances, deductions, and attendance data at the time of calculation
2. THE System SHALL retain all historical salary calculations for a minimum of 10 years and prevent any modification or deletion of finalized records through system-enforced immutability
3. WHEN a finalized payslip requires correction, THE System SHALL create a new revision linked to the original record, recording the user who initiated the correction, the reason for correction, the date of revision, and the updated values while preserving the original record unchanged
4. THE System SHALL log all changes to Unit_Price, Salary_Grade, Chức_Vụ unit prices, Cấp_Bậc_QL unit prices, and salary-relevant employee fields (position, department, contract type, allowances) with the user who made the change, timestamp, and previous values
5. WHEN an Admin requests an audit trace for a specific salary record, THE System SHALL display the complete history of that record including all revisions, the source data snapshot, and the identities of users who calculated, approved, or corrected it

### Requirement 15: MISA HR Data Import

**User Story:** As an HR staff member, I want to import employee HR data from MISA AMIS Excel templates (employee profiles, family/dependents, salary history, work history, qualifications, leave balances, organization structure, job positions), so that the system stays synchronized with MISA and I do not need to manually re-enter data.

#### Acceptance Criteria

1. THE System SHALL provide import endpoints for 9 MISA template types: Nhập khẩu hồ sơ nhân viên, Thông tin gia đình, Lịch sử lương, Quá trình công tác, Bằng cấp, Tổng hợp nghỉ phép, Cơ cấu tổ chức, Vị trí công việc, and Chấm công
2. THE System SHALL store extended employee profile fields compatible with MISA "Nhập khẩu hồ sơ" form including: giới tính, nơi sinh, nguyên quán, tình trạng hôn nhân, MST cá nhân, dân tộc, tôn giáo, quốc tịch, CMND/CCCD info (số, ngày cấp, nơi cấp, hết hạn), hộ chiếu info, trình độ văn hóa, trình độ đào tạo, nơi đào tạo, khoa, chuyên ngành, năm tốt nghiệp, xếp loại, liên lạc (ĐT cơ quan, ĐT nhà riêng, email cơ quan), lương cơ bản, bậc lương, tính chất lao động, quản lý trực tiếp/gián tiếp, TK ngân hàng, ngân hàng, bảo hiểm (tham gia, ngày tham gia, tỷ lệ đóng BHXH/BHYT/BHTN, số sổ BHXH, mã số BHXH, nơi đăng ký KCB), địa chỉ (HKTT, hiện nay), thuế suất, giảm trừ bản thân, mã chấm công, số ngày phép
3. THE System SHALL store Gia_Đình records including: họ tên người thân, quan hệ với nhân viên, giới tính, ngày sinh, quốc tịch, số CMND, SĐT, email, nghề nghiệp, MST cá nhân, nơi làm việc, cùng sổ hộ khẩu, đã mất, là người phụ thuộc, thời điểm tính/kết thúc giảm trừ
4. THE System SHALL store Lịch_Sử_Lương records including: ngày hiệu lực, loại lương (GROSS/NET), đơn vị công tác, vị trí công việc, bậc lương, lương cơ bản, tỷ lệ hưởng lương, khoản phụ cấp/giá trị/tính theo công/trạng thái, khoản khấu trừ/giá trị/tính theo công/trạng thái
5. THE System SHALL store Quá_Trình_Công_Tác records including: từ ngày, loại thủ tục, đơn vị công tác, bậc, trạng thái lao động, tính chất lao động, quản lý trực tiếp/gián tiếp, vị trí công việc, số quyết định, ngày quyết định
6. THE System SHALL store Bảng_Cấp records including: nơi đào tạo, từ năm, đến năm, khoa, chuyên ngành, trình độ đào tạo, hình thức, xếp loại, đã tốt nghiệp, ngày nhận bằng
7. THE System SHALL store Nghỉ_Phép_Balance records including: năm, số NP năm nay, số NP năm trước chuyển sang, số NP tăng theo thâm niên, số NP được thưởng khác, số NP đã hủy, số NP đã sử dụng không theo đơn
8. THE System SHALL extend dm_don_vi with MISA "Cơ cấu tổ chức" fields: mã đơn vị, thuộc đơn vị, địa chỉ, cấp tổ chức, trưởng đơn vị, chức năng nhiệm vụ, hạch toán, thứ tự sắp xếp, mã số ĐKKD
9. THE System SHALL extend dm_vi_tri with MISA "Vị trí công việc" fields: mã vị trí, đơn vị công tác, nhóm vị trí, chức danh, trạng thái
10. WHEN importing MISA data, THE System SHALL match employees by mã nhân viên (case-insensitive) and report errors for unmatched records while importing valid records
11. WHEN importing Cơ cấu tổ chức or Vị trí công việc, THE System SHALL upsert (update existing or create new) records based on name/code matching
12. THE System SHALL provide a dedicated "Import MISA" page with tabs for each import type, accessible to Admin, Accountant, and HR roles
