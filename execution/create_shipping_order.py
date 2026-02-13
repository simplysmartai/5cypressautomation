"""
Shipping Order Creation Script

Multi-provider shipping integration supporting:
- ShipStation
- Shopify Fulfillment  
- ShipBob
- EasyShip

Usage:
    python create_shipping_order.py --data order_data.json

Requirements:
    pip install requests python-dotenv
"""

import os
import json
import sys
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ShippingOrderCreator:
    def __init__(self):
        self.provider = os.getenv('SHIPPING_PROVIDER', 'shipstation').lower()
        self.api_key = os.getenv('SHIPPING_API_KEY')
        self.api_secret = os.getenv('SHIPPING_API_SECRET')
        self.store_id = os.getenv('SHIPPING_STORE_ID')
        
        if not self.api_key:
            raise ValueError("Missing SHIPPING_API_KEY in .env file")
        
        # Provider-specific setup
        if self.provider == 'shipstation':
            self.base_url = 'https://ssapi.shipstation.com'
        elif self.provider == 'shopify':
            self.base_url = f"https://{os.getenv('SHOPIFY_STORE_NAME')}.myshopify.com/admin/api/2024-01"
        elif self.provider == 'shipbob':
            self.base_url = 'https://api.shipbob.com/1.0'
        elif self.provider == 'easyship':
            self.base_url = 'https://api.easyship.com/2023-01'
        else:
            raise ValueError(f"Unsupported shipping provider: {self.provider}")
    
    def validate_address(self, address_data):
        """
        Validate shipping address
        
        Returns:
            tuple: (is_valid, validated_address or error_message)
        """
        required_fields = ['street1', 'city', 'state', 'postal_code', 'country']
        missing = [f for f in required_fields if not address_data.get(f)]
        
        if missing:
            return False, f"Missing required address fields: {', '.join(missing)}"
        
        # Basic validation
        if len(address_data['postal_code']) < 5:
            return False, "Invalid postal code"
        
        if len(address_data['state']) != 2:
            return False, "State must be 2-letter code (e.g., CA, NY)"
        
        return True, address_data
    
    def map_shipping_method(self, method):
        """
        Map form shipping method to carrier service code
        """
        mappings = {
            'standard': {
                'carrier': 'usps',
                'service': 'usps_first_class_mail'
            },
            'express': {
                'carrier': 'fedex',
                'service': 'fedex_2day'
            },
            'overnight': {
                'carrier': 'fedex',
                'service': 'fedex_priority_overnight'
            }
        }
        
        return mappings.get(method.lower(), mappings['standard'])
    
    def create_shipstation_order(self, order_data):
        """Create order in ShipStation"""
        url = f"{self.base_url}/orders/createorder"
        
        # Map to ShipStation format
        payload = {
            "orderNumber": order_data['order_number'],
            "orderDate": order_data['order_date'],
            "orderStatus": "awaiting_shipment",
            "customerUsername": order_data['customer']['email'],
            "customerEmail": order_data['customer']['email'],
            "billTo": {
                "name": order_data['customer']['name'],
                "street1": order_data['customer']['address']['street1'],
                "street2": order_data['customer']['address'].get('street2', ''),
                "city": order_data['customer']['address']['city'],
                "state": order_data['customer']['address']['state'],
                "postalCode": order_data['customer']['address']['postal_code'],
                "country": order_data['customer']['address']['country'],
                "phone": order_data['customer'].get('phone', '')
            },
            "shipTo": {
                "name": order_data['customer']['name'],
                "street1": order_data['customer']['address']['street1'],
                "street2": order_data['customer']['address'].get('street2', ''),
                "city": order_data['customer']['address']['city'],
                "state": order_data['customer']['address']['state'],
                "postalCode": order_data['customer']['address']['postal_code'],
                "country": order_data['customer']['address']['country'],
                "phone": order_data['customer'].get('phone', '')
            },
            "items": []
        }
        
        # Add line items
        for item in order_data['items']:
            payload['items'].append({
                "sku": item['sku'],
                "name": item['name'],
                "quantity": item['quantity'],
                "unitPrice": item.get('unit_price', 0),
                "weight": item.get('weight', {'value': 0, 'units': 'pounds'})
            })
        
        # Set carrier and service
        shipping_service = self.map_shipping_method(order_data.get('shipping_method', 'standard'))
        payload["carrierCode"] = shipping_service['carrier']
        payload["serviceCode"] = shipping_service['service']
        
        # Make API request
        response = requests.post(
            url,
            json=payload,
            auth=(self.api_key, self.api_secret),
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                'success': True,
                'order_id': result['orderId'],
                'order_number': result['orderNumber'],
                'order_key': result['orderKey']
            }
        else:
            return {
                'success': False,
                'error': f"ShipStation API error: {response.text}"
            }
    
    def create_shopify_fulfillment(self, order_data):
        """Create fulfillment order in Shopify"""
        # Note: Assumes order already exists in Shopify
        # This would typically be called after Shopify order creation
        
        url = f"{self.base_url}/fulfillment_orders.json"
        
        payload = {
            "fulfillment_order": {
                "order_id": order_data['shopify_order_id'],  # Must be provided
                "line_items": [
                    {
                        "id": item['shopify_line_item_id'],
                        "quantity": item['quantity']
                    }
                    for item in order_data['items']
                ]
            }
        }
        
        response = requests.post(
            url,
            json=payload,
            headers={
                'Content-Type': 'application/json',
                'X-Shopify-Access-Token': self.api_key
            }
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            return {
                'success': True,
                'fulfillment_order_id': result['fulfillment_order']['id'],
                'status': result['fulfillment_order']['status']
            }
        else:
            return {
                'success': False,
                'error': f"Shopify API error: {response.text}"
            }
    
    def create_order(self, order_data):
        """
        Create shipping order using configured provider
        
        Args:
            order_data (dict): Order information
                {
                    'order_number': 'ORD-12345',
                    'order_date': '2024-02-03T10:00:00',
                    'customer': {
                        'name': 'John Doe',
                        'email': 'john@example.com',
                        'phone': '555-1234',
                        'address': {
                            'street1': '123 Main St',
                            'street2': 'Apt 4',
                            'city': 'San Francisco',
                            'state': 'CA',
                            'postal_code': '94102',
                            'country': 'US'
                        }
                    },
                    'items': [
                        {
                            'sku': 'PROD-001',
                            'name': 'Product Name',
                            'quantity': 2,
                            'weight': {'value': 1.5, 'units': 'pounds'}
                        }
                    ],
                    'shipping_method': 'standard'
                }
        
        Returns:
            dict: Shipping order details
        """
        try:
            # Validate address
            is_valid, result = self.validate_address(order_data['customer']['address'])
            if not is_valid:
                return {
                    'success': False,
                    'error': f"Address validation failed: {result}"
                }
            
            print(f"✓ Address validated")
            
            # Create order with appropriate provider
            if self.provider == 'shipstation':
                result = self.create_shipstation_order(order_data)
            elif self.provider == 'shopify':
                result = self.create_shopify_fulfillment(order_data)
            elif self.provider == 'shipbob':
                result = {'success': False, 'error': 'ShipBob integration not yet implemented'}
            elif self.provider == 'easyship':
                result = {'success': False, 'error': 'EasyShip integration not yet implemented'}
            else:
                result = {'success': False, 'error': f'Unknown provider: {self.provider}'}
            
            if result['success']:
                print(f"✓ Shipping order created: {result.get('order_number', result.get('order_id'))}")
                result['provider'] = self.provider
                result['created_at'] = datetime.now().isoformat()
            
            return result
            
        except Exception as e:
            print(f"✗ Error creating shipping order: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


def main():
    """
    Main execution function
    """
    # Example order data
    sample_order = {
        'order_number': f'ORD-{datetime.now().strftime("%Y%m%d%H%M%S")}',
        'order_date': datetime.now().isoformat(),
        'customer': {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '555-1234',
            'address': {
                'street1': '123 Main St',
                'street2': 'Apt 4',
                'city': 'San Francisco',
                'state': 'CA',
                'postal_code': '94102',
                'country': 'US'
            }
        },
        'items': [
            {
                'sku': 'PROD-001',
                'name': 'Premium Widget',
                'quantity': 2,
                'unit_price': 49.99,
                'weight': {'value': 1.5, 'units': 'pounds'},
                'dimensions': {'length': 10, 'width': 8, 'height': 6, 'units': 'inches'}
            },
            {
                'sku': 'PROD-002',
                'name': 'Standard Gadget',
                'quantity': 1,
                'unit_price': 29.99,
                'weight': {'value': 0.5, 'units': 'pounds'},
                'dimensions': {'length': 6, 'width': 4, 'height': 2, 'units': 'inches'}
            }
        ],
        'shipping_method': 'standard',
        'insurance': False,
        'signature_required': False
    }
    
    # Check if data file provided
    if len(sys.argv) > 2 and sys.argv[1] == '--data':
        with open(sys.argv[2], 'r') as f:
            sample_order = json.load(f)
    
    # Create shipping order
    creator = ShippingOrderCreator()
    result = creator.create_order(sample_order)
    
    # Print result
    print("\n" + "="*50)
    print("SHIPPING ORDER CREATION RESULT")
    print("="*50)
    print(json.dumps(result, indent=2))
    
    # Save result
    os.makedirs('.tmp', exist_ok=True)
    with open('.tmp/shipping_result.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    return result


if __name__ == '__main__':
    main()
