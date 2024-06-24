# generate payroll
from fastapi import APIRouter, Depends, HTTPException, status
from app import oauth2
from app.dbase import conn, cursor

from datetime import datetime
import calendar

router = APIRouter(
    prefix="/payroll",
    tags=["Payroll"]
)

@router.get("/")
def get_payrolls(current_user: dict = Depends(oauth2.get_current_user), start_date: str=datetime.date(datetime.today()).replace(day=1), end_date: str=datetime.date(datetime.today()).replace(day=calendar.monthrange(datetime.today().year, datetime.today().month)[1])):
    """
    Retrieve payrolls within a specified date range.

    Parameters:
    - current_user (dict): The current user's information obtained from the OAuth2 authentication.
    - start_date (str): The start date of the date range. Defaults to the first day of the current month.
    - end_date (str): The end date of the date range. Defaults to the last day of the current month.

    Returns:
    - List[dict]: A list of payrolls within the specified date range.

    Raises:
    - HTTPException: If no payrolls are found within the specified date range.
    """
   
    # set and check permissions
    oauth2.check_permissions(current_user, ['admin'])
    
    cursor.execute("SELECT * FROM payroll p WHERE p.start_date BETWEEN %s AND %s", (start_date,end_date))
    payrolls = cursor.fetchall()
    if not payrolls:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No payrolls found")
    
    return payrolls

@router.get("/{id}")
def get_payroll(id: int, current_user: dict = Depends(oauth2.get_current_user)):
    """
    Retrieve payroll information based on the specified ID.

    Parameters:
    - id (int): The ID of the payroll.
    - current_user (dict): The current user's information obtained from the OAuth2 authentication.

    Returns:
    - dict: The payroll information.

    Raises:
    - HTTPException: If the payroll is not found.
    """
    # set and check permissions
    oauth2.check_permissions(current_user, ['admin'])
    
    cursor.execute("SELECT * FROM payroll WHERE id = %s", (str(id),))
    payroll = cursor.fetchone()
    if not payroll:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payroll not found")
    
    return payroll

@router.get("/monthly_payroll")
def get_monthly_payroll(current_user: dict = Depends(oauth2.get_current_user), start_date: str=datetime.date(datetime.today()).replace(day=1), end_date: str=datetime.date(datetime.today()).replace(day=calendar.monthrange(datetime.today().year, datetime.today().month)[1])):
    """
    Retrieve monthly payroll information.

    Parameters:
    - current_user (dict): The current user's information obtained from the OAuth2 authentication.

    Returns:
    - List[dict]: A list of monthly payroll information.

    Raises:
    - HTTPException: If no payrolls are found.
    """
    # set and check permissions
    oauth2.check_permissions(current_user, ['admin'])
    
    cursor.execute("SELECT * FROM payroll p JOIN employee e ON p.employee_id=e.id WHERE p.start_date BETWEEN %s AND %s;", (start_date,end_date))
    payrolls = cursor.fetchall()
    if not payrolls:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No payrolls found")
    
    return payrolls

@router.get("/monthly_summary")
def get_monthly_summary(current_user: dict = Depends(oauth2.get_current_user), start_date: str=datetime.date(datetime.today()).replace(day=1), end_date: str=datetime.date(datetime.today()).replace(day=calendar.monthrange(datetime.today().year, datetime.today().month)[1])):
    """
    Retrieve monthly payroll summary.

    Parameters:
    - current_user (dict): The current user's information obtained from the OAuth2 authentication.

    Returns:
    - dict: The monthly payroll summary.

    Raises:
    - HTTPException: If no payrolls are found.
    """
    # set and check permissions
    # oauth2.check_permissions(current_user, ['admin'])
    
    cursor.execute("SELECT SUM(gross_pay) as total_gross, SUM(net_pay) as total_net, SUM(total_deductions) as total_deductions, SUM(total_perks) as total_perks, SUM(tax) as total_tax FROM payroll WHERE start_date BETWEEN %s AND %s", (start_date,end_date))
    summary = cursor.fetchone()
    if not summary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No payrolls found")
    
    summary['start_date'] = start_date
    summary['end_date'] = end_date
    return summary

