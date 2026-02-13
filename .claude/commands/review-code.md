---
description: Review code for SMB automation best practices
---

Review the code with focus on: $ARGUMENTS

## Review Checklist

### Security
- [ ] No hardcoded secrets (check for API keys, passwords)
- [ ] Input validation on all external data
- [ ] Webhook signatures verified
- [ ] SQL injection prevention (parameterized queries)
- [ ] Proper error messages (don't leak internals)

### Reliability
- [ ] Retry logic for external API calls
- [ ] Timeout handling
- [ ] Idempotent operations where needed
- [ ] Graceful error handling
- [ ] Structured logging with context

### Architecture (3-Layer)
- [ ] Business logic in `execution/` scripts (not inline)
- [ ] Directives updated when workflows change
- [ ] Clear separation of concerns
- [ ] Follows existing patterns in codebase

### Code Quality
- [ ] Type hints on all functions
- [ ] Pydantic models for data validation
- [ ] Async/await for I/O operations
- [ ] Clear variable names
- [ ] No duplicate code

### Testing
- [ ] Unit tests for core logic
- [ ] Mock external APIs in tests
- [ ] Edge cases covered
- [ ] Dry-run capability for critical operations

## SMB-Specific Checks

- [ ] QuickBooks API: Sandbox tested before production
- [ ] Payments: PCI compliance patterns followed
- [ ] Customer data: Properly secured
- [ ] Rate limits: Respected on external APIs

## Output Format

Provide findings as:

### Critical Issues
- Issue description and location
- Why it matters
- Suggested fix

### Improvements
- Current approach
- Better alternative
- Example code

### Positive Notes
- Good patterns worth keeping
