**SettleUp**

Technical Requirements Document

Version 1.0 • Django 5.x • PostgreSQL • Tailwind CSS

**1. Project Overview**

SettleUp is a Django-based shared expense tracking application for
groups of two or more members. Members can track shared expenses, record
payments into a shared pool, and view running balances. The application
uses a percentage-based contribution model where each member has a
default share that can be overridden per expense.

  --------------------- -----------------------------------------------
  **Project name**      settleup
  **Framework**         Django 5.x
  **Database**          PostgreSQL
  **Package manager**   uv
  **Frontend**          Tailwind CSS (CDN for dev, compiled for prod)
  **Python**            3.13+
  **Session store**     Django database sessions
  **Auth**              Django built-in auth with custom User model
  --------------------- -----------------------------------------------

**2. Architecture**

**2.1 Application Structure**

The project follows a multi-app Django structure. Each domain area is a
separate app with its own models, views, forms, services, and URLs.

  ------------------- ---------------------------------------------------------------------------------------------------------------
  **App**             **Responsibility**
  **users**           Custom User model extending AbstractUser. Email as unique identifier.
  **groups**          Group, GroupMember, Invitation models. Permission mixins. Group services.
  **expenses**        Category, Expense, ExpenseSplit models. Expense services and forms.
  **payments**        Payment model. Payment views and forms.
  **notifications**   Outbound notification records (email delivery deferred to task manager).
  **alerts**          In-app alerts for percentage changes, deactivations, ownership transfers.
  **audit**           AuditLog model. Logs role changes, percentage changes, deactivations, ownership transfers, expense deletions.
  **reporting**       Expense aggregation by category with date/member filters.
  **config**          Settings (base/development/production), root URLs, WSGI.
  ------------------- ---------------------------------------------------------------------------------------------------------------

**2.2 Settings Structure**

-   config/settings/base.py --- shared settings

-   config/settings/development.py --- DEBUG=True, console email, debug
    toolbar

-   config/settings/production.py --- HTTPS, whitenoise, SMTP email

-   manage.py points to config.settings.development

-   .env file for secrets (DATABASE\_URL, SECRET\_KEY, etc.)

**2.3 Service Layer Pattern**

Business logic lives in services.py files within each app, not in views
or models. Views call services; services call models. This keeps views
thin and logic testable.

-   groups/services.py --- create\_group, rebalance\_percentages,
    deactivate\_member, transfer\_ownership, accept\_invitation

-   expenses/services.py --- calculate\_balance,
    calculate\_group\_balances, create\_expense, edit\_expense,
    delete\_expense

-   notifications/services.py --- generate\_notifications

-   alerts/services.py --- alert\_percentage\_change,
    alert\_member\_deactivated, alert\_ownership\_transferred,
    mark\_alert\_read

-   audit/services.py --- log\_role\_change, log\_percentage\_change,
    log\_member\_deactivation, log\_ownership\_transfer,
    log\_expense\_deletion

**3. Domain Model**

**3.1 User**

Extends AbstractUser. Email is unique and used as login identifier.
username is set to email automatically on registration.

-   email (unique EmailField)

-   first\_name, last\_name (required on registration)

-   username (auto-set to email value)

**3.2 Group**

-   name, description

-   created\_by → User

-   is\_active --- False when archived

-   created\_at

**3.3 GroupMember**

Represents a User\'s membership in a Group. Roles: owner, admin, member.
Status: active, inactive (soft delete).

-   user → User, group → Group (unique together)

-   role: owner / admin / member

-   default\_percentage (Decimal) --- normal contribution share

-   status: active / inactive

-   joined\_at, deactivated\_at

**Role hierarchy and permissions:**

-   Owner: transfer ownership, manage admins, archive group (one per
    group)

-   Admin: manage members, deactivate members (not other admins)

-   Member: add expenses/payments, view balances

-   Inactive: read-only access to group history

**3.4 Expense**

-   group → Group, description, amount, category → Category

-   paid\_by → GroupMember (who fronted the money)

-   date, notes, created\_by → GroupMember

-   is\_deleted, deleted\_at, deleted\_by (soft delete)

**3.5 ExpenseSplit**

-   expense → Expense, group\_member → GroupMember

-   percentage (Decimal), amount (Decimal, stored for auditability)

-   Splits per expense must sum to 100%

**3.6 Payment**

