import qrcode
from datetime import datetime
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from tkinter import Tk, Label, Entry, Button, Text, END, messagebox

class BillManager:
    """Manages bills locally using a JSON file as storage."""
    def __init__(self, storage_file='bills.json'):
        self.storage_file = storage_file
        self.bills = self.load_bills()

    def load_bills(self):
        """Load bills from local storage."""
        if os.path.exists(self.storage_file):
            with open(self.storage_file, 'r') as file:
                return json.load(file)
        return {}

    def save_bills(self):
        """Save bills to local storage."""
        with open(self.storage_file, 'w') as file:
            json.dump(self.bills, file, indent=4)

    def save_bill(self, bill_id, customer_name, total_amount, qr_code_path, items):
        """Save a new bill, ensuring unique bill ID."""
        if bill_id in self.bills:
            raise ValueError(f"Bill ID '{bill_id}' already exists.")

        self.bills[bill_id] = {
            'customer_name': customer_name,
            'total_amount': total_amount,
            'timestamp': datetime.now().isoformat(),
            'qr_code_path': qr_code_path,
            'items': items
        }
        self.save_bills()

    def get_bill_details(self, bill_id):
        """Retrieve bill details by ID."""
        return self.bills.get(bill_id, None)

    def generate_report(self):
        """Generate a summary report of all bills."""
        report = """Bill Report\n===========\n"""
        for bill_id, details in self.bills.items():
            report += f"Bill ID: {bill_id}\nCustomer: {details['customer_name']}\nTotal: {details['total_amount']}\nDate: {details['timestamp']}\n---\n"
        return report

def validate_input(customer_name, bill_id, items):
    """Validate user input for bills."""
    if not customer_name or not customer_name.strip():
        raise ValueError("Customer name cannot be empty.")

    if not bill_id or not bill_id.strip():
        raise ValueError("Bill ID cannot be empty.")

    if not items:
        raise ValueError("At least one item must be added.")

    for item in items:
        if item['price'] <= 0:
            raise ValueError(f"Price for {item['name']} must be positive.")
        if item['quantity'] <= 0:
            raise ValueError(f"Quantity for {item['name']} must be positive.")

def generate_shopping_qr(customer_name, bill_id, items, filename=None, qr_color="black", background_color="white"):
    """Generate a QR code for shopping details."""
    total_bill = sum(item['price'] * item['quantity'] for item in items)
    bill_details = f"Customer Name: {customer_name}\nBill ID: {bill_id}\n\nItems:\n"
    for item in items:
        bill_details += f"- {item['name']} (Price: {item['price']}, Quantity: {item['quantity']})\n"
    bill_details += f"\nTotal: {total_bill}"

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(bill_details)
    qr.make(fit=True)
    img = qr.make_image(fill_color=qr_color, back_color=background_color)

    if filename is None:
        filename = f"bill_{bill_id}_{customer_name.replace(' ', '_')}.png"

    img.save(filename)
    return filename

def send_email(email_address, subject, body):
    """Send an email with the given subject and body."""
    try:
        sender_email = "your_email@example.com"  # Replace with your email
        sender_password = "your_password"  # Replace with your email password

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email_address
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)

        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def main():
    """Main program function with a simple GUI."""
    bill_manager = BillManager()

    def add_bill():
        try:
            customer_name = name_entry.get()
            bill_id = id_entry.get()
            items_text = items_entry.get("1.0", END).strip()
            items = json.loads(items_text)  # Expects JSON format for items

            validate_input(customer_name, bill_id, items)

            qr_path = generate_shopping_qr(customer_name, bill_id, items)
            total_bill = sum(item['price'] * item['quantity'] for item in items)
            bill_manager.save_bill(bill_id, customer_name, total_bill, qr_path, items)

            messagebox.showinfo("Success", f"Bill saved and QR code generated at {qr_path}.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_report():
        report = bill_manager.generate_report()
        report_window = Tk()
        report_window.title("Bill Report")
        report_text = Text(report_window, wrap="word")
        report_text.insert("1.0", report)
        report_text.pack()
        report_window.mainloop()

    app = Tk()
    app.title("Shopping Bill Manager")

    Label(app, text="Customer Name:").grid(row=0, column=0)
    name_entry = Entry(app)
    name_entry.grid(row=0, column=1)

    Label(app, text="Bill ID:").grid(row=1, column=0)
    id_entry = Entry(app)
    id_entry.grid(row=1, column=1)

    Label(app, text="Items (JSON format):").grid(row=2, column=0)
    items_entry = Text(app, height=10, width=40)
    items_entry.grid(row=2, column=1)

    Button(app, text="Add Bill", command=add_bill).grid(row=3, column=0, columnspan=2)
    Button(app, text="Show Report", command=show_report).grid(row=4, column=0, columnspan=2)

    app.mainloop()

if __name__ == "__main__":
    main()

