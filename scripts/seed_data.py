#!/usr/bin/env python3
"""
Seed Script for PostgreSQL Database.
Populates initial sample records for:
1. departments
2. employees (with unique codes and indexed phone numbers)
3. task_items
"""

import asyncio
import os
import sys
from decimal import Decimal
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = BASE_DIR / "backend"
sys.path.append(str(BACKEND_DIR))

load_dotenv(BACKEND_DIR / ".env")


async def seed():
    from app.core.database import db_client

    print("=" * 60)
    print("Seeding Database (departments, employees, task_items)")
    print("=" * 60)

    await db_client.connect()

    try:
        # 1. Seed Departments
        departments_data = [
            "Engineering",
            "Operations",
            "Human Resources",
            "Sales & Marketing",
            "Customer Support",
        ]

        dept_map = {}
        for dept_name in departments_data:
            row = await db_client.fetchrow(
                """
                INSERT INTO departments (name)
                VALUES ($1)
                ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
                RETURNING id, name;
                """,
                dept_name,
            )
            dept_map[row["name"]] = row["id"]
            print(f"  [Department] {row['name']} -> ID: {row['id']}")

        # 2. Seed Employees
        employees_data = [
            {
                "employee_code": "EMP-101",
                "full_name": "Kasun Perera",
                "phone_number": "+94771234567",
                "department": "Engineering",
                "employment_type": "FULL_TIME",
                "monthly_base_salary": Decimal("185000.00"),
                "is_active": True,
            },
            {
                "employee_code": "EMP-102",
                "full_name": "Nimali Silva",
                "phone_number": "+94779876543",
                "department": "Engineering",
                "employment_type": "FULL_TIME",
                "monthly_base_salary": Decimal("210000.00"),
                "is_active": True,
            },
            {
                "employee_code": "EMP-103",
                "full_name": "Sarah Fernando",
                "phone_number": "+94712345678",
                "department": "Human Resources",
                "employment_type": "FULL_TIME",
                "monthly_base_salary": Decimal("160000.00"),
                "is_active": True,
            },
            {
                "employee_code": "EMP-104",
                "full_name": "Dinesh Gunawardena",
                "phone_number": "+94765432109",
                "department": "Operations",
                "employment_type": "FULL_TIME",
                "monthly_base_salary": Decimal("145000.00"),
                "is_active": True,
            },
            {
                "employee_code": "EMP-105",
                "full_name": "Ruwan Jayasinghe",
                "phone_number": "+94723456789",
                "department": "Sales & Marketing",
                "employment_type": "CONTRACT",
                "monthly_base_salary": Decimal("120000.00"),
                "is_active": True,
            },
            {
                "employee_code": "EMP-106",
                "full_name": "Anusha Wickramasinghe",
                "phone_number": "+94756789012",
                "department": "Customer Support",
                "employment_type": "PART_TIME",
                "monthly_base_salary": Decimal("95000.00"),
                "is_active": True,
            },
        ]

        emp_map = {}
        for emp in employees_data:
            dept_id = dept_map.get(emp["department"])
            row = await db_client.fetchrow(
                """
                INSERT INTO employees (
                    employee_code, full_name, phone_number, department_id,
                    employment_type, monthly_base_salary, is_active
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (employee_code) DO UPDATE SET
                    full_name = EXCLUDED.full_name,
                    phone_number = EXCLUDED.phone_number,
                    department_id = EXCLUDED.department_id,
                    employment_type = EXCLUDED.employment_type,
                    monthly_base_salary = EXCLUDED.monthly_base_salary,
                    is_active = EXCLUDED.is_active
                RETURNING id, employee_code, full_name;
                """,
                emp["employee_code"],
                emp["full_name"],
                emp["phone_number"],
                dept_id,
                emp["employment_type"],
                emp["monthly_base_salary"],
                emp["is_active"],
            )
            emp_map[row["employee_code"]] = row["id"]
            print(f"  [Employee] {row['employee_code']} - {row['full_name']} -> ID: {row['id']}")

        # 3. Seed Task Items
        tasks_data = [
            ("EMP-101", "Designed and implemented PostgreSQL connection pooling module using asyncpg"),
            ("EMP-101", "Integrated database migration runner with automated schema sync"),
            ("EMP-101", "Fixed edge-case connection leak in long-running background tasks"),
            ("EMP-102", "Configured Prisma Python client models and index definitions"),
            ("EMP-102", "Optimized SQL query performance for employee department lookups"),
            ("EMP-103", "Onboarded three new engineering hires and processed tax documentation"),
            ("EMP-103", "Reviewed quarterly performance appraisals and compensation bands"),
            ("EMP-104", "Inspected server resource utilization across production database clusters"),
            ("EMP-104", "Set up automated backup verification jobs on local storage"),
            ("EMP-105", "Prepared client proposal deck for Q4 enterprise attendance software rollout"),
            ("EMP-105", "Conducted product walkthrough demo with regional partner teams"),
            ("EMP-106", "Resolved 14 incoming support inquiries regarding employee code formatting"),
            ("EMP-106", "Documented troubleshooting guide for WhatsApp webhook delivery errors"),
        ]

        # Clear existing tasks to allow clean re-seeding
        await db_client.execute("DELETE FROM task_items;")

        task_count = 0
        for emp_code, description in tasks_data:
            emp_id = emp_map.get(emp_code)
            if emp_id:
                await db_client.execute(
                    """
                    INSERT INTO task_items (employee_id, task_description)
                    VALUES ($1, $2);
                    """,
                    emp_id,
                    description,
                )
                task_count += 1

        print(f"  [Task Items] Seeded {task_count} task items across {len(emp_map)} employees.")

        # Summary query
        dept_cnt = await db_client.fetchval("SELECT COUNT(*) FROM departments;")
        emp_cnt = await db_client.fetchval("SELECT COUNT(*) FROM employees;")
        tsk_cnt = await db_client.fetchval("SELECT COUNT(*) FROM task_items;")

        print("=" * 60)
        print("Seeding Summary:")
        print(f"  - Total Departments: {dept_cnt}")
        print(f"  - Total Employees:   {emp_cnt}")
        print(f"  - Total Task Items:  {tsk_cnt}")
        print("=" * 60)

    finally:
        await db_client.disconnect()


if __name__ == "__main__":
    asyncio.run(seed())