-   group → Group, paid\_by → GroupMember

-   amount, date, notes

-   Payments go into a shared pool (no recipient)

**3.7 Category**

-   name (unique, global lookup table)

-   16 categories seeded via data migration

-   Admins can add/edit categories via /categories/

**3.8 Invitation**

-   group → Group, invited\_by → GroupMember

-   email, token (UUID, unique)

-   default\_percentage --- assigned to member on acceptance

-   status: pending / accepted / declined / expired

-   expires\_at (INVITATION\_EXPIRY\_DAYS setting, default 7)

**3.9 Notification**

-   Outbound balance reminder records (email delivery deferred)

-   group, recipient → GroupMember, message, balance\_snapshot

-   status: pending / sent / failed

-   triggered\_by → GroupMember (null if system-triggered)

**3.10 Alert**

-   In-app notifications for: percentage\_changed, member\_deactivated,
    ownership\_transferred

-   recipient → GroupMember, message, is\_read, read\_at

-   Unread count injected into all templates via context processor

**3.11 AuditLog**

-   group\_member (affected), acted\_by (who performed action)

-   event\_type: role\_changed, percentage\_changed,
    member\_deactivated, ownership\_transferred, expense\_deleted

-   old\_value, new\_value (strings), timestamp, notes

**4. Key Business Logic**

**4.1 Balance Calculation**

Balances are computed on the fly from ExpenseSplit and Payment records.
No stored balance field.

> balance = SUM(ExpenseSplit.amount where expense.is\_deleted=False) -
> SUM(Payment.amount)

-   Positive balance --- member owes the pool

-   Negative balance --- pool owes the member

-   Zero --- settled

**4.2 Auto-Rebalancing**

When a member is deactivated, their percentage is redistributed
proportionally across remaining active members.

-   Validate balance is zero (hard requirement before deactivation)

-   Deactivate member (status → inactive)

-   Redistribute percentage: new\_pct = (old\_pct / remaining\_total) \*
    100

-   Correct rounding drift (assign remainder to largest-share member)

-   Log percentage changes to AuditLog

-   Create Alert for each affected active member

**4.3 Manual Rebalancing**

Admins/owners can manually adjust default percentages via Members →
Rebalance Percentages. Fires audit log entries and alerts for all
affected members.

**4.4 Deactivation Rules**

-   Owner cannot be deactivated (must transfer ownership first)

-   Members cannot deactivate anyone

-   Admins can deactivate members but not other admins

-   Owner can deactivate admins

-   Balance must be zero before deactivation

**4.5 Expense Splits**

-   paid\_by is always set to the logged-in user (not a form field)

-   Splits use plain FormSet (not inline ModelFormSet) to support
    creation without a parent instance

-   On edit: existing splits are deleted and recreated

-   Split amounts are stored: amount = expense.amount \* percentage /
    100

**4.6 Invitation Flow**

-   Admin/owner creates invitation with email and default\_percentage

-   Invitation record created with UUID token and expiry timestamp

-   Invitee navigates to /groups/invitations/\<token\>/

-   On acceptance: GroupMember created with specified percentage

-   Admin must manually rebalance percentages after acceptance

**5. Permission System**

Permission enforcement uses Django class-based view mixins defined in
groups/mixins.py.

  ------------------------------- -------------------------------------------------------------------------------
  **Mixin**                       **Who can access**
  **GroupMemberRequiredMixin**    Any member of the group (active or inactive). Read-only views.
  **ActiveMemberRequiredMixin**   Active members only. Write actions (add expense, add payment).
  **AdminRequiredMixin**          Active admins and owners. Member management, notifications.
  **OwnerRequiredMixin**          Active owner only. Archive group, used as base for ownership-sensitive views.
  ------------------------------- -------------------------------------------------------------------------------

**6. URL Structure**

> / → redirect to /groups/
>
> /register/ /login/ /logout/
>
> /password-reset/ /profile/
>
> /categories/
>
> /categories/add/
>
> /categories/\<id\>/edit/
>
> /groups/
>
> /groups/create/
>
> /groups/\<id\>/ → dashboard
>
> /groups/\<id\>/edit/ /archive/ /transfer-ownership/
>
> /groups/\<id\>/members/
>
> /groups/\<id\>/members/invite/ /rebalance/
>
> /groups/\<id\>/members/\<mid\>/edit/ /deactivate/ /role/
>
> /groups/\<id\>/expenses/
>
> /groups/\<id\>/expenses/add/
>
> /groups/\<id\>/expenses/\<eid\>/ /edit/ /delete/
>
> /groups/\<id\>/payments/ /add/
>
> /groups/\<id\>/payments/\<pid\>/delete/
>
> /groups/\<id\>/notifications/ /send/
>
> /groups/\<id\>/audit/
>
> /groups/\<id\>/reports/
>
> /groups/invitations/\<token\>/
>
> /alerts/
>
> /alerts/\<id\>/read/

