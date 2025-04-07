# utils/pdf_generator.py
from PyQt6.QtGui import QTextDocument, QPainter, QPageSize
from PyQt6.QtPrintSupport import QPrinter
from PyQt6.QtCore import QSizeF, Qt
import os
import datetime

class PDFGenerator:
    """Generates PDF files for invoices and reports."""
    
    def __init__(self, settings=None):
        self.settings = settings
    
    def generate_invoice_pdf(self, invoice, output_path=None):
        """Generate a PDF for an invoice."""
        # Get clinic info from settings
        clinic_name = "مركز جوزيل للتجميل"
        clinic_phone = "+963956961395"
        clinic_address = "سوريا - ريف دمشق التل موقف طيبة مقابل امركز الثقافي الجديد"
        
        if self.settings:
            clinic_name = self.settings.get_setting("clinic_info.name", clinic_name)
            clinic_phone = self.settings.get_setting("clinic_info.phone", clinic_phone)
            clinic_address = self.settings.get_setting("clinic_info.address", clinic_address)
        
        # Format date
        date_str = invoice["date"]
        if "T" in date_str:
            date_str = date_str.split("T")[0]
        
        # Format payment method
        if invoice["payment_method"] == "cash":
            payment_method = "نقدي"
        else:
            payment_method = "تقسيط"
        
        # Generate HTML
        html = f"""
        <html dir="rtl">
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ text-align: center; margin-bottom: 20px; }}
                .invoice-info {{ display: flex; justify-content: space-between; margin-bottom: 20px; }}
                .invoice-info div {{ width: 45%; }}
                table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: right; }}
                th {{ background-color: #f2f2f2; }}
                .total {{ text-align: left; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{clinic_name}</h1>
                <p>{clinic_address}</p>
                <p>{clinic_phone}</p>
                <h2>فاتورة #{invoice["id"]}</h2>
            </div>
            
            <div class="invoice-info">
                <div>
                    <p><strong>اسم العميل:</strong> {invoice["customer_name"]}</p>
                    <p><strong>الهاتف:</strong> {invoice["customer_phone"]}</p>
                </div>
                <div>
                    <p><strong>التاريخ:</strong> {date_str}</p>
                    <p><strong>طريقة الدفع:</strong> {payment_method}</p>
                </div>
            </div>
            
            <table>
                <tr>
                    <th>#</th>
                    <th>الخدمة</th>
                    <th>السعر</th>
                </tr>
        """
        
        # Add services
        for i, service in enumerate(invoice["services"]):
            price = service["price"]
            quantity = service.get("quantity", 1)
            total_price = price * quantity
            
            html += f"""
                <tr>
                    <td>{i+1}</td>
                    <td>{service["name"]}</td>
                    <td>{total_price:,.0f} ل.س</td>
                </tr>
            """
        
        # Add totals
        html += f"""
                <tr>
                    <td colspan="2" class="total">المبلغ الإجمالي</td>
                    <td>{invoice["total_amount"]:,.0f} ل.س</td>
                </tr>
                <tr>
                    <td colspan="2" class="total">المبلغ المدفوع</td>
                    <td>{invoice["amount_paid"]:,.0f} ل.س</td>
                </tr>
        """
        
        if invoice["amount_remaining"] > 0:
            html += f"""
                <tr>
                    <td colspan="2" class="total">المبلغ المتبقي</td>
                    <td>{invoice["amount_remaining"]:,.0f} ل.س</td>
                </tr>
            """
        
        html += f"""
            </table>
            
            <div>
                <p><strong>مقدم الخدمة:</strong> {invoice["service_provider"]}</p>
                <p><strong>منشئ الفاتورة:</strong> {invoice["invoice_creator"]}</p>
            </div>
        </body>
        </html>
        """
        
        # Create PDF
        document = QTextDocument()
        document.setHtml(html)
        
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        
        # Set output path
        if not output_path:
            # Create output directory if it doesn't exist
            os.makedirs("invoices", exist_ok=True)
            
            # Generate filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"invoices/invoice_{invoice['id']}_{timestamp}.pdf"
        
        printer.setOutputFileName(output_path)
        
        # Print document to PDF
        document.print_(printer)
        
        return output_path
    
    def generate_daily_report_pdf(self, date, invoices, total_revenue, output_path=None):
        """Generate a PDF for a daily report."""
        # Get clinic info from settings
        clinic_name = "مركز جوزيل للتجميل"
        clinic_phone = "+963956961395"
        clinic_address = "سوريا - ريف دمشق التل موقف طيبة مقابل امركز الثقافي الجديد"
        
        if self.settings:
            clinic_name = self.settings.get_setting("clinic_info.name", clinic_name)
            clinic_phone = self.settings.get_setting("clinic_info.phone", clinic_phone)
            clinic_address = self.settings.get_setting("clinic_info.address", clinic_address)
        
        # Format date
        date_str = date.strftime("%Y-%m-%d")
        
        # Generate HTML
        html = f"""
        <html dir="rtl">
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ text-align: center; margin-bottom: 20px; }}
                table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: right; }}
                th {{ background-color: #f2f2f2; }}
                .total {{ text-align: left; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{clinic_name}</h1>
                <p>{clinic_address}</p>
                <p>{clinic_phone}</p>
                <h2>تقرير يومي - {date_str}</h2>
            </div>
            
            <table>
                <tr>
                    <th>#</th>
                    <th>رقم الفاتورة</th>
                    <th>اسم العميل</th>
                    <th>الخدمات</th>
                    <th>المبلغ المدفوع</th>
                </tr>
        """
        
        # Add invoices
        for i, invoice in enumerate(invoices):
            services = ", ".join([service["name"] for service in invoice["services"]])
            
            html += f"""
                <tr>
                    <td>{i+1}</td>
                    <td>{invoice["id"]}</td>
                    <td>{invoice["customer_name"]}</td>
                    <td>{services}</td>
                    <td>{invoice["amount_paid"]:,.0f} ل.س</td>
                </tr>
            """
        
        # Add total
        html += f"""
                <tr>
                    <td colspan="4" class="total">المجموع</td>
                    <td>{total_revenue:,.0f} ل.س</td>
                </tr>
            </table>
            
            <div>
                <p><strong>عدد الفواتير:</strong> {len(invoices)}</p>
                <p><strong>تاريخ التقرير:</strong> {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </div>
        </body>
        </html>
        """
        
        # Create PDF
        document = QTextDocument()
        document.setHtml(html)
        
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        
        # Set output path
        if not output_path:
            # Create output directory if it doesn't exist
            os.makedirs("reports", exist_ok=True)
            
            # Generate filename
            output_path = f"reports/daily_report_{date_str}.pdf"
        
        printer.setOutputFileName(output_path)
        
        # Print document to PDF
        document.print_(printer)
        
        return output_path
