# generate payroll
from fastapi import APIRouter, Depends, HTTPException, status
from app import schemas, oauth2, utils
from app.dbase import conn, cursor
from . import employee

from datetime import datetime
import calendar

router = APIRouter(
    prefix="/payroll",
    tags=["Payroll"]
)

def compute_sss(employee: dict):
    emp = employee
    contrib = 0

    cursor.execute("SELECT MAX(min_val) FROM sss_matrix")
    max_val = cursor.fetchone()
    
    if emp['basic_salary'] >= max_val['max']:
        cursor.execute("SELECT MAX(contribution) FROM sss_matrix")
        max_contribution = cursor.fetchone()

        contrib = max_contribution['max']
    else:
        cursor.execute("SELECT * FROM sss_matrix AS sss WHERE %s BETWEEN sss.min_val AND sss.max_val", (emp['basic_salary'],))
        sss = cursor.fetchone()
        # print(sss)
        if not sss:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"SSS not found")

        contrib = sss['contribution']
        
    return contrib

def compute_salary(employee: dict, start_date: str, end_date: str):
    overtime = 0
    total_hours = 0

    cursor.execute("SELECT * FROM attendance WHERE employee_id = %s AND end_date BETWEEN %s AND %s", (employee['id'],start_date,end_date))
    attendance = cursor.fetchall()
    
    for att in attendance:
        if att['total_hours'] > 8 and att['overtime'] == 0:
            total_hours += 8
        else:
            total_hours += 8
            overtime += att['overtime']
    
    hourly_rate = employee['basic_salary']/21/8
    gross = (total_hours+overtime)*hourly_rate
      
    return total_hours, overtime, gross

def compute_tax(taxable_income: int):
    # print("taxable income", taxable_income)
    tax = 0
    if taxable_income <= 20832:
        return 0

    cursor.execute("SELECT * FROM tax_matrix AS tax WHERE %s BETWEEN tax.salary_min AND tax.salary_max", (taxable_income,))
    rate = cursor.fetchone()
    # print(rate)

    tax = (taxable_income - rate['salary_min']) * rate['excess_rate'] + rate['tax_rate']

    return tax

def compute_deductions(employee: dict):
    #philhealth
    phealth = employee['basic_salary']*0.03/2
    if phealth > 1800:
        phealth = 1800

    #pagibig
    pagibig = employee['basic_salary']*0.04/2
    if pagibig > 100:
        pagibig = 100
    
    # employee['basic_salary'] = 20000
    sss = compute_sss(employee)

    return phealth, pagibig, sss

@router.get("/")
def get_payrolls(current_user: dict = Depends(oauth2.get_current_user)):
    return employee.get_employees(current_user)

@router.post("/{id}")
def generate_payroll(id: int, current_user: dict = Depends(oauth2.get_current_user),start_date: str=datetime.date(datetime.today()).replace(day=1), 
                     end_date: str=datetime.date(datetime.today()).replace(day=calendar.monthrange(datetime.today().year, datetime.today().month)[1])):
    # set and check permissions
    # oauth2.check_permissions(current_user, ['admin'])
    # get employee
    cursor.execute("SELECT * FROM employee WHERE id = %s", (str(id),))
    employee = cursor.fetchone()
    
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Employee not found")
    
    #get gross salary
    total, overtime, gross = compute_salary(employee, start_date, end_date)
    print("basic salary", employee['basic_salary'])
    print("hourly rate", employee['basic_salary']/21/8)
    print("gross", gross)
    print("over time", overtime)
    print("total hours", total)
    
    #get deductions
    phealth, pagibig, sss = compute_deductions(employee)
    print("sss", sss)
    print("phealth", phealth)
    print("pagibig", pagibig)
    
    total_deductions = sss + phealth + pagibig
    print("total deductions", total_deductions)

    #get tax
    taxable_income = gross - total_deductions
    print("taxable income", taxable_income)

    tax = compute_tax(taxable_income)
    print("tax", tax)

    net_pay = gross - total_deductions - tax
    print("net pay", net_pay)

    return employee