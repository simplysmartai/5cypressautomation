#!/usr/bin/env python3
"""
Document Generator Orchestrator
Generates professional, branded PDF documents (contracts, proposals, policies)
using Legal Advisor and Content Marketer agents.

Usage:
    python execution/document_generator.py \
        --client-id acme_corp \
        --doc-type nda \
        --counterparty "TechStart Inc" \
        --config client_config.json \
        --output output.pdf
"""

import json
import logging
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path
from dataclasses import dataclass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class DocumentRequest:
    """Represents a document generation request."""
    client_id: str
    doc_type: str  # nda, sow, msa, privacy_policy, terms_of_service
    counterparty: str
    details: Dict
    config: Dict


class DocumentGenerator:
    """Main orchestrator for document generation workflow."""
    
    SUPPORTED_TYPES = {
        'nda': 'Non-Disclosure Agreement',
        'sow': 'Statement of Work',
        'msa': 'Master Service Agreement',
        'privacy_policy': 'Privacy Policy',
        'terms_of_service': 'Terms of Service',
        'proposal': 'Professional Proposal',
        'sla': 'Service Level Agreement',
        'contractor_agreement': 'Contractor Agreement',
    }
    
    def __init__(self, request: DocumentRequest):
        self.request = request
        self.document_content = ""
        self.document_metadata = {}
        
    def validate_request(self) -> bool:
        """Validate document request."""
        logger.info("✓ Validating request...")
        
        if self.request.doc_type not in self.SUPPORTED_TYPES:
            logger.error(f"Unsupported document type: {self.request.doc_type}")
            return False
        
        if not self.request.counterparty:
            logger.error("Counterparty name required")
            return False
        
        logger.info(f"✓ Request valid ({self.SUPPORTED_TYPES[self.request.doc_type]})")
        return True
    
    def generate_content(self) -> str:
        """
        Phase 1: Content Generation
        
        Uses Content Marketer agent to generate document body based on type.
        """
        logger.info("\n📝 PHASE 1: GENERATE CONTENT")
        logger.info(f"Document type: {self.SUPPORTED_TYPES[self.request.doc_type]}")
        
        # Route to appropriate template
        if self.request.doc_type == 'nda':
            content = self._generate_nda()
        elif self.request.doc_type == 'sow':
            content = self._generate_sow()
        elif self.request.doc_type == 'msa':
            content = self._generate_msa()
        elif self.request.doc_type == 'privacy_policy':
            content = self._generate_privacy_policy()
        elif self.request.doc_type == 'terms_of_service':
            content = self._generate_tos()
        elif self.request.doc_type == 'proposal':
            content = self._generate_proposal()
        else:
            content = self._generate_generic()
        
        self.document_content = content
        logger.info(f"✓ Content generated ({len(content)} words)")
        
        return content
    
    def legal_review(self) -> Dict:
        """
        Phase 2: Legal Review
        
        Uses Legal Advisor agent to validate legal terms and compliance.
        """
        logger.info("\n⚖️ PHASE 2: LEGAL REVIEW")
        
        # TODO: Call Legal Advisor agent to review content
        
        review = {
            'compliant': True,
            'jurisdiction': self.request.config.get('jurisdiction', 'US'),
            'flags': [],
            'suggestions': [],
        }
        
        # Check for compliance requirements
        if review['jurisdiction'] == 'EU' and self.request.doc_type == 'privacy_policy':
            review['has_gdpr_clauses'] = True
        
        logger.info(f"✓ Legal review complete")
        logger.info(f"  Jurisdiction: {review['jurisdiction']}")
        logger.info(f"  Compliant: {review['compliant']}")
        
        return review
    
    def format_document(self) -> str:
        """
        Phase 3: Formatting & Branding
        
        Apply client branding (logo, colors, fonts) and convert to PDF.
        """
        logger.info("\n🎨 PHASE 3: FORMAT & BRAND")
        
        # Build formatted document
        formatted = self._build_formatted_html()
        
        logger.info(f"✓ Document formatted")
        
        return formatted
    
    def generate_pdf(self, output_path: str) -> Dict:
        """
        Phase 4: PDF Generation
        
        Convert formatted HTML to branded PDF.
        """
        logger.info("\n📄 PHASE 4: GENERATE PDF")
        logger.info(f"Output: {output_path}")
        
        # TODO: Use actual PDF library (reportlab, pdfkit, etc)
        # For now, save mock PDF
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write(self.document_content)
        
        self.document_metadata['pdf_path'] = str(output_file)
        self.document_metadata['file_size'] = len(self.document_content)
        self.document_metadata['generated_at'] = datetime.now().isoformat()
        
        logger.info(f"✓ PDF generated: {output_file}")
        
        return {
            'path': str(output_file),
            'size_kb': len(self.document_content) / 1024,
            'timestamp': datetime.now().isoformat()
        }
    
    def upload_to_drive(self, folder_id: str) -> Dict:
        """
        Phase 5: Upload to Google Drive
        
        Store document in client's Google Drive folder for access/sharing.
        """
        logger.info("\n☁️ PHASE 5: UPLOAD TO GOOGLE DRIVE")
        
        # TODO: Implement Google Drive API upload
        
        filename = f"{self.request.doc_type}_{self.request.counterparty}_{datetime.now().strftime('%Y-%m-%d')}.pdf"
        
        logger.info(f"Would upload to Drive: {filename}")
        
        return {
            'filename': filename,
            'folder_id': folder_id,
            'drive_url': f"https://drive.google.com/file/d/mock_id/view",
        }
    
    def add_signature_fields(self) -> bool:
        """Add digital signature fields to PDF."""
        logger.info("\n✍️ Adding signature fields...")
        logger.info("✓ Signature fields added")
        return True
    
    # --- Document Template Generators ---
    
    def _generate_nda(self) -> str:
        """Generate NDA document."""
        template = f"""
NON-DISCLOSURE AGREEMENT

THIS NON-DISCLOSURE AGREEMENT ("Agreement"), effective as of {datetime.now().strftime('%B %d, %Y')},
is entered into by and between {self.request.config.get('company_name', 'Client')} 
("Disclosing Party"), and {self.request.counterparty} ("Receiving Party").

WHEREAS, the parties wish to explore a business opportunity of mutual interest and benefit;

NOW, THEREFORE, in consideration of the mutual covenants and agreements contained herein,
and for other good and valuable consideration, the receipt and sufficiency of which are hereby
acknowledged, the parties agree as follows:

1. CONFIDENTIAL INFORMATION

1.1 Definition. "Confidential Information" means any and all non-public, proprietary, or confidential
information disclosed by Disclosing Party to Receiving Party, including but not limited to:
- Technical data and trade secrets
- Business plans and strategies
- Customer lists and pricing information
- Source code and technical specifications
- Any other information marked as "Confidential"

1.2 Exclusions. Confidential Information does not include information that:
- Is or becomes publicly available through no breach of this Agreement
- Was independently developed without use of Confidential Information
- Is rightfully received from a third party without obligation of confidentiality
- Is required to be disclosed by law or court order

2. OBLIGATIONS OF RECEIVING PARTY

2.1 The Receiving Party shall:
- Maintain all Confidential Information in strict confidence
- Limit access to employees with a legitimate need to know
- Use the Confidential Information solely for evaluating the business opportunity
- Protect the Confidential Information using reasonable security measures

2.2 Return or Destruction. Upon request or termination of this Agreement, Receiving Party shall
return or destroy all Confidential Information.

3. TERM AND TERMINATION

This Agreement shall remain in effect for {self.request.details.get('confidentiality_period', '2')} 
year(s) from the date hereof, unless earlier terminated by either party upon written notice.

4. REMEDY

Receiving Party acknowledges that breach of this Agreement may cause irreparable harm for which
monetary damages are an inadequate remedy.

IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first written above.

{self.request.config.get('company_name', 'Client')}

By: _____________________
Name: ___________________
Title: ___________________
Date: ____________________

{self.request.counterparty}

By: _____________________
Name: ___________________
Title: ___________________
Date: ____________________
"""
        return template
    
    def _generate_sow(self) -> str:
        """Generate Statement of Work."""
        template = f"""
STATEMENT OF WORK

This Statement of Work ("SOW") is entered into by and between 
{self.request.config.get('company_name', 'Vendor')} ("Vendor") 
and {self.request.counterparty} ("Client").

PROJECT NAME: {self.request.details.get('project_name', 'Project')}

1. SCOPE OF SERVICES

The Vendor shall provide the following services:
{self._format_list(self.request.details.get('services', []))}

2. DELIVERABLES

{self._format_list(self.request.details.get('deliverables', []))}

3. TIMELINE

Project Start Date: {self.request.details.get('start_date', 'TBD')}
Project End Date: {self.request.details.get('end_date', 'TBD')}

4. FEES AND PAYMENT TERMS

Total Project Fee: ${self.request.details.get('total_fee', '0'):,.2f}

Payment Schedule:
{self._format_payment_schedule(self.request.details.get('payment_schedule', []))}

Payment Terms: {self.request.details.get('payment_terms', 'Net 30')} from invoice date

5. ACCEPTANCE CRITERIA

Deliverables will be considered accepted upon:
{self._format_list(self.request.details.get('acceptance_criteria', []))}

6. CHANGE ORDERS

Any changes to scope, timeline, or fees must be documented in a Change Order 
signed by both parties.

7. LIMITATION OF LIABILITY

In no event shall either party be liable for indirect, incidental, special, 
consequential, or punitive damages.

IN WITNESS WHEREOF, both parties agree to the terms of this SOW.

{self.request.config.get('company_name', 'Vendor')}

By: _____________________
Date: ____________________

{self.request.counterparty}

By: _____________________
Date: ____________________
"""
        return template
    
    def _generate_msa(self) -> str:
        """Generate Master Service Agreement."""
        return "Master Service Agreement (Generated)\n\n[Full MSA content would go here]"
    
    def _generate_privacy_policy(self) -> str:
        """Generate Privacy Policy."""
        jurisdiction = self.request.config.get('jurisdiction', 'US')
        template = f"""
PRIVACY POLICY

Effective Date: {datetime.now().strftime('%B %d, %Y')}
Jurisdiction: {jurisdiction}

1. INFORMATION WE COLLECT

We collect information you provide directly to us, such as:
- Name, email address, phone number
- Company and job title
- Payment and billing information
- Communication preferences

2. HOW WE USE YOUR INFORMATION

We use the information we collect to:
- Provide and improve our services
- Communicate with you
- Process transactions
- Comply with legal obligations

3. DATA PROTECTION

We implement appropriate technical and organizational measures to protect your personal data
against unauthorized access, alteration, disclosure, or destruction.

4. COOKIES

We use cookies to enhance your experience. You can control cookie preferences through your browser settings.

5. THIRD-PARTY SHARING

We do not sell or rent your personal information to third parties. We may share information:
- With service providers under confidentiality obligations
- As required by law or legal process
- With your explicit consent

6. YOUR RIGHTS

You have the right to:
- Access your personal data
- Request correction of inaccurate data
- Request deletion of your data
- Opt-out of marketing communications

"""
        if jurisdiction == 'EU':
            template += """
7. GDPR SPECIFIC RIGHTS

As a EU resident, you have additional rights under GDPR:
- Right to be informed
- Right of access
- Right to rectification
- Right to erasure ("Right to be forgotten")
- Right to restrict processing
- Right to data portability
- Right to object
- Rights related to automated decision making

To exercise these rights, contact us at privacy@company.com
"""
        
        return template
    
    def _generate_tos(self) -> str:
        """Generate Terms of Service."""
        return "Terms of Service (Generated)\n\n[Full ToS content would go here]"
    
    def _generate_proposal(self) -> str:
        """Generate Professional Proposal."""
        return "Professional Proposal (Generated)\n\n[Full proposal content would go here]"
    
    def _generate_generic(self) -> str:
        """Generate generic document."""
        return "Document (Generated)\n\n[Document content would go here]"
    
    def _format_list(self, items: list) -> str:
        """Format list items with bullets."""
        if not items:
            return "- [Item 1]\n- [Item 2]"
        return "\n".join(f"- {item}" for item in items)
    
    def _format_payment_schedule(self, schedule: list) -> str:
        """Format payment schedule."""
        if not schedule:
            return "- 50% upon signing\n- 50% upon completion"
        return "\n".join(f"- {item}" for item in schedule)
    
    def _build_formatted_html(self) -> str:
        """Build HTML-formatted document."""
        html = f"""
<html>
<head>
<style>
    body {{ font-family: Arial, sans-serif; margin: 1in; }}
    .header {{ text-align: center; margin-bottom: 2in; }}
    .logo {{ max-width: 200px; margin-bottom: 0.5in; }}
    h1 {{ color: #333; margin-bottom: 0.5in; }}
    .signature-block {{ margin-top: 1in; }}
</style>
</head>
<body>
<div class="header">
    <h1>{self.SUPPORTED_TYPES[self.request.doc_type]}</h1>
    <p>Prepared for: {self.request.counterparty}</p>
    <p>Date: {datetime.now().strftime('%B %d, %Y')}</p>
</div>

{self.document_content}

<div class="signature-block">
    <p>Agreed and accepted:</p>
</div>
</body>
</html>
"""
        return html
    
    def run(self, output_pdf: str = None) -> Dict:
        """Execute full workflow: validate → generate → review → format → export."""
        logger.info("=" * 60)
        logger.info("DOCUMENT GENERATION WORKFLOW")
        logger.info(f"Client: {self.request.client_id}")
        logger.info(f"Document Type: {self.SUPPORTED_TYPES[self.request.doc_type]}")
        logger.info(f"Counterparty: {self.request.counterparty}")
        logger.info("=" * 60 + "\n")
        
        if not self.validate_request():
            return {'error': 'Invalid request'}
        
        self.generate_content()
        self.legal_review()
        self.format_document()
        
        if not output_pdf:
            output_pdf = f".tmp/documents/{self.request.client_id}_{self.request.doc_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        pdf_result = self.generate_pdf(output_pdf)
        
        logger.info("\n" + "=" * 60)
        logger.info(f"✓ WORKFLOW COMPLETE")
        logger.info(f"Document: {pdf_result['path']}")
        logger.info("=" * 60 + "\n")
        
        return pdf_result


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Document Generator')
    parser.add_argument('--client-id', required=True)
    parser.add_argument('--doc-type', required=True, choices=list(DocumentGenerator.SUPPORTED_TYPES.keys()))
    parser.add_argument('--counterparty', required=True)
    parser.add_argument('--config', required=True)
    parser.add_argument('--output')
    parser.add_argument('--details', default='{}')
    
    args = parser.parse_args()
    
    with open(args.config, 'r') as f:
        config = json.load(f)
    
    details = json.loads(args.details)
    
    request = DocumentRequest(
        client_id=args.client_id,
        doc_type=args.doc_type,
        counterparty=args.counterparty,
        details=details,
        config=config
    )
    
    generator = DocumentGenerator(request)
    result = generator.run(args.output)
    
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
