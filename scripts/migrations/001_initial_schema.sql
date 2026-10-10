-- =============================================================================
-- Migration: 001_initial_schema.sql
-- Entities: departments, employees, task_items
-- Target: PostgreSQL 14+ / 16+ / 18+
-- =============================================================================

-- Enable pgcrypto / uuid-ossp for UUID generation if needed
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Clean up any legacy tables from previous prototypes if present
DROP TABLE IF EXISTS "daily_tasks" CASCADE;
DROP TABLE IF EXISTS "attendance_logs" CASCADE;
DROP TABLE IF EXISTS "processed_webhook_messages" CASCADE;
DROP TABLE IF EXISTS "payroll_records" CASCADE;
DROP TABLE IF EXISTS "payroll_periods" CASCADE;
DROP TABLE IF EXISTS "task_items" CASCADE;
DROP TABLE IF EXISTS "employees" CASCADE;
DROP TABLE IF EXISTS "departments" CASCADE;

-- Drop legacy enums if present
DO $$ BEGIN
    DROP TYPE IF EXISTS "Role";
    DROP TYPE IF EXISTS "AttendanceStatus";
    DROP TYPE IF EXISTS "AttendanceSource";
    DROP TYPE IF EXISTS "TaskStatus";
    DROP TYPE IF EXISTS "ProcessingStatus";
    DROP TYPE IF EXISTS "PayrollStatus";
    DROP TYPE IF EXISTS "PayrollRecordStatus";
EXCEPTION WHEN OTHERS THEN NULL;
END $$;

-- -----------------------------------------------------------------------------
-- 1. Departments Table
-- -----------------------------------------------------------------------------
CREATE TABLE "departments" (
    "id" TEXT PRIMARY KEY DEFAULT gen_random_uuid()::TEXT,
    "name" VARCHAR(100) NOT NULL,
    "created_at" TIMESTAMP(3) WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "departments_name_key" UNIQUE ("name")
);

-- -----------------------------------------------------------------------------
-- 2. Employees Table
-- -----------------------------------------------------------------------------
CREATE TABLE "employees" (
    "id" TEXT PRIMARY KEY DEFAULT gen_random_uuid()::TEXT,
    "employee_code" VARCHAR(50) NOT NULL,
    "full_name" VARCHAR(255) NOT NULL,
    "phone_number" VARCHAR(30) NOT NULL,
    "department_id" TEXT,
    "employment_type" VARCHAR(50) NOT NULL DEFAULT 'FULL_TIME',
    "monthly_base_salary" DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    "is_active" BOOLEAN NOT NULL DEFAULT TRUE,
    "created_at" TIMESTAMP(3) WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "employees_employee_code_key" UNIQUE ("employee_code"),
    CONSTRAINT "employees_phone_number_key" UNIQUE ("phone_number"),
    CONSTRAINT "employees_department_id_fkey" FOREIGN KEY ("department_id")
        REFERENCES "departments"("id") ON DELETE SET NULL ON UPDATE CASCADE
);

-- -----------------------------------------------------------------------------
-- 3. Task Items Table
-- -----------------------------------------------------------------------------
CREATE TABLE "task_items" (
    "id" TEXT PRIMARY KEY DEFAULT gen_random_uuid()::TEXT,
    "employee_id" TEXT NOT NULL,
    "task_description" TEXT NOT NULL,
    "created_at" TIMESTAMP(3) WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "task_items_employee_id_fkey" FOREIGN KEY ("employee_id")
        REFERENCES "employees"("id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- =============================================================================
-- Indexes
-- =============================================================================

-- Departments Indexes
CREATE INDEX IF NOT EXISTS "idx_departments_name" ON "departments"("name");
CREATE INDEX IF NOT EXISTS "idx_departments_created_at" ON "departments"("created_at");

-- Employees Indexes
CREATE INDEX IF NOT EXISTS "idx_employees_phone_number" ON "employees"("phone_number");
CREATE INDEX IF NOT EXISTS "idx_employees_employee_code" ON "employees"("employee_code");
CREATE INDEX IF NOT EXISTS "idx_employees_department_id" ON "employees"("department_id");
CREATE INDEX IF NOT EXISTS "idx_employees_is_active" ON "employees"("is_active");
CREATE INDEX IF NOT EXISTS "idx_employees_employment_type" ON "employees"("employment_type");

-- Task Items Indexes
CREATE INDEX IF NOT EXISTS "idx_task_items_employee_id" ON "task_items"("employee_id");
CREATE INDEX IF NOT EXISTS "idx_task_items_created_at" ON "task_items"("created_at");
CREATE INDEX IF NOT EXISTS "idx_task_items_employee_created" ON "task_items"("employee_id", "created_at" DESC);

-- =============================================================================
-- Automatic updated_at Trigger for employees
-- =============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS set_employees_updated_at ON "employees";
CREATE TRIGGER set_employees_updated_at
BEFORE UPDATE ON "employees"
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
