---
name: data-validation
description: Pydantic and Zod validation patterns for SMB automation. Use when validating form inputs, API requests, or external data. Prevents bad data from reaching QuickBooks or payment systems.
---

# Data Validation for SMB Automation

Robust validation patterns to catch errors before they reach critical systems.

## When to Use This Skill

- Validating sales form submissions
- Checking API request payloads
- Sanitizing data before QBO/ShipStation sync
- Preventing duplicate submissions
- Rate limiting contact forms

## Why Validation Matters

From your `CLAUDE.md`:
> If you do everything yourself, errors compound. 90% accuracy per step = 59% success over 5 steps.

Validation is the first line of defense. Bad data caught early saves debugging later.

## Pydantic Patterns (Python)

### 1. Form Submission Validation
```python
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime

class SalesFormSubmission(BaseModel):
    customer_name: str = Field(min_length=2, max_length=100)
    customer_email: EmailStr
    customer_phone: Optional[str] = None
    product_id: str
    quantity: int = Field(gt=0, le=1000)
    shipping_address: str = Field(min_length=10)

    @field_validator('customer_phone')
    @classmethod
    def validate_phone(cls, v):
        if v is None:
            return v
        # Strip non-digits
        digits = ''.join(c for c in v if c.isdigit())
        if len(digits) < 10:
            raise ValueError('Phone must have at least 10 digits')
        return digits

    @field_validator('product_id')
    @classmethod
    def validate_product_id(cls, v):
        if not v.startswith('SKU-'):
            raise ValueError('Product ID must start with SKU-')
        return v.upper()
```

### 2. QuickBooks Invoice Validation
```python
class QBOLineItem(BaseModel):
    description: str = Field(min_length=1)
    quantity: float = Field(gt=0)
    unit_price: float = Field(ge=0)
    item_ref: Optional[str] = None  # QBO Item ID

    @property
    def amount(self) -> float:
        return round(self.quantity * self.unit_price, 2)

class QBOInvoice(BaseModel):
    customer_ref: str = Field(description="QBO Customer ID")
    line_items: list[QBOLineItem] = Field(min_length=1)
    due_date: datetime
    memo: Optional[str] = Field(max_length=4000, default=None)

    @field_validator('due_date')
    @classmethod
    def due_date_not_past(cls, v):
        if v.date() < datetime.now().date():
            raise ValueError('Due date cannot be in the past')
        return v

    @property
    def total(self) -> float:
        return sum(item.amount for item in self.line_items)
```

### 3. Webhook Payload Validation
```python
from enum import Enum

class StripeEventType(str, Enum):
    PAYMENT_SUCCEEDED = "payment_intent.succeeded"
    PAYMENT_FAILED = "payment_intent.payment_failed"
    INVOICE_PAID = "invoice.paid"
    SUBSCRIPTION_DELETED = "customer.subscription.deleted"

class StripeWebhookPayload(BaseModel):
    id: str = Field(pattern=r'^evt_[a-zA-Z0-9]+$')
    type: StripeEventType
    data: dict
    created: int

    @property
    def event_object(self):
        return self.data.get("object", {})
```

### 4. Duplicate Detection
```python
from pydantic import BaseModel
import hashlib
from datetime import datetime, timedelta

class SubmissionTracker:
    def __init__(self, cache):
        self.cache = cache
        self.ttl = timedelta(hours=24)

    def get_fingerprint(self, submission: BaseModel) -> str:
        """Create unique fingerprint for submission."""
        # Use stable fields that identify the same request
        data = f"{submission.customer_email}:{submission.product_id}:{submission.quantity}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    async def is_duplicate(self, submission: BaseModel) -> bool:
        fingerprint = self.get_fingerprint(submission)

        if await self.cache.get(f"submission:{fingerprint}"):
            return True

        await self.cache.set(
            f"submission:{fingerprint}",
            datetime.utcnow().isoformat(),
            ex=int(self.ttl.total_seconds())
        )
        return False
```

## Zod Patterns (TypeScript/Node.js)

### 1. Form Validation
```typescript
import { z } from 'zod';

const SalesFormSchema = z.object({
  customerName: z.string().min(2).max(100),
  customerEmail: z.string().email(),
  customerPhone: z.string()
    .transform(v => v.replace(/\D/g, ''))
    .refine(v => v.length >= 10, 'Phone must have 10+ digits')
    .optional(),
  productId: z.string()
    .refine(v => v.startsWith('SKU-'), 'Must start with SKU-')
    .transform(v => v.toUpperCase()),
  quantity: z.number().int().positive().max(1000),
  shippingAddress: z.string().min(10)
});

type SalesForm = z.infer<typeof SalesFormSchema>;

// Usage
function validateForm(data: unknown): SalesForm {
  return SalesFormSchema.parse(data);
}
```

### 2. API Response Validation
```typescript
const QBOInvoiceResponse = z.object({
  Id: z.string(),
  DocNumber: z.string(),
  TotalAmt: z.number(),
  CustomerRef: z.object({
    value: z.string(),
    name: z.string().optional()
  }),
  Line: z.array(z.object({
    Amount: z.number(),
    Description: z.string().optional()
  }))
});

async function createInvoice(data: InvoiceRequest) {
  const response = await qboClient.post('/invoice', data);

  // Validate response matches expected shape
  return QBOInvoiceResponse.parse(response.data);
}
```

## Spam Prevention (from directives/prevent_contact_form_spam.md)

```python
from pydantic import BaseModel, field_validator
import re

class ContactFormSubmission(BaseModel):
    name: str
    email: str
    message: str
    honeypot: str = ""  # Should be empty

    @field_validator('honeypot')
    @classmethod
    def honeypot_empty(cls, v):
        if v:
            raise ValueError('Bot detected')
        return v

    @field_validator('message')
    @classmethod
    def check_spam_patterns(cls, v):
        spam_patterns = [
            r'buy now',
            r'click here',
            r'act now',
            r'limited time',
            r'\b(viagra|cialis)\b',
        ]
        for pattern in spam_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError('Message flagged as spam')
        return v

    @field_validator('email')
    @classmethod
    def check_disposable_email(cls, v):
        disposable_domains = ['tempmail.com', '10minutemail.com', 'guerrillamail.com']
        domain = v.split('@')[1].lower()
        if domain in disposable_domains:
            raise ValueError('Disposable email not allowed')
        return v
```

## Error Handling Pattern

```python
from pydantic import ValidationError
from fastapi import HTTPException

async def process_form(data: dict):
    try:
        validated = SalesFormSubmission(**data)
    except ValidationError as e:
        # Return user-friendly errors
        errors = []
        for error in e.errors():
            field = '.'.join(str(x) for x in error['loc'])
            errors.append(f"{field}: {error['msg']}")

        raise HTTPException(
            status_code=422,
            detail={"message": "Validation failed", "errors": errors}
        )

    return validated
```

## Validation Checklist

- [ ] All external inputs validated with Pydantic/Zod
- [ ] Email addresses use EmailStr/z.string().email()
- [ ] Numbers have min/max bounds
- [ ] Strings have length limits
- [ ] Dates are checked for valid ranges
- [ ] Duplicate submissions detected
- [ ] Spam patterns blocked
- [ ] Error messages don't leak internals
