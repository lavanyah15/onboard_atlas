# <Onboard Atlas>

> Fill this top section from your Examate project card on Day 1. Replace every line in angle brackets.

## Problem

HR consultancies manage HR operations for multiple startups, each with different leave, expense, onboarding, and performance management policies. HR staff often waste time searching lengthy handbooks and may accidentally provide one company's policy to another company's employee. This can lead to incorrect decisions, confusion, and potential confidentiality breaches. Onboard Atlas solves this problem by providing AI-powered answers from the correct company's handbook while enforcing tenant isolation and role-based access control. It also helps employees submit HR requests and routes exceptional requests for approval.

## Who it is for

-HR operations leads at people-operations consultancies in Chennai that manage HR services for multiple startups.

-Employees, managers, and HR administrators at client companies who need quick, reliable, and secure access to company-specific HR policies.

## Signature feature

A tenant-isolated RAG-based HR assistant that provides source-cited policy answers and handles leave or expense requests with role-based permissions and approval workflows.

## Hardest problem (my interview story)

The hardest problem is preventing cross-tenant data leaks while searching thousands of handbook pages. The system must ensure that employees can retrieve only their own company's policies and that manager-only information remains restricted. I address this by attaching a tenant ID and role metadata to every document chunk and enforcing PostgreSQL Row-Level Security before vector search. I will evaluate the system using 100 adversarial prompts, targeting zero cross-tenant leaks, and a separate 150-question evaluation set, targeting at least 85% answer accuracy.

## Dataset

| Source | Link | Documents | Pages | Licence / terms |
|---|---|---|---|---|
| GitLab Handbook | https://handbook.gitlab.com/handbook/ | To be measured | To be counted | Verify applicable repository and content licence; preserve required notices |
| PostHog Handbook | https://posthog.com/handbook | To be measured | To be counted | Verify applicable repository and content licence; preserve required notices |
| Synthetic Demo Policies | Created for Onboard Atlas | To be measured | To be counted | Original fictional content created for demonstration |

**Dataset target:** At least 3,000 distinct handbook pages across the two real-company tenants, GitLab and PostHog. Synthetic demo policies are additional and do not count toward this minimum.

## 10 real questions
See [docs/QUESTIONS.md](docs/QUESTIONS.md).

Example questions:

How many days of parental leave do I get, and do I need manager sign-off?

What is the expense limit for a client dinner?

As a manager, what is the process to put someone on a performance plan?

What is the procedure for requesting annual leave?

Which documents are required for expense reimbursement?

How do I onboard a new employee?

What is the process for reporting a workplace concern?

Who approves an expense reimbursement request?

What should I do if my leave request is rejected?

What is the process for updating my employee information?

Answers must be based on the selected tenant's authorized handbook content. If the relevant policy cannot be found, the assistant should say so instead of inventing a rule.

## Run it
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env                                 # Windows: copy .env.example .env
uvicorn app.main:app --reload
curl localhost:8000/health
```

## Live link
<Added in Week 2>