@router.post("/{id}")
def generate_payroll(id: int, current_user: dict = Depends(oauth2.get_current_user),start_date: str=datetime.date(datetime.today()).replace(day=1), 
                     end_date: str=datetime.date(datetime.today()).replace(day=calendar.monthrange(datetime.today().year, datetime.today().month)[1])):
    """
    Generate payroll for an employee based on their attendance and salary information.

    Args:
        id (int): The ID of the employee.
        current_user (dict, optional): The current user. Defaults to the result of `oauth2.get_current_user`.
        start_date (str, optional): The start date of the payroll period. Defaults to the first day of the current month.
        end_date (str, optional): The end date of the payroll period. Defaults to the last day of the current month.

    Returns:
        dict: The generated payroll information.

    Raises:
        HTTPException: If the employee is not found or has no attendance records.
    """
    # set and check permissions
    oauth2.check_permissions(current_user, ['admin'])

    # check if employee exists
    cursor.execute("SELECT * FROM employee WHERE id = %s", (str(id),))
    employee = cursor.fetchone()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Employee not found")
    
    # check if employee have attendance
    cursor.execute("SELECT * FROM attendance WHERE employee_id = %s AND end_date BETWEEN %s AND %s", (str(id),start_date,end_date))
    attendance = cursor.fetchall()
    if not attendance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No attendance")
    
    # check if payroll is already generated
    # cursor.execute("SELECT * FROM payroll WHERE employee_id = %s AND start_date = %s AND end_date = %s", (str(id),start_date,end_date))
    # payroll = cursor.fetchone()
    # if payroll:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Payroll already generated")

    #get gross salary
    total_hours, overtime, gross, days = compute_salary(employee, start_date, end_date)
    
    #get deductions
    philhealth, pagibig, sss = compute_deductions(employee)
    total_deductions = sss + philhealth + pagibig

    #get perks
    total_perks, perks = compute_perks(employee)

    #get taxable income
    taxable_income = gross - total_deductions
    # taxable_income = 20832
    tax = compute_tax(taxable_income)

    total_deductions += round(tax,2)

    net_pay = round(gross - total_deductions - tax,2)

    take_home_pay = net_pay + total_perks

    # create payroll
    try:
        cursor.execute("INSERT INTO payroll (employee_id, start_date, end_date, total_hours, overtime, gross_pay, days, net_pay, \
                    total_deductions, total_perks, basic_salary, take_home,tax) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
                    RETURNING *", (str(id),start_date,end_date,total_hours,overtime,gross,days,net_pay,total_deductions,total_perks,
                                    employee['basic_salary'],take_home_pay,tax))
        payroll = cursor.fetchone()
        conn.commit()
    except Exception as e:
        cursor.execute("ROLLBACK")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error: {e}")

    # create deductions
    try:
        deduction_list = [(philhealth,payroll['id'],"philhealth"),
                        (pagibig,payroll['id'],"pagibig"),
                            (sss,payroll['id'],"sss")]
        cursor.executemany("INSERT INTO pay_deduction (amount, payroll_id, name) VALUES (%s, %s, %s) RETURNING *", deduction_list)
        conn.commit()
    except Exception as e:
        cursor.execute("ROLLBACK")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error: {e}")

    # create benefits
    try:
        perk_list = []
        for perk in perks:
            perk_list.append((payroll['id'],perk['amount'],perk['perk_id']))
        cursor.executemany("INSERT INTO pay_perk (payroll_id, amount, perk_id) VALUES (%s, %s, %s) RETURNING *", perk_list)
        conn.commit()
    except Exception as e:
        cursor.execute("ROLLBACK")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error: {e}")

    return payroll

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
        if not sss:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"SSS not found")

        contrib = sss['contribution']
        
    return contrib

def compute_salary(employee: dict, start_date: str, end_date: str):
    overtime = 0
    total_hours = 0
    days = 0
    hourly_rate = employee['basic_salary']/20/8

    cursor.execute("SELECT * FROM attendance WHERE employee_id = %s AND end_date BETWEEN %s AND %s", (employee['id'],start_date,end_date))
    attendance = cursor.fetchall()

    if not attendance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No attendance")
    
    for att in attendance:
        days += 1
        if att['total_hours'] > 8 and att['overtime'] == 0:
            total_hours += 8
        else:
            total_hours += 8
            overtime += att['overtime']
    
    gross = (total_hours+overtime)*hourly_rate
      
    return total_hours, overtime, gross, days

def compute_tax(taxable_income: int):
    tax = 0
    cursor.execute("SELECT MIN(salary_max) FROM tax_matrix")
    max_val = cursor.fetchone()
    
    if taxable_income <= max_val['min']:
        return 0

    cursor.execute("SELECT * FROM tax_matrix AS tax WHERE %s BETWEEN tax.salary_min AND tax.salary_max", (taxable_income,))
    rate = cursor.fetchone()
    if not rate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tax rate not found")

    tax = (taxable_income - rate['salary_min']) * rate['excess_rate'] + rate['tax_rate']

    return tax

def compute_deductions(employee: dict):
    philhealth = employee['basic_salary']*0.03/2
    if philhealth > 1800:
        philhealth = 1800

    pagibig = employee['basic_salary']*0.04/2
    if pagibig > 100:
        pagibig = 100
    
    # employee['basic_salary'] = 20000
    sss = compute_sss(employee)

    return philhealth, pagibig, sss

def compute_perks(employee: dict):
    total_perks = 0
    cursor.execute("SELECT * FROM emp_perk WHERE employee_id = %s", (employee['id'],))
    perks = cursor.fetchall()
    for perk in perks:
        total_perks += perk['amount']

    return total_perks, perks

def test_compute_deuctions():
    employee = {"basic_salary": 20000}
    philhealth, pagibig, sss = compute_deductions(employee)
    assert philhealth == 900
    assert pagibig == 100
    assert sss == 581.3