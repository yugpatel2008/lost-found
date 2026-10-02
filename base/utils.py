"""
Decoupled Utility Services for Indus Uni. Lost & Found
Contains email notifications, Excel parsers, and password generators with lazy imports.
"""
from django.contrib.auth import get_user_model

def get_user_model_lazy():
    return get_user_model()


# ─── Email Services ───────────────────────────────────────────────────────────

def send_credentials_email_async(user, raw_password, request=None):
    """Dispatches a welcome email with credentials in a non-blocking background thread."""
    import threading

    def _worker():
        try:
            from django.core.mail import EmailMultiAlternatives

            login_url = request.build_absolute_uri('/login/') if request else "http://127.0.0.1:8000/login/"
            role_display = user.profile.get_role_display() if hasattr(user, 'profile') else 'Student'
            dept_display = (user.profile.department or 'N/A') if hasattr(user, 'profile') else 'N/A'

            subject = "[Indus Uni. Lost & Found] Your Account Credentials"
            text_body = (
                f"Welcome to Indus Uni. Lost & Found!\n\n"
                f"An account has been created for you by your institution administrator.\n\n"
                f"Your Login Credentials:\n"
                f"• Email / Username: {user.email}\n"
                f"• Password: {raw_password}\n"
                f"• Role: {role_display}\n"
                f"• Department: {dept_display}\n\n"
                f"Sign in here: {login_url}\n"
            )

            html_body = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
              <meta charset="UTF-8">
              <meta name="viewport" content="width=device-width, initial-scale=1.0">
            </head>
            <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f1f5f9; margin: 0; padding: 20px 10px;">
              <table role="presentation" cellspacing="0" cellpadding="0" border="0" align="center" style="max-width: 580px; width: 100%; margin: 0 auto; background-color: #ffffff; border-radius: 20px; overflow: hidden; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05); border: 1px solid #e2e8f0;">
                <tr>
                  <td style="background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4338ca 100%); padding: 36px 28px; text-align: center;">
                    <div style="display: inline-block; background: rgba(255, 255, 255, 0.12); padding: 6px 16px; border-radius: 99px; margin-bottom: 12px; border: 1px solid rgba(255, 255, 255, 0.2);">
                      <span style="color: #a5b4fc; font-size: 12px; font-weight: 700; uppercase;">Indus Uni. Lost &amp; Found</span>
                    </div>
                    <h1 style="color: #ffffff; margin: 0; font-size: 24px; font-weight: 800;">Welcome to the Portal</h1>
                    <p style="color: #c7d2fe; margin: 8px 0 0 0; font-size: 14px;">Your official institutional login credentials</p>
                  </td>
                </tr>
                <tr>
                  <td style="padding: 32px 28px;">
                    <p style="color: #1e293b; font-size: 16px; font-weight: 700; margin: 0 0 8px 0;">Hello {user.first_name or user.username},</p>
                    <p style="color: #475569; font-size: 14px; line-height: 1.6; margin: 0 0 24px 0;">Below are your login credentials to sign in to the portal:</p>
                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="width: 100%; background-color: #f8fafc; border-radius: 14px; border: 1px solid #cbd5e1; overflow: hidden; margin-bottom: 28px;">
                      <tr>
                        <td style="padding: 16px 20px; border-bottom: 1px solid #e2e8f0; background-color: #f1f5f9;">
                          <span style="color: #64748b; font-size: 11px; font-weight: 700; text-transform: uppercase;">Account Email / Username</span>
                          <div style="color: #0f172a; font-size: 15px; font-weight: 700; font-family: monospace; word-break: break-all;">{user.email}</div>
                        </td>
                      </tr>
                      <tr>
                        <td style="padding: 16px 20px; border-bottom: 1px solid #e2e8f0; background-color: #eff6ff;">
                          <span style="color: #1d4ed8; font-size: 11px; font-weight: 700; text-transform: uppercase;">Temporary Password</span>
                          <div style="color: #2563eb; font-size: 18px; font-weight: 800; font-family: monospace; word-break: break-all;">{raw_password}</div>
                        </td>
                      </tr>
                      <tr>
                        <td style="padding: 14px 20px; border-bottom: 1px solid #e2e8f0;">
                          <span style="color: #64748b; font-size: 11px; font-weight: 700; text-transform: uppercase;">Role</span>
                          <div style="color: #334155; font-size: 14px; font-weight: 600;">{role_display}</div>
                        </td>
                      </tr>
                      <tr>
                        <td style="padding: 14px 20px;">
                          <span style="color: #64748b; font-size: 11px; font-weight: 700; text-transform: uppercase;">Department</span>
                          <div style="color: #334155; font-size: 14px; font-weight: 600;">{dept_display}</div>
                        </td>
                      </tr>
                    </table>
                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" align="center" style="margin: 0 auto 24px auto;">
                      <tr>
                        <td align="center" style="border-radius: 12px; background-color: #4338ca;">
                          <a href="{login_url}" target="_blank" style="font-size: 15px; font-weight: 700; color: #ffffff; text-decoration: none; padding: 14px 32px; border-radius: 12px; display: inline-block;">Sign In &rarr;</a>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>
            </body>
            </html>
            """
            msg = EmailMultiAlternatives(subject=subject, body=text_body, to=[user.email])
            msg.attach_alternative(html_body, 'text/html')
            msg.send(fail_silently=False)
            print(f"[CREDENTIALS EMAIL SUCCESS] Sent to {user.email}")
        except Exception as e:
            print(f"[CREDENTIALS EMAIL ERROR] {e}")

    t = threading.Thread(target=_worker)
    t.daemon = True
    t.start()


# ─── Excel / File Parser Services (Lazy Loaded) ───────────────────────────────

def parse_user_import_data(uploaded_file=None, pasted_text='', default_department='', default_role='student'):
    """
    Parses user import records from an uploaded Excel (.xlsx/.xls/.csv) file or CSV text lines.
    Lazily imports openpyxl, csv, and io on demand.
    Returns a list of dicts: [{'email': ..., 'first_name': ..., 'last_name': ..., 'department': ..., 'role': ...}]
    """
    records = []
    raw_rows = []

    if uploaded_file:
        filename = uploaded_file.name.lower()
        if filename.endswith(('.xlsx', '.xls')):
            import openpyxl
            wb = openpyxl.load_workbook(uploaded_file, data_only=True)
            sheet = wb.active
            for r in sheet.iter_rows(values_only=True):
                if r and any(r):
                    raw_rows.append([str(c or '').strip() for c in r])
        elif filename.endswith('.csv'):
            import csv
            import io
            decoded = uploaded_file.read().decode('utf-8-sig', errors='ignore')
            reader = csv.reader(io.StringIO(decoded))
            for r in reader:
                if r and any(r):
                    raw_rows.append([str(c or '').strip() for c in r])

    elif pasted_text:
        lines = pasted_text.splitlines()
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                parts = [p.strip() for p in line.split(',')]
                raw_rows.append(parts)

    for idx, row in enumerate(raw_rows):
        if not row or len(row) == 0:
            continue

        email_candidate = row[0].strip().lower()

        # Skip header line
        if idx == 0 and ('email' in email_candidate or 'mail' in email_candidate):
            continue

        if '@' not in email_candidate:
            continue

        email = email_candidate
        first_name = row[1].strip() if len(row) > 1 else ''
        last_name  = row[2].strip() if len(row) > 2 else ''
        department = row[3].strip() if len(row) > 3 and row[3].strip() else default_department
        role       = row[4].strip().lower() if len(row) > 4 and row[4].strip() else default_role

        records.append({
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'department': department,
            'role': role,
        })

    return records


def generate_sample_excel_response():
    """Generates an in-memory sample .xlsx spreadsheet response using lazy openpyxl."""
    import openpyxl
    import io
    from django.http import HttpResponse

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Students Import Sample"

    ws.append(['Email', 'First Name', 'Last Name', 'Department', 'Role'])
    ws.append(['rahul.sharma@iite.indusuni.ac.in', 'Rahul', 'Sharma', 'Computer Department', 'student'])
    ws.append(['priya.patel@iite.indusuni.ac.in', 'Priya', 'Patel', 'IT Department', 'student'])
    ws.append(['vikram.mehta@indusuni.ac.in', 'Vikram', 'Mehta', 'Mechanical Department', 'teacher'])

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=student_import_sample.xlsx'
    return response