**7. Templates & Frontend**

**7.1 Stack**

-   Tailwind CSS via CDN (development). Production build via npm/PostCSS
    (not yet configured).

-   Fonts: Playfair Display (headings), DM Sans (body), DM Mono
    (numbers/balances)

-   Dark theme: surface \#0F1117, raised \#161B27, accent green \#4ADE80

**7.2 Layout**

-   base.html --- full sidebar layout for authenticated users, centered
    card for unauthenticated

-   Fixed left sidebar (240px) with group-contextual nav links

-   Sticky top bar with page title and header action buttons

-   Django messages rendered as styled alert banners below the top bar

-   Unread alert count badge in sidebar via context processor

**7.3 Template Directory**

-   templates/base.html

-   templates/users/ --- login, register, profile, password reset flow

-   templates/groups/ --- group list/form/detail, member
    list/form/invite/rebalance, transfer ownership, invitation accept

-   templates/expenses/ --- expense list/detail/form, category list/form

-   templates/payments/ --- payment list/form

-   templates/notifications/ --- notification list

-   templates/alerts/ --- alert list

-   templates/audit/ --- audit log

-   templates/reporting/ --- report

-   templates/403.html, 404.html, 500.html

**8. Dependencies**

**8.1 Python (via uv / pyproject.toml)**

-   django --- web framework

-   psycopg2-binary --- PostgreSQL adapter

-   django-environ --- .env file support

-   django-crispy-forms + crispy-bootstrap5 --- form rendering helpers

-   django-extensions --- shell\_plus, show\_urls, etc.

-   whitenoise --- static file serving in production

-   django-debug-toolbar --- development only

**8.2 Frontend (CDN, no build step yet)**

-   Tailwind CSS --- https://cdn.tailwindcss.com

-   Google Fonts --- DM Sans, DM Mono, Playfair Display

**9. Current Implementation Status**

**9.1 Fully Implemented & Verified**

-   User registration, login, logout, password reset, profile edit

-   Group create, edit, archive

-   GroupMember roles, permissions, deactivation with zero-balance check

-   Invitation flow (create, token link, accept)

-   Expense create, edit, soft delete with custom percentage splits

-   Payment create, delete

-   Balance calculation (computed on the fly)

-   Auto-rebalance on member deactivation

-   Manual rebalance with audit log and alerts

-   Ownership transfer

-   In-app alerts (percentage change, deactivation, ownership transfer)

-   Audit log (role change, percentage change, deactivation, ownership
    transfer, expense deletion)

-   Notification queue (create pending records, delivery deferred)

-   Category management (list, add, edit)

-   Reporting (spend by category with filters)

-   403, 404, 500 error pages

**9.2 Deferred / Not Yet Started**

-   Task manager integration (Celery + Redis) for email delivery

-   Notification model redesign (balance-only vs. event-driven)

-   Tailwind production build (npm + PostCSS)

-   REST API

-   Automated test suite

-   Deployment configuration (Gunicorn, Nginx, Docker)

-   UI rough edges pass

**10. Known Issues & Design Decisions**

-   Model-level clean() methods removed from Expense and Payment to
    avoid RelatedObjectDoesNotExist during form validation. Validation
    moved to service layer.

-   TransferOwnershipView uses AdminRequiredMixin (not
    OwnerRequiredMixin) with a manual owner check inside the view, to
    avoid 403 after the transfer demotes the acting user.

-   Notification deduplication intentionally not implemented. Discussed;
    deferred to notification model redesign.

-   Categories are global (not per-group). All groups share the same
    category list.

-   paid\_by on Expense is always set to the logged-in user. There is no
    UI field for this.

-   Tailwind CDN is used for development. A production npm build step is
    not yet configured.

-   SESSION\_EXPIRE\_AT\_BROWSER\_CLOSE should be set to True in
    production settings.
