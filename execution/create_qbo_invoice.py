"""
QuickBooks Online Invoice Creation Script

This script creates invoices in QuickBooks Online from order form data.
Handles customer lookup/creation, line items, tax calculation, and PDF generation.

Usage:
    python create_qbo_invoice.py --data order_data.json

Requirements:
    pip install intuitlib requests python-dotenv
"""

import os
import json
import sys
from datetime import datetime
from intuitlib.client import AuthClient
from intuitlib.enums import Scopes
from quickbooks import QuickBooks
from quickbooks.objects.customer import Customer
from quickbooks.objects.invoice import Invoice
from quickbooks.objects.detailline import SalesItemLine, SalesItemLineDetail
from quickbooks.objects.item import Item
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class QuickBooksInvoiceCreator:
    def __init__(self):
        self.client_id = os.getenv('QUICKBOOKS_CLIENT_ID')
        self.client_secret = os.getenv('QUICKBOOKS_CLIENT_SECRET')
        self.realm_id = os.getenv('QUICKBOOKS_REALM_ID')
        self.refresh_token = os.getenv('QUICKBOOKS_REFRESH_TOKEN')
        self.sandbox = os.getenv('QUICKBOOKS_SANDBOX', 'false').lower() == 'true'
        
        if not all([self.client_id, self.client_secret, self.realm_id, self.refresh_token]):
            raise ValueError("Missing required QuickBooks credentials in .env file")
        
        self.auth_client = AuthClient(
            client_id=self.client_id,
            client_secret=self.client_secret,
            environment='sandbox' if self.sandbox else 'production',
            redirect_uri='https://developer.intuit.com/v2/OAuth2Playground/RedirectUrl'
        )
        
        # Refresh access token
        self.auth_client.refresh(refresh_token=self.refresh_token)
        self.access_token = self.auth_client.access_token
        
        # Initialize QuickBooks client
        self.qb_client = QuickBooks(
            auth_client=self.auth_client,
            refresh_token=self.refresh_token,
            company_id=self.realm_id,
            minorversion=65
        )
    
    def find_or_create_customer(self, customer_data):
        """
        Find existing customer by email or create new one
        
        Args:
            customer_data (dict): Customer information
                {
                    'name': 'John Doe',
                    'email': 'john@example.com',
                    'phone': '555-1234',
                    'billing_address': {...},
                    'shipping_address': {...}
                }
        
        Returns:
            Customer: QuickBooks Customer object
        """
        # Search for existing customer by email
        customers = Customer.query(
            f"SELECT * FROM Customer WHERE PrimaryEmailAddr = '{customer_data['email']}'",
            qb=self.qb_client
        )
        
        if customers:
            print(f"✓ Found existing customer: {customers[0].DisplayName}")
            return customers[0]
        
        # Create new customer
        customer = Customer()
        customer.DisplayName = customer_data['name']
        customer.GivenName = customer_data.get('first_name', customer_data['name'].split()[0])
        customer.FamilyName = customer_data.get('last_name', ' '.join(customer_data['name'].split()[1:]))
        customer.PrimaryEmailAddr = {'Address': customer_data['email']}
        customer.PrimaryPhone = {'FreeFormNumber': customer_data.get('phone', '')}
        
        # Add billing address if provided
        if 'billing_address' in customer_data:
            billing = customer_data['billing_address']
            customer.BillAddr = {
                'Line1': billing.get('street1', ''),
                'Line2': billing.get('street2', ''),
                'City': billing.get('city', ''),
                'CountrySubDivisionCode': billing.get('state', ''),
                'PostalCode': billing.get('postal_code', ''),
                'Country': billing.get('country', 'US')
            }
        
        # Add shipping address if provided
        if 'shipping_address' in customer_data:
            shipping = customer_data['shipping_address']
            customer.ShipAddr = {
                'Line1': shipping.get('street1', ''),
                'Line2': shipping.get('street2', ''),
                'City': shipping.get('city', ''),
                'CountrySubDivisionCode': shipping.get('state', ''),
                'PostalCode': shipping.get('postal_code', ''),
                'Country': shipping.get('country', 'US')
            }
        
        customer.save(qb=self.qb_client)
        print(f"✓ Created new customer: {customer.DisplayName}")
        return customer
    
    def create_invoice(self, order_data):
        """
        Create invoice in QuickBooks from order data
        
        Args:
            order_data (dict): Order information
                {
                    'customer': {customer_data},
                    'line_items': [
                        {'sku': 'PROD-001', 'description': 'Product', 'quantity': 2, 'rate': 49.99},
                        ...
                    ],
                    'payment_terms': 'Due on receipt',
                    'shipping_method': 'Standard',
                    'notes': 'Special instructions',
                    'discount_percent': 0,
                    'shipping_cost': 10.00
                }
        
        Returns:
            dict: Invoice details
                {
                    'invoice_id': '123',
                    'invoice_number': 'INV-001',
                    'total': 123.45,
                    'pdf_url': 'https://...',
                    'customer_id': '456'
                }
        """
        try:
            # Find or create customer
            customer = self.find_or_create_customer(order_data['customer'])
            
            # Create invoice object
            invoice = Invoice()
            invoice.CustomerRef = customer.to_ref()
            
            # Add line items
            invoice.Line = []
            for item_data in order_data['line_items']:
                # Query for QuickBooks Item by SKU
                items = Item.query(
                    f"SELECT * FROM Item WHERE Sku = '{item_data['sku']}'",
                    qb=self.qb_client
                )
                
                if not items:
                    print(f"⚠ Warning: Item with SKU {item_data['sku']} not found in QuickBooks")
                    continue
                
                item = items[0]
                
                # Create sales line
                line = SalesItemLine()
                line.LineNum = len(invoice.Line) + 1
                line.Description = item_data.get('description', item.Name)
                line.Amount = item_data['quantity'] * item_data['rate']
                
                detail = SalesItemLineDetail()
                detail.ItemRef = item.to_ref()
                detail.Qty = item_data['quantity']
                detail.UnitPrice = item_data['rate']
                
                # Add tax code if specified
                if 'tax_code' in item_data:
                    detail.TaxCodeRef = {'value': item_data['tax_code']}
                
                line.SalesItemLineDetail = detail
                invoice.Line.append(line)
            
            # Add shipping as line item if specified
            if 'shipping_cost' in order_data and order_data['shipping_cost'] > 0:
                shipping_line = SalesItemLine()
                shipping_line.LineNum = len(invoice.Line) + 1
                shipping_line.Description = f"Shipping - {order_data.get('shipping_method', 'Standard')}"
                shipping_line.Amount = order_data['shipping_cost']
                
                shipping_detail = SalesItemLineDetail()
                # Note: You'll need to create a "Shipping" item in QuickBooks
                shipping_items = Item.query("SELECT * FROM Item WHERE Name = 'Shipping'", qb=self.qb_client)
                if shipping_items:
                    shipping_detail.ItemRef = shipping_items[0].to_ref()
                    shipping_detail.Qty = 1
                    shipping_detail.UnitPrice = order_data['shipping_cost']
                    shipping_line.SalesItemLineDetail = shipping_detail
                    invoice.Line.append(shipping_line)
            
            # Set payment terms
            if 'payment_terms' in order_data:
                terms_map = {
                    'Due on receipt': '1',
                    'Net 15': '2',
                    'Net 30': '3',
                    'Net 60': '4'
                }
                terms_value = terms_map.get(order_data['payment_terms'], '1')
                invoice.SalesTermRef = {'value': terms_value}
            
            # Add notes/memo
            if 'notes' in order_data:
                invoice.CustomerMemo = {'value': order_data['notes']}
            
            # Set email delivery
            invoice.BillEmail = {'Address': order_data['customer']['email']}
            invoice.EmailStatus = 'NeedToSend' if os.getenv('AUTO_SEND_INVOICE', 'false') == 'true' else 'NotSet'
            
            # Save invoice
            invoice.save(qb=self.qb_client)
            
            print(f"✓ Invoice created: {invoice.DocNumber}")
            
            # Generate PDF URL
            pdf_url = f"https://app.qbo.intuit.com/app/invoice?txnId={invoice.Id}"
            
            return {
                'success': True,
                'invoice_id': str(invoice.Id),
                'invoice_number': invoice.DocNumber,
                'total': float(invoice.TotalAmt),
                'pdf_url': pdf_url,
                'customer_id': str(customer.Id),
                'customer_name': customer.DisplayName,
                'created_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"✗ Error creating invoice: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


def main():
    """
    Main execution function
    """
    # Example order data (replace with actual form data)
    sample_order = {
        'customer': {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '555-1234',
            'billing_address': {
                'street1': '123 Main St',
                'city': 'San Francisco',
                'state': 'CA',
                'postal_code': '94102',
                'country': 'US'
            },
            'shipping_address': {
                'street1': '123 Main St',
                'city': 'San Francisco',
                'state': 'CA',
                'postal_code': '94102',
                'country': 'US'
            }
        },
        'line_items': [
            {
                'sku': 'PROD-001',
                'description': 'Premium Widget',
                'quantity': 2,
                'rate': 49.99
            },
            {
                'sku': 'PROD-002',
                'description': 'Standard Gadget',
                'quantity': 1,
                'rate': 29.99
            }
        ],
        'payment_terms': 'Net 30',
        'shipping_method': 'Standard',
        'shipping_cost': 10.00,
        'notes': 'Please handle with care'
    }
    
    # Check if data file provided
    if len(sys.argv) > 2 and sys.argv[1] == '--data':
        with open(sys.argv[2], 'r') as f:
            sample_order = json.load(f)
    
    # Create invoice
    creator = QuickBooksInvoiceCreator()
    result = creator.create_invoice(sample_order)
    
    # Print result
    print("\n" + "="*50)
    print("INVOICE CREATION RESULT")
    print("="*50)
    print(json.dumps(result, indent=2))
    
    # Save result to file
    with open('.tmp/invoice_result.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    return result


if __name__ == '__main__':
    main()
