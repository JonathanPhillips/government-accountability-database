## Description

<!-- Provide a brief description of the changes in this PR -->

## Type of Change

<!-- Check all that apply -->

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Refactoring (no functional changes)
- [ ] Performance improvement
- [ ] Test coverage improvement
- [ ] CI/CD changes

## Related Issues

<!-- Link related issues here. Use "Closes #123" to auto-close issues when PR is merged -->

Closes #
Related to #

## Changes Made

<!-- List the main changes made in this PR -->

-
-
-

## Testing

### Backend Testing

<!-- Describe backend testing performed -->

```bash
# Commands run
pytest tests/ -v
pytest tests/ --cov=app
```

**Test Results:**
- [ ] All tests pass
- [ ] New tests added for new functionality
- [ ] Test coverage maintained or improved

### Frontend Testing

<!-- Describe frontend testing performed -->

```bash
# Commands run
npm test
npm run lint
```

**Test Results:**
- [ ] All tests pass
- [ ] No linting errors
- [ ] TypeScript compilation successful

### Manual Testing

<!-- Describe manual testing performed -->

- [ ] Tested locally with Docker Compose
- [ ] Tested affected features manually
- [ ] Verified database migrations work
- [ ] Checked for console errors

## Screenshots

<!-- If applicable, add screenshots to demonstrate the changes -->

### Before


### After


## Deployment Notes

<!-- Any special deployment considerations? -->

- [ ] Requires database migration
- [ ] Requires environment variable changes
- [ ] Requires dependency updates
- [ ] Requires configuration changes
- [ ] No special deployment steps needed

**Migration commands:**
```bash
# If migrations are required
alembic upgrade head
```

**Environment variables:**
```bash
# If new env vars are needed
NEW_VAR=value
```

## Performance Impact

<!-- Describe any performance implications -->

- [ ] No performance impact
- [ ] Performance improved
- [ ] Performance may be affected (explain below)

## Security Considerations

<!-- Any security implications? -->

- [ ] No security implications
- [ ] Security improved
- [ ] Requires security review

## Documentation

- [ ] README updated
- [ ] API documentation updated (if applicable)
- [ ] Code comments added/updated
- [ ] CHANGELOG updated

## Checklist

### Code Quality

- [ ] Code follows project style guidelines
- [ ] Self-review of code performed
- [ ] Comments added for complex logic
- [ ] No unnecessary console logs or debug code
- [ ] No hardcoded values (use environment variables)

### Testing

- [ ] Existing tests pass locally
- [ ] New tests added for new features
- [ ] Edge cases considered and tested
- [ ] Error handling tested

### Documentation

- [ ] Docstrings/JSDoc added for new functions
- [ ] Type hints added (Python) / types defined (TypeScript)
- [ ] README updated if user-facing changes
- [ ] API documentation updated if endpoints changed

### Dependencies

- [ ] No new dependencies added
- [ ] OR: New dependencies justified and documented
- [ ] Dependencies scanned for vulnerabilities
- [ ] Lock files updated (requirements.txt / package-lock.json)

### Backwards Compatibility

- [ ] Changes are backwards compatible
- [ ] OR: Breaking changes documented and migration guide provided

## Additional Notes

<!-- Any additional information for reviewers -->

## Reviewer Checklist

<!-- For reviewers -->

- [ ] Code reviewed for quality and best practices
- [ ] Tests reviewed and adequate
- [ ] Documentation reviewed
- [ ] Security implications considered
- [ ] Performance implications considered
- [ ] Deployment plan reviewed

---

**By submitting this PR, I confirm that:**
- [ ] I have read the [CONTRIBUTING.md](../CONTRIBUTING.md) guide
- [ ] My code follows the project's code style
- [ ] I have performed a self-review of my code
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
