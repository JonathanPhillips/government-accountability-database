# Contributing to GADB

Thank you for your interest in contributing to the Government Accountability Database (GADB)! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Workflow](#development-workflow)
4. [Coding Standards](#coding-standards)
5. [Testing Guidelines](#testing-guidelines)
6. [Commit Message Guidelines](#commit-message-guidelines)
7. [Pull Request Process](#pull-request-process)
8. [Documentation](#documentation)
9. [Community](#community)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of background or identity.

### Expected Behavior

- Be respectful and constructive in all interactions
- Focus on what is best for the project and community
- Show empathy towards other community members
- Accept constructive criticism gracefully
- Credit others for their contributions

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Trolling or inflammatory remarks
- Publishing others' private information
- Unethical or unprofessional conduct

## Getting Started

### Prerequisites

- Git
- Python 3.11+
- Node.js 20+
- Docker & Docker Compose (recommended)
- Basic knowledge of FastAPI and React

### Setting Up Development Environment

1. **Fork the repository**
   ```bash
   # Click "Fork" on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/govt_accountability.git
   cd govt_accountability
   ```

2. **Add upstream remote**
   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/govt_accountability.git
   ```

3. **Start development environment**
   ```bash
   # Option 1: Docker Compose (recommended)
   docker-compose up -d

   # Option 2: Local development
   # Backend
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload

   # Frontend (in a new terminal)
   cd frontend
   npm install
   npm run dev
   ```

4. **Verify setup**
   ```bash
   # Check backend
   curl http://localhost:8000/health

   # Check frontend
   open http://localhost:5173
   ```

## Development Workflow

### 1. Create a Feature Branch

```bash
# Update your local main branch
git checkout main
git pull upstream main

# Create a feature branch
git checkout -b feature/amazing-feature
# OR
git checkout -b fix/bug-description
```

### Branch Naming Conventions

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions or fixes
- `chore/` - Maintenance tasks

### 2. Make Your Changes

- Write clean, readable code
- Follow project coding standards
- Add/update tests for your changes
- Update documentation as needed
- Keep commits focused and atomic

### 3. Test Your Changes

```bash
# Backend tests
cd backend
pytest tests/ -v
pytest tests/ --cov=app

# Frontend tests
cd frontend
npm test
npm run lint
npx tsc --noEmit

# E2E tests (if applicable)
npm run test:e2e
```

### 4. Commit Your Changes

Follow the [commit message guidelines](#commit-message-guidelines) below.

```bash
git add .
git commit -m "feat(incidents): add advanced filtering"
```

### 5. Push to Your Fork

```bash
git push origin feature/amazing-feature
```

### 6. Create a Pull Request

- Go to your fork on GitHub
- Click "New Pull Request"
- Fill out the PR template completely
- Link related issues
- Request reviews from maintainers

## Coding Standards

### Python (Backend)

**Style Guide**: Follow [PEP 8](https://pep8.org/)

```python
# Good
def calculate_incident_severity(
    incident: Incident,
    factors: Dict[str, float]
) -> SeverityEnum:
    """
    Calculate incident severity based on multiple factors.

    Args:
        incident: The incident to evaluate
        factors: Dictionary of severity factors

    Returns:
        Calculated severity level
    """
    pass

# Bad
def calc_sev(i, f):
    pass
```

**Best Practices**:
- Use type hints for all function parameters and return values
- Write docstrings for all public functions and classes
- Keep functions small and focused (< 50 lines)
- Use descriptive variable names
- Avoid nested conditionals (max 3 levels)

**Linting**:
```bash
cd backend
pylint app/
black app/ --check
isort app/ --check-only
mypy app/
```

### TypeScript/React (Frontend)

**Style Guide**: Follow [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)

```typescript
// Good
interface IncidentCardProps {
  incident: Incident;
  onEdit: (id: string) => void;
  className?: string;
}

export const IncidentCard: React.FC<IncidentCardProps> = ({
  incident,
  onEdit,
  className
}) => {
  return (
    <div className={className}>
      {/* ... */}
    </div>
  );
};

// Bad
export const Card = (props: any) => {
  return <div>{props.i.title}</div>;
};
```

**Best Practices**:
- Use functional components with hooks
- Use TypeScript interfaces for props
- Keep components small (< 200 lines)
- Extract reusable logic into custom hooks
- Use meaningful component and variable names
- Avoid prop drilling (use context when needed)

**Linting**:
```bash
cd frontend
npm run lint
npx tsc --noEmit
```

### Database Migrations

```bash
# Create a new migration
cd backend
alembic revision --autogenerate -m "Add incident source table"

# Review the generated migration
# Edit if necessary
# Test the migration
alembic upgrade head
alembic downgrade -1
alembic upgrade head
```

## Testing Guidelines

### Backend Testing

**Unit Tests**:
```python
def test_create_incident(db_session):
    """Test incident creation."""
    incident = Incident(
        title="Test Incident",
        severity=SeverityEnum.HIGH,
        # ...
    )
    db_session.add(incident)
    db_session.commit()

    assert incident.id is not None
    assert incident.severity == SeverityEnum.HIGH
```

**Integration Tests**:
```python
def test_create_incident_endpoint(client, admin_token):
    """Test POST /api/incidents endpoint."""
    response = client.post(
        "/api/incidents",
        json={"title": "Test", "severity": "high"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 201
    assert response.json()["title"] == "Test"
```

**Test Coverage Requirements**:
- New code: Minimum 80% coverage
- Critical paths: 100% coverage
- Edge cases must be tested

### Frontend Testing

**Component Tests**:
```typescript
describe('IncidentCard', () => {
  it('renders incident title', () => {
    const incident = mockIncident();
    render(<IncidentCard incident={incident} />);

    expect(screen.getByText(incident.title)).toBeInTheDocument();
  });

  it('calls onEdit when edit button clicked', async () => {
    const onEdit = vi.fn();
    const incident = mockIncident();

    render(<IncidentCard incident={incident} onEdit={onEdit} />);

    await userEvent.click(screen.getByRole('button', { name: /edit/i }));

    expect(onEdit).toHaveBeenCalledWith(incident.id);
  });
});
```

**E2E Tests**:
```typescript
test('user can create new incident', async ({ page }) => {
  await page.goto('/incidents/new');

  await page.fill('input[name="title"]', 'New Incident');
  await page.selectOption('select[name="severity"]', 'high');
  await page.click('button[type="submit"]');

  await expect(page).toHaveURL(/\/incidents\/\w+/);
  await expect(page.locator('h1')).toContainText('New Incident');
});
```

## Commit Message Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Scopes

- `incidents`: Incident-related changes
- `auth`: Authentication/authorization
- `analytics`: Analytics features
- `api`: API changes
- `ui`: UI/UX changes
- `db`: Database changes
- `ci`: CI/CD changes

### Examples

```bash
feat(incidents): add advanced filtering by date range

Implement date range filtering for incidents list with
date picker component and query parameter support.

Closes #123

---

fix(auth): resolve token refresh race condition

Fix issue where multiple simultaneous requests could
cause token refresh to fail.

Fixes #456

---

docs(api): update analytics endpoints documentation

Add examples and improve descriptions for all
analytics API endpoints.
```

### Commit Message Rules

- Use present tense ("add feature" not "added feature")
- Use imperative mood ("move cursor to..." not "moves cursor to...")
- Limit first line to 72 characters
- Reference issues and PRs when applicable
- Explain *what* and *why*, not *how*

## Pull Request Process

### Before Submitting

- [ ] All tests pass locally
- [ ] Code follows project style guidelines
- [ ] New code has tests (80%+ coverage)
- [ ] Documentation is updated
- [ ] Commit messages follow guidelines
- [ ] Branch is up to date with main

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe testing performed

## Screenshots (if applicable)
Add screenshots for UI changes

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
- [ ] Follows code style

## Related Issues
Closes #123
Related to #456
```

### Review Process

1. **Automated Checks**: CI must pass
2. **Code Review**: At least one maintainer approval required
3. **Testing**: Reviewers may test changes locally
4. **Discussion**: Address all feedback and comments
5. **Approval**: Maintainer approves and merges

### After Merge

- Delete your feature branch
- Pull latest main
- Close related issues if not auto-closed

## Documentation

### Code Documentation

**Python**:
```python
def process_incident(incident: Incident, options: ProcessOptions) -> ProcessResult:
    """
    Process an incident with given options.

    This function handles incident processing including validation,
    enrichment, and storage.

    Args:
        incident: The incident to process
        options: Processing options including validation level

    Returns:
        ProcessResult containing status and any errors

    Raises:
        ValidationError: If incident data is invalid
        DatabaseError: If storage fails

    Examples:
        >>> result = process_incident(incident, ProcessOptions(strict=True))
        >>> assert result.success
    """
    pass
```

**TypeScript**:
```typescript
/**
 * Hook for managing incident data
 *
 * @param incidentId - The ID of the incident to manage
 * @returns Object containing incident data and actions
 *
 * @example
 * ```tsx
 * const { incident, loading, updateIncident } = useIncident('123');
 * ```
 */
export function useIncident(incidentId: string) {
  // ...
}
```

### README Updates

Update README.md when:
- Adding new features
- Changing setup instructions
- Modifying deployment process
- Adding new dependencies

### API Documentation

Update OpenAPI/Swagger docs for:
- New endpoints
- Changed request/response formats
- New query parameters
- Authentication changes

## Community

### Getting Help

- **Documentation**: Check README.md and DEPLOYMENT.md first
- **Issues**: Search existing issues before creating new ones
- **Discussions**: Use GitHub Discussions for questions
- **Discord**: Join our community server (if available)

### Reporting Bugs

Use the bug report template and include:
- Clear description
- Steps to reproduce
- Expected vs actual behavior
- Environment details
- Screenshots/logs if applicable

### Suggesting Features

Use the feature request template and include:
- Clear use case
- Proposed solution
- Alternatives considered
- Additional context

### Security Issues

**DO NOT** open public issues for security vulnerabilities.

Email: security@yourdomain.com

Include:
- Description of vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project README

Thank you for contributing to GADB! 🙏

---

**Questions?** Open a [GitHub Discussion](https://github.com/JonathanPhillips/government-accountability-database/discussions)
