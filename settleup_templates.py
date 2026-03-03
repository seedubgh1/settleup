# =============================================================================
# ./templates/base.html
# =============================================================================
<!DOCTYPE html>
<html lang="en" class="h-full">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{% block title %}SettleUp{% endblock %}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      theme: {
        extend: {
          fontFamily: {
            sans: ['DM Sans', 'sans-serif'],
            display: ['Playfair Display', 'serif'],
            mono: ['DM Mono', 'monospace'],
          },
          colors: {
            surface: {
              DEFAULT: '#0f1117',
              raised: '#161b27',
              border: '#1e2535',
            },
            accent: {
              DEFAULT: '#4ade80',
              muted: '#166534',
              dim: '#14532d',
            },
            ink: {
              DEFAULT: '#f1f5f9',
              muted: '#94a3b8',
              dim: '#475569',
            },
          },
        },
      },
    }
  </script>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&family=DM+Mono:wght@400;500&family=Playfair+Display:wght@700&display=swap" rel="stylesheet" />
  <style>
    body { background-color: #0f1117; color: #f1f5f9; }
    .sidebar-link { transition: all 0.15s ease; }
    .sidebar-link:hover { background-color: #1e2535; color: #4ade80; }
    .sidebar-link.active { background-color: #14532d; color: #4ade80; border-left: 2px solid #4ade80; }
    .card { background-color: #161b27; border: 1px solid #1e2535; border-radius: 0.75rem; }
    .btn-primary { background-color: #4ade80; color: #0f1117; font-weight: 600; padding: 0.5rem 1.25rem; border-radius: 0.5rem; transition: all 0.15s ease; }
    .btn-primary:hover { background-color: #86efac; }
    .btn-secondary { background-color: #1e2535; color: #f1f5f9; font-weight: 500; padding: 0.5rem 1.25rem; border-radius: 0.5rem; transition: all 0.15s ease; border: 1px solid #334155; }
    .btn-secondary:hover { background-color: #263148; }
    .btn-danger { background-color: #7f1d1d; color: #fca5a5; font-weight: 500; padding: 0.5rem 1.25rem; border-radius: 0.5rem; transition: all 0.15s ease; }
    .btn-danger:hover { background-color: #991b1b; }
    .form-input { background-color: #1e2535; border: 1px solid #334155; color: #f1f5f9; border-radius: 0.5rem; padding: 0.5rem 0.75rem; width: 100%; transition: border-color 0.15s ease; }
    .form-input:focus { outline: none; border-color: #4ade80; box-shadow: 0 0 0 1px #4ade80; }
    .form-label { font-size: 0.75rem; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase; color: #94a3b8; margin-bottom: 0.375rem; display: block; }
    .balance-owe { color: #f87171; }
    .balance-owed { color: #4ade80; }
    .balance-zero { color: #94a3b8; }
    .tag { font-size: 0.7rem; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; padding: 0.2rem 0.5rem; border-radius: 0.25rem; }
    .tag-owner { background-color: #1e3a5f; color: #7dd3fc; }
    .tag-admin { background-color: #3b1f5e; color: #c4b5fd; }
    .tag-member { background-color: #1e2535; color: #94a3b8; }
    .tag-active { background-color: #14532d; color: #86efac; }
    .tag-inactive { background-color: #292524; color: #a8a29e; }
    .alert-message { animation: slideIn 0.2s ease; }
    @keyframes slideIn { from { opacity: 0; transform: translateY(-8px); } to { opacity: 1; transform: translateY(0); } }
    select.form-input option { background-color: #1e2535; }
    textarea.form-input { resize: vertical; min-height: 80px; }
  </style>
  {% block extra_head %}{% endblock %}
</head>
<body class="h-full font-sans antialiased">

{% if user.is_authenticated %}
<div class="flex h-full min-h-screen">

  <!-- Sidebar -->
  <aside class="w-60 flex-shrink-0 flex flex-col bg-surface-raised border-r border-surface-border fixed inset-y-0 left-0 z-10">

    <!-- Logo -->
    <div class="px-6 py-6 border-b border-surface-border">
      <a href="{% url 'group_list' %}" class="flex items-center gap-2">
        <div class="w-7 h-7 rounded-md bg-accent flex items-center justify-center">
          <svg class="w-4 h-4 text-surface" fill="currentColor" viewBox="0 0 20 20">
            <path d="M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582zM11 12.849v-1.698c.22.071.412.164.567.267.364.243.433.468.433.582 0 .114-.07.34-.433.582a2.305 2.305 0 01-.567.267z"/>
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z" clip-rule="evenodd"/>
          </svg>
        </div>
        <span class="font-display text-lg text-ink font-bold tracking-tight">SettleUp</span>
      </a>
    </div>

    <!-- Nav -->
    <nav class="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">

      <p class="px-3 pt-2 pb-1 text-xs font-semibold tracking-widest uppercase text-ink-dim">Groups</p>
      <a href="{% url 'group_list' %}" class="sidebar-link flex items-center gap-3 px-3 py-2 rounded-md text-sm text-ink-muted {% block nav_groups %}{% endblock %}">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
        My Groups
      </a>
      <a href="{% url 'group_create' %}" class="sidebar-link flex items-center gap-3 px-3 py-2 rounded-md text-sm text-ink-muted {% block nav_group_create %}{% endblock %}">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
        New Group
      </a>

      {% if group is defined or group %}
      <p class="px-3 pt-4 pb-1 text-xs font-semibold tracking-widest uppercase text-ink-dim">{{ group.name|truncatechars:18 }}</p>
      <a href="{% url 'group_detail' group_id=group.pk %}" class="sidebar-link flex items-center gap-3 px-3 py-2 rounded-md text-sm text-ink-muted {% block nav_dashboard %}{% endblock %}">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg>
        Dashboard
      </a>
      <a href="{% url 'expense_list' group_id=group.pk %}" class="sidebar-link flex items-center gap-3 px-3 py-2 rounded-md text-sm text-ink-muted {% block nav_expenses %}{% endblock %}">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/></svg>
        Expenses
      </a>
      <a href="{% url 'payment_list' group_id=group.pk %}" class="sidebar-link flex items-center gap-3 px-3 py-2 rounded-md text-sm text-ink-muted {% block nav_payments %}{% endblock %}">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"/></svg>
        Payments
      </a>
      <a href="{% url 'member_list' group_id=group.pk %}" class="sidebar-link flex items-center gap-3 px-3 py-2 rounded-md text-sm text-ink-muted {% block nav_members %}{% endblock %}">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/></svg>
        Members
      </a>
      <a href="{% url 'report' group_id=group.pk %}" class="sidebar-link flex items-center gap-3 px-3 py-2 rounded-md text-sm text-ink-muted {% block nav_reports %}{% endblock %}">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>
        Reports
      </a>
      <a href="{% url 'audit_log' group_id=group.pk %}" class="sidebar-link flex items-center gap-3 px-3 py-2 rounded-md text-sm text-ink-muted {% block nav_audit %}{% endblock %}">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
        Audit Log
      </a>
      {% endif %}

      <p class="px-3 pt-4 pb-1 text-xs font-semibold tracking-widest uppercase text-ink-dim">Account</p>
      <a href="{% url 'alert_list' %}" class="sidebar-link flex items-center gap-3 px-3 py-2 rounded-md text-sm text-ink-muted {% block nav_alerts %}{% endblock %}">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/></svg>
        Alerts
        {% if unread_alert_count > 0 %}
        <span class="ml-auto text-xs font-bold bg-accent text-surface rounded-full px-1.5 py-0.5">{{ unread_alert_count }}</span>
        {% endif %}
      </a>
      <a href="{% url 'profile' %}" class="sidebar-link flex items-center gap-3 px-3 py-2 rounded-md text-sm text-ink-muted {% block nav_profile %}{% endblock %}">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>
        Profile
      </a>
    </nav>

    <!-- User footer -->
    <div class="px-4 py-4 border-t border-surface-border">
      <div class="flex items-center gap-3">
        <div class="w-8 h-8 rounded-full bg-accent-dim flex items-center justify-center text-accent text-xs font-bold">
          {{ user.first_name|first|upper }}{{ user.last_name|first|upper }}
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium text-ink truncate">{{ user.get_full_name }}</p>
          <p class="text-xs text-ink-dim truncate">{{ user.email }}</p>
        </div>
        <form method="post" action="{% url 'logout' %}">
          {% csrf_token %}
          <button type="submit" title="Sign out" class="text-ink-dim hover:text-accent transition-colors">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/></svg>
          </button>
        </form>
      </div>
    </div>

  </aside>

  <!-- Main content -->
  <div class="ml-60 flex-1 flex flex-col min-h-screen">

    <!-- Top bar -->
    <header class="h-14 border-b border-surface-border flex items-center px-8 gap-4 sticky top-0 bg-surface z-10">
      <h1 class="text-sm font-semibold text-ink-muted tracking-wide">{% block page_title %}{% endblock %}</h1>
      <div class="ml-auto flex items-center gap-3">
        {% block header_actions %}{% endblock %}
      </div>
    </header>

    <!-- Messages -->
    {% if messages %}
    <div class="px-8 pt-4 space-y-2">
      {% for message in messages %}
      <div class="alert-message flex items-start gap-3 px-4 py-3 rounded-lg text-sm
        {% if message.tags == 'error' %}bg-red-950 border border-red-800 text-red-300
        {% elif message.tags == 'success' %}bg-green-950 border border-green-800 text-green-300
        {% elif message.tags == 'warning' %}bg-yellow-950 border border-yellow-800 text-yellow-300
        {% else %}bg-surface-raised border border-surface-border text-ink-muted{% endif %}">
        <span>{{ message }}</span>
      </div>
      {% endfor %}
    </div>
    {% endif %}

    <!-- Page content -->
    <main class="flex-1 px-8 py-6">
      {% block content %}{% endblock %}
    </main>

  </div>

</div>

{% else %}
<!-- Unauthenticated layout — centered card -->
<div class="min-h-screen flex items-center justify-center px-4">
  <div class="w-full max-w-md">
    <div class="text-center mb-8">
      <div class="inline-flex items-center gap-2 mb-2">
        <div class="w-8 h-8 rounded-md bg-accent flex items-center justify-center">
          <svg class="w-5 h-5 text-surface" fill="currentColor" viewBox="0 0 20 20">
            <path d="M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582zM11 12.849v-1.698c.22.071.412.164.567.267.364.243.433.468.433.582 0 .114-.07.34-.433.582a2.305 2.305 0 01-.567.267z"/>
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z" clip-rule="evenodd"/>
          </svg>
        </div>
        <span class="font-display text-2xl text-ink font-bold">SettleUp</span>
      </div>
      <p class="text-ink-dim text-sm">Shared expenses, simplified.</p>
    </div>
    {% block auth_content %}{% endblock %}
  </div>
</div>
{% endif %}

</body>
</html>


# =============================================================================
# ./templates/users/login.html
# =============================================================================
{% extends "base.html" %}
{% block title %}Sign In — SettleUp{% endblock %}
{% block auth_content %}
<div class="card p-8">
  <h2 class="font-display text-2xl text-ink font-bold mb-6">Welcome back</h2>
  <form method="post" class="space-y-5">
    {% csrf_token %}
    <div>
      <label class="form-label">Email</label>
      <input type="text" name="username" autofocus autocomplete="email"
             class="form-input" placeholder="you@example.com" />
    </div>
    <div>
      <div class="flex items-center justify-between mb-1.5">
        <label class="form-label mb-0">Password</label>
        <a href="{% url 'password_reset' %}" class="text-xs text-accent hover:text-accent-muted transition-colors">Forgot password?</a>
      </div>
      <input type="password" name="password" autocomplete="current-password"
             class="form-input" placeholder="••••••••" />
    </div>
    {% if form.errors %}
    <p class="text-sm text-red-400">Invalid email or password. Please try again.</p>
    {% endif %}
    <button type="submit" class="btn-primary w-full text-center block mt-2">Sign in</button>
  </form>
  <p class="text-center text-sm text-ink-dim mt-6">
    No account? <a href="{% url 'register' %}" class="text-accent hover:underline">Create one</a>
  </p>
</div>
{% endblock %}


# =============================================================================
# ./templates/users/register.html
# =============================================================================
{% extends "base.html" %}
{% block title %}Create Account — SettleUp{% endblock %}
{% block auth_content %}
<div class="card p-8">
  <h2 class="font-display text-2xl text-ink font-bold mb-6">Create your account</h2>
  <form method="post" class="space-y-5">
    {% csrf_token %}
    <div class="grid grid-cols-2 gap-4">
      <div>
        <label class="form-label">First name</label>
        <input type="text" name="first_name" class="form-input" placeholder="Jane" value="{{ form.first_name.value|default:'' }}" />
        {% if form.first_name.errors %}<p class="text-xs text-red-400 mt-1">{{ form.first_name.errors|join:", " }}</p>{% endif %}
      </div>
      <div>
        <label class="form-label">Last name</label>
        <input type="text" name="last_name" class="form-input" placeholder="Smith" value="{{ form.last_name.value|default:'' }}" />
      </div>
    </div>
    <div>
      <label class="form-label">Email</label>
      <input type="email" name="email" class="form-input" placeholder="you@example.com" value="{{ form.email.value|default:'' }}" />
      {% if form.email.errors %}<p class="text-xs text-red-400 mt-1">{{ form.email.errors|join:", " }}</p>{% endif %}
    </div>
    <div>
      <label class="form-label">Password</label>
      <input type="password" name="password1" class="form-input" placeholder="Choose a strong password" />
      {% if form.password1.errors %}<p class="text-xs text-red-400 mt-1">{{ form.password1.errors|join:", " }}</p>{% endif %}
    </div>
    <div>
      <label class="form-label">Confirm password</label>
      <input type="password" name="password2" class="form-input" placeholder="Repeat your password" />
      {% if form.password2.errors %}<p class="text-xs text-red-400 mt-1">{{ form.password2.errors|join:", " }}</p>{% endif %}
    </div>
    <button type="submit" class="btn-primary w-full text-center block mt-2">Create account</button>
  </form>
  <p class="text-center text-sm text-ink-dim mt-6">
    Already have an account? <a href="{% url 'login' %}" class="text-accent hover:underline">Sign in</a>
  </p>
</div>
{% endblock %}


# =============================================================================
# ./templates/users/password_reset.html
# =============================================================================
{% extends "base.html" %}
{% block title %}Reset Password — SettleUp{% endblock %}
{% block auth_content %}
<div class="card p-8">
  <h2 class="font-display text-2xl text-ink font-bold mb-2">Reset your password</h2>
  <p class="text-sm text-ink-dim mb-6">Enter your email and we'll send a reset link.</p>
  <form method="post" class="space-y-5">
    {% csrf_token %}
    <div>
      <label class="form-label">Email</label>
      <input type="email" name="email" class="form-input" placeholder="you@example.com" />
    </div>
    <button type="submit" class="btn-primary w-full text-center block">Send reset link</button>
  </form>
  <p class="text-center text-sm text-ink-dim mt-6">
    <a href="{% url 'login' %}" class="text-accent hover:underline">Back to sign in</a>
  </p>
</div>
{% endblock %}


# =============================================================================
# ./templates/users/password_reset_done.html
# =============================================================================
{% extends "base.html" %}
{% block title %}Check Your Email — SettleUp{% endblock %}
{% block auth_content %}
<div class="card p-8 text-center">
  <div class="w-12 h-12 rounded-full bg-accent-dim flex items-center justify-center mx-auto mb-4">
    <svg class="w-6 h-6 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>
  </div>
  <h2 class="font-display text-xl text-ink font-bold mb-2">Check your email</h2>
  <p class="text-sm text-ink-dim mb-6">If an account exists for that address, we've sent a password reset link.</p>
  <a href="{% url 'login' %}" class="btn-secondary inline-block">Back to sign in</a>
</div>
{% endblock %}


# =============================================================================
# ./templates/users/password_reset_confirm.html
# =============================================================================
{% extends "base.html" %}
{% block title %}Set New Password — SettleUp{% endblock %}
{% block auth_content %}
<div class="card p-8">
  <h2 class="font-display text-2xl text-ink font-bold mb-6">Set a new password</h2>
  <form method="post" class="space-y-5">
    {% csrf_token %}
    <div>
      <label class="form-label">New password</label>
      <input type="password" name="new_password1" class="form-input" />
      {% if form.new_password1.errors %}<p class="text-xs text-red-400 mt-1">{{ form.new_password1.errors|join:", " }}</p>{% endif %}
    </div>
    <div>
      <label class="form-label">Confirm new password</label>
      <input type="password" name="new_password2" class="form-input" />
    </div>
    <button type="submit" class="btn-primary w-full text-center block">Update password</button>
  </form>
</div>
{% endblock %}


# =============================================================================
# ./templates/users/password_reset_complete.html
# =============================================================================
{% extends "base.html" %}
{% block title %}Password Updated — SettleUp{% endblock %}
{% block auth_content %}
<div class="card p-8 text-center">
  <div class="w-12 h-12 rounded-full bg-accent-dim flex items-center justify-center mx-auto mb-4">
    <svg class="w-6 h-6 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
  </div>
  <h2 class="font-display text-xl text-ink font-bold mb-2">Password updated</h2>
  <p class="text-sm text-ink-dim mb-6">You can now sign in with your new password.</p>
  <a href="{% url 'login' %}" class="btn-primary inline-block">Sign in</a>
</div>
{% endblock %}


# =============================================================================
# ./templates/users/profile.html
# =============================================================================
{% extends "base.html" %}
{% block title %}Profile — SettleUp{% endblock %}
{% block page_title %}Profile{% endblock %}
{% block nav_profile %}active{% endblock %}
{% block content %}
<div class="max-w-lg">
  <div class="card p-6">
    <h2 class="font-display text-xl text-ink font-bold mb-6">Your profile</h2>
    <form method="post" class="space-y-5">
      {% csrf_token %}
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="form-label">First name</label>
          <input type="text" name="first_name" class="form-input" value="{{ form.first_name.value|default:'' }}" />
        </div>
        <div>
          <label class="form-label">Last name</label>
          <input type="text" name="last_name" class="form-input" value="{{ form.last_name.value|default:'' }}" />
        </div>
      </div>
      <div>
        <label class="form-label">Email</label>
        <input type="email" name="email" class="form-input" value="{{ form.email.value|default:'' }}" />
        {% if form.email.errors %}<p class="text-xs text-red-400 mt-1">{{ form.email.errors|join:", " }}</p>{% endif %}
      </div>
      <div class="flex gap-3 pt-2">
        <button type="submit" class="btn-primary">Save changes</button>
        <a href="{% url 'password_reset' %}" class="btn-secondary">Change password</a>
      </div>
    </form>
  </div>
</div>
{% endblock %}


# =============================================================================
# ./templates/groups/group_list.html
# =============================================================================
{% extends "base.html" %}
{% block title %}My Groups — SettleUp{% endblock %}
{% block page_title %}My Groups{% endblock %}
{% block nav_groups %}active{% endblock %}
{% block header_actions %}
  <a href="{% url 'group_create' %}" class="btn-primary text-sm">+ New Group</a>
{% endblock %}
{% block content %}
{% if memberships %}
<div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
  {% for membership in memberships %}
  <a href="{% url 'group_detail' group_id=membership.group.pk %}"
     class="card p-6 block hover:border-accent transition-colors group">
    <div class="flex items-start justify-between mb-4">
      <div class="w-10 h-10 rounded-lg bg-accent-dim flex items-center justify-center text-accent font-bold text-lg font-display">
        {{ membership.group.name|first|upper }}
      </div>
      <span class="tag tag-{{ membership.role }}">{{ membership.get_role_display }}</span>
    </div>
    <h3 class="font-semibold text-ink text-base group-hover:text-accent transition-colors mb-1">
      {{ membership.group.name }}
    </h3>
    {% if membership.group.description %}
    <p class="text-xs text-ink-dim line-clamp-2">{{ membership.group.description }}</p>
    {% endif %}
    {% if not membership.group.is_active %}
    <span class="tag tag-inactive mt-3 inline-block">Archived</span>
    {% endif %}
  </a>
  {% endfor %}
</div>
{% else %}
<div class="flex flex-col items-center justify-center py-24 text-center">
  <div class="w-16 h-16 rounded-full bg-surface-raised border border-surface-border flex items-center justify-center mb-4">
    <svg class="w-8 h-8 text-ink-dim" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
  </div>
  <h3 class="font-display text-lg text-ink font-bold mb-2">No groups yet</h3>
  <p class="text-sm text-ink-dim mb-6">Create a group to start tracking shared expenses.</p>
  <a href="{% url 'group_create' %}" class="btn-primary">Create your first group</a>
</div>
{% endif %}
{% endblock %}


# =============================================================================
# ./templates/groups/group_form.html
# =============================================================================
{% extends "base.html" %}
{% block title %}{% if object %}Edit Group{% else %}New Group{% endif %} — SettleUp{% endblock %}
{% block page_title %}{% if object %}Edit Group{% else %}New Group{% endif %}{% endblock %}
{% block nav_group_create %}{% if not object %}active{% endif %}{% endblock %}
{% block content %}
<div class="max-w-lg">
  <div class="card p-6">
    <form method="post" class="space-y-5">
      {% csrf_token %}
      <div>
        <label class="form-label">Group name</label>
        <input type="text" name="name" class="form-input"
               placeholder="e.g. Apartment 4B, Road Trip 2025"
               value="{{ form.name.value|default:'' }}" />
        {% if form.name.errors %}<p class="text-xs text-red-400 mt-1">{{ form.name.errors|join:", " }}</p>{% endif %}
      </div>
      <div>
        <label class="form-label">Description <span class="normal-case font-normal text-ink-dim">(optional)</span></label>
        <textarea name="description" class="form-input"
                  placeholder="What is this group for?">{{ form.description.value|default:'' }}</textarea>
      </div>
      <div class="flex gap-3 pt-2">
        <button type="submit" class="btn-primary">{% if object %}Save changes{% else %}Create group{% endif %}</button>
        <a href="{% url 'group_list' %}" class="btn-secondary">Cancel</a>
      </div>
    </form>
  </div>
</div>
{% endblock %}


# =============================================================================
# ./templates/groups/group_detail.html
# =============================================================================
{% extends "base.html" %}
{% block title %}{{ group.name }} — SettleUp{% endblock %}
{% block page_title %}{{ group.name }}{% endblock %}
{% block nav_dashboard %}active{% endblock %}
{% block header_actions %}
  <a href="{% url 'expense_add' group_id=group.pk %}" class="btn-primary text-sm">+ Add Expense</a>
  <a href="{% url 'payment_add' group_id=group.pk %}" class="btn-secondary text-sm">+ Add Payment</a>
{% endblock %}
{% block content %}

<!-- Balance card -->
<div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
  <div class="card p-5">
    <p class="form-label mb-1">Your Balance</p>
    <p class="text-2xl font-mono font-semibold
      {% if my_balance > 0 %}balance-owe
      {% elif my_balance < 0 %}balance-owed
      {% else %}balance-zero{% endif %}">
      {% if my_balance > 0 %}you owe ${{ my_balance }}
      {% elif my_balance < 0 %}you're owed ${{ my_balance|slice:"1:" }}
      {% else %}all settled{% endif %}
    </p>
  </div>
  <div class="card p-5">
    <p class="form-label mb-1">Your Share</p>
    <p class="text-2xl font-mono font-semibold text-ink">{{ group_member.default_percentage }}%</p>
  </div>
  <div class="card p-5">
    <p class="form-label mb-1">Your Role</p>
    <p class="mt-1"><span class="tag tag-{{ group_member.role }}">{{ group_member.get_role_display }}</span></p>
  </div>
</div>

<!-- Recent expenses -->
<div class="card">
  <div class="flex items-center justify-between px-6 py-4 border-b border-surface-border">
    <h2 class="font-semibold text-ink text-sm">Recent Expenses</h2>
    <a href="{% url 'expense_list' group_id=group.pk %}" class="text-xs text-accent hover:underline">View all</a>
  </div>
  {% if recent_expenses %}
  <div class="divide-y divide-surface-border">
    {% for expense in recent_expenses %}
    <div class="flex items-center gap-4 px-6 py-3">
      <div class="w-8 h-8 rounded-md bg-surface-border flex items-center justify-center flex-shrink-0 text-ink-dim">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/></svg>
      </div>
      <div class="flex-1 min-w-0">
        <p class="text-sm font-medium text-ink truncate">{{ expense.description }}</p>
        <p class="text-xs text-ink-dim">{{ expense.paid_by.user.get_full_name }} · {{ expense.date }}</p>
      </div>
      <div class="text-right">
        <p class="text-sm font-mono font-semibold text-ink">${{ expense.amount }}</p>
        <p class="text-xs text-ink-dim">{{ expense.category.name }}</p>
      </div>
    </div>
    {% endfor %}
  </div>
  {% else %}
  <div class="px-6 py-10 text-center">
    <p class="text-sm text-ink-dim">No expenses yet.</p>
    <a href="{% url 'expense_add' group_id=group.pk %}" class="text-sm text-accent hover:underline mt-1 inline-block">Add the first one</a>
  </div>
  {% endif %}
</div>

{% endblock %}


# =============================================================================
# ./templates/groups/member_list.html
# =============================================================================
{% extends "base.html" %}
{% block title %}Members — {{ group.name }} — SettleUp{% endblock %}
{% block page_title %}Members{% endblock %}
{% block nav_members %}active{% endblock %}
{% block header_actions %}
  {% if group_member.role != 'member' %}
  <a href="{% url 'member_invite' group_id=group.pk %}" class="btn-primary text-sm">+ Invite Member</a>
  {% endif %}
{% endblock %}
{% block content %}

{% comment %} Build a balance lookup dict {% endcomment %}
{% for entry in balances %}
  {% comment %} balances is a list of dicts, we display inline {% endcomment %}
{% endfor %}

<div class="card">
  <div class="divide-y divide-surface-border">
    {% for membership in memberships %}
    <div class="flex items-center gap-4 px-6 py-4">
      <div class="w-9 h-9 rounded-full bg-accent-dim flex items-center justify-center text-accent text-sm font-bold flex-shrink-0">
        {{ membership.user.first_name|first|upper }}{{ membership.user.last_name|first|upper }}
      </div>
      <div class="flex-1 min-w-0">
        <div class="flex items-center gap-2 flex-wrap">
          <p class="text-sm font-semibold text-ink">{{ membership.user.get_full_name }}</p>
          <span class="tag tag-{{ membership.role }}">{{ membership.get_role_display }}</span>
          <span class="tag tag-{{ membership.status }}">{{ membership.get_status_display }}</span>
        </div>
        <p class="text-xs text-ink-dim">{{ membership.user.email }} · {{ membership.default_percentage }}% default share</p>
      </div>
      <!-- Balance for this member -->
      {% for entry in balances %}
        {% if entry.member.pk == membership.pk %}
        <div class="text-right mr-4">
          <p class="text-xs text-ink-dim mb-0.5">Balance</p>
          <p class="text-sm font-mono font-semibold
            {% if entry.balance > 0 %}balance-owe
            {% elif entry.balance < 0 %}balance-owed
            {% else %}balance-zero{% endif %}">
            {% if entry.balance == 0 %}$0.00
            {% elif entry.balance > 0 %}+${{ entry.balance }}
            {% else %}-${{ entry.balance|slice:"1:" }}{% endif %}
          </p>
        </div>
        {% endif %}
      {% endfor %}
      <!-- Actions -->
      {% if group_member.role == 'owner' or group_member.role == 'admin' %}
      {% if membership.pk != group_member.pk %}
      <div class="flex items-center gap-2">
        <a href="{% url 'member_edit' group_id=group.pk member_id=membership.pk %}"
           class="text-xs text-ink-dim hover:text-ink transition-colors px-2 py-1 rounded hover:bg-surface-border">
          Edit
        </a>
        {% if membership.status == 'active' %}
        <form method="post" action="{% url 'member_deactivate' group_id=group.pk member_id=membership.pk %}">
          {% csrf_token %}
          <button type="submit" class="text-xs text-red-400 hover:text-red-300 transition-colors px-2 py-1 rounded hover:bg-surface-border"
                  onclick="return confirm('Deactivate {{ membership.user.get_full_name }}?')">
            Deactivate
          </button>
        </form>
        {% endif %}
      </div>
      {% endif %}
      {% endif %}
    </div>
    {% endfor %}
  </div>
</div>

{% if group_member.role == 'owner' or group_member.role == 'admin' %}
<div class="flex gap-3 mt-4">
  <a href="{% url 'member_rebalance' group_id=group.pk %}" class="btn-secondary text-sm">Rebalance Percentages</a>
  {% if group_member.role == 'owner' %}
  <a href="{% url 'group_transfer_ownership' group_id=group.pk %}" class="btn-secondary text-sm">Transfer Ownership</a>
  {% endif %}
</div>
{% endif %}

{% endblock %}


# =============================================================================
# ./templates/groups/member_form.html
# =============================================================================
{% extends "base.html" %}
{% block title %}Edit Member — SettleUp{% endblock %}
{% block page_title %}Edit Member{% endblock %}
{% block nav_members %}active{% endblock %}
{% block content %}
<div class="max-w-md">
  <div class="card p-6">
    <div class="flex items-center gap-3 mb-6 pb-4 border-b border-surface-border">
      <div class="w-10 h-10 rounded-full bg-accent-dim flex items-center justify-center text-accent font-bold">
        {{ member.user.first_name|first|upper }}{{ member.user.last_name|first|upper }}
      </div>
      <div>
        <p class="font-semibold text-ink">{{ member.user.get_full_name }}</p>
        <p class="text-xs text-ink-dim">{{ member.user.email }}</p>
      </div>
    </div>
    <form method="post" class="space-y-5">
      {% csrf_token %}
      <div>
        <label class="form-label">Role</label>
        <select name="role" class="form-input">
          {% for value, label in form.fields.role.choices %}
            {% if value != 'owner' %}
            <option value="{{ value }}" {% if form.role.value == value %}selected{% endif %}>{{ label }}</option>
            {% endif %}
          {% endfor %}
        </select>
      </div>
      <div>
        <label class="form-label">Default Percentage</label>
        <div class="relative">
          <input type="number" name="default_percentage" step="0.01" min="0.01" max="100"
                 class="form-input pr-8"
                 value="{{ form.default_percentage.value|default:'' }}" />
          <span class="absolute right-3 top-1/2 -translate-y-1/2 text-ink-dim text-sm">%</span>
        </div>
        {% if form.default_percentage.errors %}<p class="text-xs text-red-400 mt-1">{{ form.default_percentage.errors|join:", " }}</p>{% endif %}
        <p class="text-xs text-ink-dim mt-1">Remember to rebalance all members so percentages sum to 100.</p>
      </div>
      <div class="flex gap-3 pt-2">
        <button type="submit" class="btn-primary">Save changes</button>
        <a href="{% url 'member_list' group_id=group.pk %}" class="btn-secondary">Cancel</a>
      </div>
    </form>
  </div>
</div>
{% endblock %}


# =============================================================================
# ./templates/groups/member_invite.html
# =============================================================================
{% extends "base.html" %}
{% block title %}Invite Member — SettleUp{% endblock %}
{% block page_title %}Invite Member{% endblock %}
{% block nav_members %}active{% endblock %}
{% block content %}
<div class="max-w-md">
  <div class="card p-6">
    <p class="text-sm text-ink-dim mb-6">An invitation will be recorded. Once the task runner is enabled, an email will be sent automatically.</p>
    <form method="post" class="space-y-5">
      {% csrf_token %}
      <div>
        <label class="form-label">Email address</label>
        <input type="email" name="email" class="form-input"
               placeholder="newmember@example.com"
               value="{{ form.email.value|default:'' }}" />
        {% if form.email.errors %}<p class="text-xs text-red-400 mt-1">{{ form.email.errors|join:", " }}</p>{% endif %}
      </div>
      <div>
        <label class="form-label">Default Percentage</label>
        <div class="relative">
          <input type="number" name="default_percentage" step="0.01" min="0.01" max="100"
                 class="form-input pr-8"
                 value="{{ form.default_percentage.value|default:'' }}" />
          <span class="absolute right-3 top-1/2 -translate-y-1/2 text-ink-dim text-sm">%</span>
        </div>
        {% if form.default_percentage.errors %}<p class="text-xs text-red-400 mt-1">{{ form.default_percentage.errors|join:", " }}</p>{% endif %}
        <p class="text-xs text-ink-dim mt-1">You will need to rebalance existing members after the invitation is accepted.</p>
      </div>
      <div class="flex gap-3 pt-2">
        <button type="submit" class="btn-primary">Send invitation</button>
        <a href="{% url 'member_list' group_id=group.pk %}" class="btn-secondary">Cancel</a>
      </div>
    </form>
  </div>
</div>
{% endblock %}


# =============================================================================
# ./templates/groups/rebalance.html
# =============================================================================
{% extends "base.html" %}
{% block title %}Rebalance Percentages — SettleUp{% endblock %}
{% block page_title %}Rebalance Percentages{% endblock %}
{% block nav_members %}active{% endblock %}
{% block content %}
<div class="max-w-md">
  <div class="card p-6">
    <p class="text-sm text-ink-dim mb-6">Adjust the default contribution percentages for all active members. The total must equal 100%.</p>
    <form method="post" class="space-y-4" id="rebalanceForm">
      {% csrf_token %}
      {% for field in form %}
      <div>
        <div class="flex items-center justify-between mb-1.5">
          <label class="form-label mb-0">{{ field.label }}</label>
          <span class="text-xs text-ink-dim font-mono" id="val_{{ field.html_name }}">{{ field.value }}%</span>
        </div>
        <div class="relative">
          <input type="number" name="{{ field.html_name }}" step="0.01" min="0" max="100"
                 class="form-input pr-8 pct-input"
                 value="{{ field.value }}" />
          <span class="absolute right-3 top-1/2 -translate-y-1/2 text-ink-dim text-sm">%</span>
        </div>
      </div>
      {% endfor %}
      {% if form.non_field_errors %}
      <p class="text-xs text-red-400">{{ form.non_field_errors|join:", " }}</p>
      {% endif %}
      <div class="flex items-center justify-between pt-2 border-t border-surface-border">
        <span class="text-xs text-ink-dim">Total: <span id="totalDisplay" class="font-mono font-semibold text-ink">0%</span></span>
        <div class="flex gap-3">
          <button type="submit" class="btn-primary">Save</button>
          <a href="{% url 'member_list' group_id=group.pk %}" class="btn-secondary">Cancel</a>
        </div>
      </div>
    </form>
  </div>
</div>
<script>
  const inputs = document.querySelectorAll('.pct-input');
  const totalEl = document.getElementById('totalDisplay');
  function updateTotal() {
    let total = 0;
    inputs.forEach(inp => { total += parseFloat(inp.value) || 0; });
    totalEl.textContent = total.toFixed(2) + '%';
    totalEl.className = 'font-mono font-semibold ' + (Math.abs(total - 100) < 0.01 ? 'text-accent' : 'text-red-400');
  }
  inputs.forEach(inp => inp.addEventListener('input', updateTotal));
  updateTotal();
</script>
{% endblock %}


# =============================================================================
# ./templates/groups/transfer_ownership.html
# =============================================================================
{% extends "base.html" %}
{% block title %}Transfer Ownership — SettleUp{% endblock %}
{% block page_title %}Transfer Ownership{% endblock %}
{% block content %}
<div class="max-w-md">
  <div class="card p-6">
    <p class="text-sm text-red-400 bg-red-950 border border-red-800 rounded-lg px-4 py-3 mb-6">
      Warning: Once you transfer ownership you will become an admin and lose owner privileges.
    </p>
    <form method="post" class="space-y-5">
      {% csrf_token %}
      <div>
        <label class="form-label">Transfer ownership to</label>
        <select name="new_owner" class="form-input">
          <option value="">— Select a member —</option>
          {% for member in form.fields.new_owner.queryset %}
          <option value="{{ member.pk }}" {% if form.new_owner.value == member.pk|stringformat:"s" %}selected{% endif %}>
            {{ member.user.get_full_name }} ({{ member.get_role_display }})
          </option>
          {% endfor %}
        </select>
        {% if form.new_owner.errors %}<p class="text-xs text-red-400 mt-1">{{ form.new_owner.errors|join:", " }}</p>{% endif %}
      </div>
      <div class="flex gap-3 pt-2">
        <button type="submit" class="btn-danger" onclick="return confirm('Are you sure? This cannot be undone.')">Transfer ownership</button>
        <a href="{% url 'member_list' group_id=group.pk %}" class="btn-secondary">Cancel</a>
      </div>
    </form>
  </div>
</div>
{% endblock %}


# =============================================================================
# ./templates/groups/invitation_accept.html
# =============================================================================
{% extends "base.html" %}
{% block title %}Accept Invitation — SettleUp{% endblock %}
{% block auth_content %}
<div class="card p-8 text-center">
  <div class="w-12 h-12 rounded-full bg-accent-dim flex items-center justify-center mx-auto mb-4">
    <svg class="w-6 h-6 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"/></svg>
  </div>
  <h2 class="font-display text-xl text-ink font-bold mb-1">You've been invited</h2>
  <p class="text-sm text-ink-dim mb-2">to join <strong class="text-ink">{{ invitation.group.name }}</strong></p>
  <p class="text-xs text-ink-dim mb-6">Invited by {{ invitation.invited_by.user.get_full_name }}</p>
  {% if invitation.status == 'pending' %}
  <form method="post" class="space-y-3">
    {% csrf_token %}
    <button type="submit" class="btn-primary w-full">Accept invitation</button>
    <a href="{% url 'login' %}" class="btn-secondary w-full block text-center">Sign in first</a>
  </form>
  {% else %}
  <p class="text-sm text-red-400">This invitation is no longer valid ({{ invitation.status }}).</p>
  {% endif %}
</div>
{% endblock %}


# =============================================================================
# ./templates/expenses/expense_list.html
# =============================================================================
{% extends "base.html" %}
{% block title %}Expenses — {{ group.name }} — SettleUp{% endblock %}
{% block page_title %}Expenses{% endblock %}
{% block nav_expenses %}active{% endblock %}
{% block header_actions %}
  <a href="{% url 'expense_add' group_id=group.pk %}" class="btn-primary text-sm">+ Add Expense</a>
{% endblock %}
{% block content %}

<!-- Filters -->
<div class="card p-4 mb-4">
  <form method="get" class="flex flex-wrap gap-3 items-end">
    <div>
      <label class="form-label">From</label>
      <input type="date" name="date_from" class="form-input w-36" value="{{ request.GET.date_from }}" />
    </div>
    <div>
      <label class="form-label">To</label>
      <input type="date" name="date_to" class="form-input w-36" value="{{ request.GET.date_to }}" />
    </div>
    <div>
      <label class="form-label">Category</label>
      <select name="category" class="form-input w-36">
        <option value="">All</option>
        {% for cat in categories %}
        <option value="{{ cat.pk }}" {% if request.GET.category == cat.pk|stringformat:"s" %}selected{% endif %}>{{ cat.name }}</option>
        {% endfor %}
      </select>
    </div>
    <div>
      <label class="form-label">Member</label>
      <select name="member" class="form-input w-36">
        <option value="">All</option>
        {% for m in members %}
        <option value="{{ m.pk }}" {% if request.GET.member == m.pk|stringformat:"s" %}selected{% endif %}>{{ m.user.first_name }}</option>
        {% endfor %}
      </select>
    </div>
    <button type="submit" class="btn-secondary">Filter</button>
    <a href="{% url 'expense_list' group_id=group.pk %}" class="btn-secondary">Clear</a>
    {% if group_member.role != 'member' %}
    <a href="?show_deleted={% if show_deleted %}false{% else %}true{% endif %}"
       class="ml-auto text-xs {% if show_deleted %}text-accent{% else %}text-ink-dim{% endif %} hover:text-ink transition-colors self-end pb-2">
      {% if show_deleted %}Hide deleted{% else %}Show deleted{% endif %}
    </a>
    {% endif %}
  </form>
</div>

<!-- Expense table -->
<div class="card">
  {% if expenses %}
  <div class="divide-y divide-surface-border">
    {% for expense in expenses %}
    <div class="flex items-center gap-4 px-6 py-3 {% if expense.is_deleted %}opacity-40{% endif %}">
      <div class="flex-1 min-w-0">
        <div class="flex items-center gap-2">
          <a href="{% url 'expense_detail' group_id=group.pk expense_id=expense.pk %}"
             class="text-sm font-medium text-ink hover:text-accent transition-colors truncate">
            {{ expense.description }}
          </a>
          {% if expense.is_deleted %}<span class="tag bg-red-950 text-red-400">deleted</span>{% endif %}
        </div>
        <p class="text-xs text-ink-dim">{{ expense.paid_by.user.get_full_name }} · {{ expense.date }} · {{ expense.category.name }}</p>
      </div>
      <p class="text-sm font-mono font-semibold text-ink">${{ expense.amount }}</p>
      {% if not expense.is_deleted %}
      <div class="flex items-center gap-2 ml-2">
        <a href="{% url 'expense_edit' group_id=group.pk expense_id=expense.pk %}"
           class="text-xs text-ink-dim hover:text-ink transition-colors">Edit</a>
        {% if group_member.role != 'member' %}
        <form method="post" action="{% url 'expense_delete' group_id=group.pk expense_id=expense.pk %}">
          {% csrf_token %}
          <button type="submit" class="text-xs text-red-400 hover:text-red-300 transition-colors"
                  onclick="return confirm('Delete this expense?')">Delete</button>
        </form>
        {% endif %}
      </div>
      {% endif %}
    </div>
    {% endfor %}
  </div>
  <!-- Pagination -->
  {% if is_paginated %}
  <div class="flex items-center justify-between px-6 py-3 border-t border-surface-border">
    <span class="text-xs text-ink-dim">Page {{ page_obj.number }} of {{ page_obj.paginator.num_pages }}</span>
    <div class="flex gap-2">
      {% if page_obj.has_previous %}
      <a href="?page={{ page_obj.previous_page_number }}" class="btn-secondary text-xs py-1 px-3">Previous</a>
      {% endif %}
      {% if page_obj.has_next %}
      <a href="?page={{ page_obj.next_page_number }}" class="btn-secondary text-xs py-1 px-3">Next</a>
      {% endif %}
    </div>
  </div>
  {% endif %}
  {% else %}
  <div class="px-6 py-12 text-center">
    <p class="text-sm text-ink-dim">No expenses found.</p>
    <a href="{% url 'expense_add' group_id=group.pk %}" class="text-sm text-accent hover:underline mt-1 inline-block">Add one</a>
  </div>
  {% endif %}
</div>
{% endblock %}


# =============================================================================
# ./templates/expenses/expense_detail.html
# =============================================================================
{% extends "base.html" %}
{% block title %}{{ expense.description }} — SettleUp{% endblock %}
{% block page_title %}Expense Detail{% endblock %}
{% block nav_expenses %}active{% endblock %}
{% block header_actions %}
  <a href="{% url 'expense_edit' group_id=group.pk expense_id=expense.pk %}" class="btn-secondary text-sm">Edit</a>
{% endblock %}
{% block content %}
<div class="max-w-lg">
  <div class="card p-6 space-y-5">
    <div class="flex items-start justify-between">
      <div>
        <h2 class="font-display text-xl text-ink font-bold">{{ expense.description }}</h2>
        <p class="text-sm text-ink-dim mt-1">{{ expense.date }} · {{ expense.category.name }}</p>
      </div>
      <p class="text-2xl font-mono font-semibold text-ink">${{ expense.amount }}</p>
    </div>
    <div class="border-t border-surface-border pt-4 space-y-2">
      <div class="flex justify-between text-sm">
        <span class="text-ink-dim">Paid by</span>
        <span class="text-ink font-medium">{{ expense.paid_by.user.get_full_name }}</span>
      </div>
      <div class="flex justify-between text-sm">
        <span class="text-ink-dim">Added by</span>
        <span class="text-ink">{{ expense.created_by.user.get_full_name }}</span>
      </div>
      {% if expense.notes %}
      <div class="flex justify-between text-sm">
        <span class="text-ink-dim">Notes</span>
        <span class="text-ink">{{ expense.notes }}</span>
      </div>
      {% endif %}
    </div>
    <div class="border-t border-surface-border pt-4">
      <p class="form-label mb-3">Split</p>
      <div class="space-y-2">
        {% for split in expense.splits.all %}
        <div class="flex items-center justify-between">
          <span class="text-sm text-ink">{{ split.group_member.user.get_full_name }}</span>
          <div class="text-right">
            <span class="text-sm font-mono font-semibold text-ink">${{ split.amount }}</span>
            <span class="text-xs text-ink-dim ml-2">{{ split.percentage }}%</span>
          </div>
        </div>
        {% endfor %}
      </div>
    </div>
    <div class="pt-2">
      <a href="{% url 'expense_list' group_id=group.pk %}" class="btn-secondary text-sm">← Back to expenses</a>
    </div>
  </div>
</div>
{% endblock %}


# =============================================================================
# ./templates/expenses/expense_form.html
# =============================================================================
{% extends "base.html" %}
{% block title %}{% if expense %}Edit Expense{% else %}Add Expense{% endif %} — SettleUp{% endblock %}
{% block page_title %}{% if expense %}Edit Expense{% else %}Add Expense{% endif %}{% endblock %}
{% block nav_expenses %}active{% endblock %}
{% block content %}
<div class="max-w-xl">
  <form method="post" id="expenseForm">
    {% csrf_token %}
    {{ formset.management_form }}

    <div class="card p-6 space-y-5 mb-4">
      <h2 class="font-semibold text-ink text-sm border-b border-surface-border pb-3">Expense Details</h2>
      <div>
        <label class="form-label">Description</label>
        <input type="text" name="description" class="form-input"
               placeholder="e.g. Groceries, Electricity bill"
               value="{{ form.description.value|default:'' }}" />
        {% if form.description.errors %}<p class="text-xs text-red-400 mt-1">{{ form.description.errors|join:", " }}</p>{% endif %}
      </div>
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="form-label">Amount</label>
          <div class="relative">
            <span class="absolute left-3 top-1/2 -translate-y-1/2 text-ink-dim">$</span>
            <input type="number" name="amount" step="0.01" min="0.01"
                   class="form-input pl-7"
                   value="{{ form.amount.value|default:'' }}" />
          </div>
          {% if form.amount.errors %}<p class="text-xs text-red-400 mt-1">{{ form.amount.errors|join:", " }}</p>{% endif %}
        </div>
        <div>
          <label class="form-label">Date</label>
          <input type="date" name="date" class="form-input"
                 value="{{ form.date.value|default:'' }}" />
        </div>
      </div>
      <div>
        <label class="form-label">Category</label>
        <select name="category" class="form-input">
          <option value="">— Select category —</option>
          {% for cat in form.fields.category.queryset %}
          <option value="{{ cat.pk }}" {% if form.category.value == cat.pk|stringformat:"s" %}selected{% endif %}>
            {{ cat.name }}
          </option>
          {% endfor %}
        </select>
        {% if form.category.errors %}<p class="text-xs text-red-400 mt-1">{{ form.category.errors|join:", " }}</p>{% endif %}
      </div>
      <div>
        <label class="form-label">Notes <span class="normal-case font-normal text-ink-dim">(optional)</span></label>
        <textarea name="notes" class="form-input">{{ form.notes.value|default:'' }}</textarea>
      </div>
    </div>

    <!-- Splits -->
    <div class="card p-6 space-y-4 mb-4">
      <div class="flex items-center justify-between border-b border-surface-border pb-3">
        <h2 class="font-semibold text-ink text-sm">Split</h2>
        <span class="text-xs text-ink-dim">Total: <span id="splitTotal" class="font-mono font-semibold text-ink">0%</span></span>
      </div>

      <div id="splitRows" class="space-y-3">
        {% for f in formset %}
        <div class="split-row flex items-center gap-3">
          {{ f.id }}
          <div class="flex-1">
            <select name="{{ f.group_member.html_name }}" class="form-input text-sm">
              <option value="">— Member —</option>
              {% for member in f.fields.group_member.queryset %}
              <option value="{{ member.pk }}"
                {% if f.group_member.value == member.pk|stringformat:"s" %}selected{% endif %}>
                {{ member.user.get_full_name }}
              </option>
              {% endfor %}
            </select>
          </div>
          <div class="w-28 relative">
            <input type="number" name="{{ f.percentage.html_name }}"
                   step="0.01" min="0.01" max="100"
                   class="form-input pr-7 text-sm split-pct"
                   value="{{ f.percentage.value|default:'' }}" />
            <span class="absolute right-3 top-1/2 -translate-y-1/2 text-ink-dim text-xs">%</span>
          </div>
          <label class="flex items-center gap-1 text-xs text-ink-dim cursor-pointer">
            <input type="checkbox" name="{{ f.DELETE.html_name }}"
                   class="rounded border-surface-border delete-check"
                   {% if f.DELETE.value %}checked{% endif %} />
            Remove
          </label>
        </div>
        {% endfor %}
      </div>

      <button type="button" id="addSplitRow" class="text-xs text-accent hover:underline">+ Add member</button>
    </div>

    <div class="flex gap-3">
      <button type="submit" class="btn-primary">{% if expense %}Save changes{% else %}Add expense{% endif %}</button>
      <a href="{% url 'expense_list' group_id=group.pk %}" class="btn-secondary">Cancel</a>
    </div>
  </form>
</div>

<script>
  // Live split total
  function updateSplitTotal() {
    const inputs = document.querySelectorAll('.split-pct');
    let total = 0;
    inputs.forEach(inp => {
      const row = inp.closest('.split-row');
      const delCheck = row ? row.querySelector('.delete-check') : null;
      if (!delCheck || !delCheck.checked) {
        total += parseFloat(inp.value) || 0;
      }
    });
    const el = document.getElementById('splitTotal');
    el.textContent = total.toFixed(2) + '%';
    el.className = 'font-mono font-semibold ' + (Math.abs(total - 100) < 0.01 ? 'text-accent' : 'text-red-400');
  }
  document.addEventListener('input', updateSplitTotal);
  document.addEventListener('change', updateSplitTotal);
  updateSplitTotal();
</script>
{% endblock %}


# =============================================================================
# ./templates/payments/payment_list.html
# =============================================================================
{% extends "base.html" %}
{% block title %}Payments — {{ group.name }} — SettleUp{% endblock %}
{% block page_title %}Payments{% endblock %}
{% block nav_payments %}active{% endblock %}
{% block header_actions %}
  <a href="{% url 'payment_add' group_id=group.pk %}" class="btn-primary text-sm">+ Add Payment</a>
{% endblock %}
{% block content %}

<!-- Filters -->
<div class="card p-4 mb-4">
  <form method="get" class="flex flex-wrap gap-3 items-end">
    <div>
      <label class="form-label">From</label>
      <input type="date" name="date_from" class="form-input w-36" value="{{ request.GET.date_from }}" />
    </div>
    <div>
      <label class="form-label">To</label>
      <input type="date" name="date_to" class="form-input w-36" value="{{ request.GET.date_to }}" />
    </div>
    <div>
      <label class="form-label">Member</label>
      <select name="member" class="form-input w-36">
        <option value="">All</option>
        {% for m in group.memberships.all %}
        <option value="{{ m.pk }}" {% if request.GET.member == m.pk|stringformat:"s" %}selected{% endif %}>{{ m.user.first_name }}</option>
        {% endfor %}
      </select>
    </div>
    <button type="submit" class="btn-secondary">Filter</button>
    <a href="{% url 'payment_list' group_id=group.pk %}" class="btn-secondary">Clear</a>
  </form>
</div>

<div class="card">
  {% if payments %}
  <div class="divide-y divide-surface-border">
    {% for payment in payments %}
    <div class="flex items-center gap-4 px-6 py-3">
      <div class="w-8 h-8 rounded-full bg-accent-dim flex items-center justify-center text-accent text-xs font-bold flex-shrink-0">
        {{ payment.paid_by.user.first_name|first|upper }}
      </div>
      <div class="flex-1 min-w-0">
        <p class="text-sm font-medium text-ink">{{ payment.paid_by.user.get_full_name }}</p>
        <p class="text-xs text-ink-dim">{{ payment.date }}{% if payment.notes %} · {{ payment.notes }}{% endif %}</p>
      </div>
      <p class="text-sm font-mono font-semibold balance-owed">${{ payment.amount }}</p>
      {% if group_member.role != 'member' %}
      <form method="post" action="{% url 'payment_delete' group_id=group.pk payment_id=payment.pk %}">
        {% csrf_token %}
        <button type="submit" class="text-xs text-red-400 hover:text-red-300 ml-2"
                onclick="return confirm('Delete this payment?')">Delete</button>
      </form>
      {% endif %}
    </div>
    {% endfor %}
  </div>
  {% if is_paginated %}
  <div class="flex items-center justify-between px-6 py-3 border-t border-surface-border">
    <span class="text-xs text-ink-dim">Page {{ page_obj.number }} of {{ page_obj.paginator.num_pages }}</span>
    <div class="flex gap-2">
      {% if page_obj.has_previous %}<a href="?page={{ page_obj.previous_page_number }}" class="btn-secondary text-xs py-1 px-3">Previous</a>{% endif %}
      {% if page_obj.has_next %}<a href="?page={{ page_obj.next_page_number }}" class="btn-secondary text-xs py-1 px-3">Next</a>{% endif %}
    </div>
  </div>
  {% endif %}
  {% else %}
  <div class="px-6 py-12 text-center">
    <p class="text-sm text-ink-dim">No payments recorded yet.</p>
    <a href="{% url 'payment_add' group_id=group.pk %}" class="text-sm text-accent hover:underline mt-1 inline-block">Add one</a>
  </div>
  {% endif %}
</div>
{% endblock %}


# =============================================================================
# ./templates/payments/payment_form.html
# =============================================================================
{% extends "base.html" %}
{% block title %}Add Payment — SettleUp{% endblock %}
{% block page_title %}Add Payment{% endblock %}
{% block nav_payments %}active{% endblock %}
{% block content %}
<div class="max-w-md">
  <div class="card p-6">
    <p class="text-sm text-ink-dim mb-6">Record a contribution you've made into the pool.</p>
    <form method="post" class="space-y-5">
      {% csrf_token %}
      <div>
        <label class="form-label">Amount</label>
        <div class="relative">
          <span class="absolute left-3 top-1/2 -translate-y-1/2 text-ink-dim">$</span>
          <input type="number" name="amount" step="0.01" min="0.01"
                 class="form-input pl-7"
                 value="{{ form.amount.value|default:'' }}" />
        </div>
        {% if form.amount.errors %}<p class="text-xs text-red-400 mt-1">{{ form.amount.errors|join:", " }}</p>{% endif %}
      </div>
      <div>
        <label class="form-label">Date</label>
        <input type="date" name="date" class="form-input"
               value="{{ form.date.value|default:'' }}" />
      </div>
      <div>
        <label class="form-label">Notes <span class="normal-case font-normal text-ink-dim">(optional)</span></label>
        <textarea name="notes" class="form-input">{{ form.notes.value|default:'' }}</textarea>
      </div>
      <div class="flex gap-3 pt-2">
        <button type="submit" class="btn-primary">Record payment</button>
        <a href="{% url 'payment_list' group_id=group.pk %}" class="btn-secondary">Cancel</a>
      </div>
    </form>
  </div>
</div>
{% endblock %}


# =============================================================================
# ./templates/notifications/notification_list.html
# =============================================================================
{% extends "base.html" %}
{% block title %}Notifications — {{ group.name }} — SettleUp{% endblock %}
{% block page_title %}Notifications{% endblock %}
{% block header_actions %}
  <form method="post" action="{% url 'notification_send' group_id=group.pk %}">
    {% csrf_token %}
    <button type="submit" class="btn-primary text-sm">Notify Members</button>
  </form>
{% endblock %}
{% block content %}
<div class="card">
  {% if notifications %}
  <div class="divide-y divide-surface-border">
    {% for n in notifications %}
    <div class="flex items-start gap-4 px-6 py-4">
      <div class="w-2 h-2 rounded-full mt-1.5 flex-shrink-0
        {% if n.status == 'sent' %}bg-accent
        {% elif n.status == 'failed' %}bg-red-500
        {% else %}bg-yellow-500{% endif %}">
      </div>
      <div class="flex-1">
        <p class="text-sm text-ink">{{ n.message }}</p>
        <p class="text-xs text-ink-dim mt-1">
          {{ n.created_at|date:"M j, Y g:i a" }} ·
          <span class="tag
            {% if n.status == 'sent' %}tag-active
            {% elif n.status == 'failed' %}bg-red-950 text-red-400
            {% else %}bg-yellow-950 text-yellow-400{% endif %}">
            {{ n.status }}
          </span>
          {% if n.triggered_by %}· by {{ n.triggered_by.user.get_full_name }}{% endif %}
        </p>
      </div>
      <p class="text-sm font-mono text-ink-muted">${{ n.balance_snapshot|floatformat:2 }}</p>
    </div>
    {% endfor %}
  </div>
  {% else %}
  <div class="px-6 py-12 text-center">
    <p class="text-sm text-ink-dim">No notifications sent yet.</p>
  </div>
  {% endif %}
</div>
{% endblock %}


# =============================================================================
# ./templates/alerts/alert_list.html
# =============================================================================
{% extends "base.html" %}
{% block title %}Alerts — SettleUp{% endblock %}
{% block page_title %}Alerts{% endblock %}
{% block nav_alerts %}active{% endblock %}
{% block content %}
<div class="max-w-2xl">
  {% if alerts %}
  <div class="space-y-2">
    {% for alert in alerts %}
    <div class="card px-5 py-4 flex items-start gap-4 {% if not alert.is_read %}border-accent{% endif %}">
      <div class="w-2 h-2 rounded-full mt-1.5 flex-shrink-0
        {% if not alert.is_read %}bg-accent{% else %}bg-surface-border{% endif %}">
      </div>
      <div class="flex-1">
        <p class="text-sm text-ink">{{ alert.message }}</p>
        <p class="text-xs text-ink-dim mt-1">{{ alert.created_at|date:"M j, Y g:i a" }}</p>
      </div>
      {% if not alert.is_read %}
      <form method="post" action="{% url 'alert_mark_read' alert_id=alert.pk %}">
        {% csrf_token %}
        <button type="submit" class="text-xs text-ink-dim hover:text-ink transition-colors">Mark read</button>
      </form>
      {% endif %}
    </div>
    {% endfor %}
  </div>
  {% if is_paginated %}
  <div class="flex justify-end gap-2 mt-4">
    {% if page_obj.has_previous %}<a href="?page={{ page_obj.previous_page_number }}" class="btn-secondary text-xs py-1 px-3">Previous</a>{% endif %}
    {% if page_obj.has_next %}<a href="?page={{ page_obj.next_page_number }}" class="btn-secondary text-xs py-1 px-3">Next</a>{% endif %}
  </div>
  {% endif %}
  {% else %}
  <div class="card px-6 py-12 text-center">
    <p class="text-sm text-ink-dim">No alerts — you're all caught up.</p>
  </div>
  {% endif %}
</div>
{% endblock %}


# =============================================================================
# ./templates/audit/audit_log.html
# =============================================================================
{% extends "base.html" %}
{% block title %}Audit Log — {{ group.name }} — SettleUp{% endblock %}
{% block page_title %}Audit Log{% endblock %}
{% block nav_audit %}active{% endblock %}
{% block content %}
<div class="card">
  {% if audit_logs %}
  <div class="divide-y divide-surface-border">
    {% for log in audit_logs %}
    <div class="flex items-start gap-4 px-6 py-3">
      <div class="w-1.5 h-1.5 rounded-full mt-2 flex-shrink-0
        {% if log.event_type == 'role_changed' %}bg-purple-400
        {% elif log.event_type == 'percentage_changed' %}bg-blue-400
        {% elif log.event_type == 'member_deactivated' %}bg-red-400
        {% elif log.event_type == 'ownership_transferred' %}bg-yellow-400
        {% else %}bg-ink-dim{% endif %}">
      </div>
      <div class="flex-1 min-w-0">
        <p class="text-sm text-ink">
          <span class="font-medium">{{ log.acted_by.user.get_full_name }}</span>
          —
          {{ log.get_event_type_display }}
          for <span class="font-medium">{{ log.group_member.user.get_full_name }}</span>
        </p>
        {% if log.old_value or log.new_value %}
        <p class="text-xs text-ink-dim font-mono mt-0.5">
          {{ log.old_value }} → {{ log.new_value }}
        </p>
        {% endif %}
      </div>
      <p class="text-xs text-ink-dim flex-shrink-0">{{ log.timestamp|date:"M j, Y g:i a" }}</p>
    </div>
    {% endfor %}
  </div>
  {% if is_paginated %}
  <div class="flex items-center justify-between px-6 py-3 border-t border-surface-border">
    <span class="text-xs text-ink-dim">Page {{ page_obj.number }} of {{ page_obj.paginator.num_pages }}</span>
    <div class="flex gap-2">
      {% if page_obj.has_previous %}<a href="?page={{ page_obj.previous_page_number }}" class="btn-secondary text-xs py-1 px-3">Previous</a>{% endif %}
      {% if page_obj.has_next %}<a href="?page={{ page_obj.next_page_number }}" class="btn-secondary text-xs py-1 px-3">Next</a>{% endif %}
    </div>
  </div>
  {% endif %}
  {% else %}
  <div class="px-6 py-12 text-center">
    <p class="text-sm text-ink-dim">No activity recorded yet.</p>
  </div>
  {% endif %}
</div>
{% endblock %}


# =============================================================================
# ./templates/reporting/report.html
# =============================================================================
{% extends "base.html" %}
{% block title %}Reports — {{ group.name }} — SettleUp{% endblock %}
{% block page_title %}Reports{% endblock %}
{% block nav_reports %}active{% endblock %}
{% block content %}

<!-- Filters -->
<div class="card p-4 mb-6">
  <form method="get" class="flex flex-wrap gap-3 items-end">
    <div>
      <label class="form-label">From</label>
      <input type="date" name="date_from" class="form-input w-36" value="{{ date_from|default:'' }}" />
    </div>
    <div>
      <label class="form-label">To</label>
      <input type="date" name="date_to" class="form-input w-36" value="{{ date_to|default:'' }}" />
    </div>
    <div>
      <label class="form-label">Category</label>
      <select name="category" class="form-input w-36">
        <option value="">All</option>
        {% for cat in categories %}
        <option value="{{ cat.pk }}" {% if selected_category == cat.pk|stringformat:"s" %}selected{% endif %}>{{ cat.name }}</option>
        {% endfor %}
      </select>
    </div>
    <button type="submit" class="btn-secondary">Run report</button>
    <a href="{% url 'report' group_id=group.pk %}" class="btn-secondary">Clear</a>
  </form>
</div>

{% if by_category %}
<div class="card">
  <div class="px-6 py-4 border-b border-surface-border">
    <h2 class="font-semibold text-ink text-sm">Spending by Category</h2>
  </div>
  {% with total=by_category|length %}
  <div class="divide-y divide-surface-border">
    {% for row in by_category %}
    <div class="flex items-center gap-4 px-6 py-4">
      <div class="flex-1">
        <p class="text-sm font-medium text-ink">{{ row.expense__category__name }}</p>
      </div>
      <div class="text-right">
        <p class="text-sm font-mono font-semibold text-ink">${{ row.total|floatformat:2 }}</p>
      </div>
    </div>
    {% endfor %}
  </div>
  {% endwith %}
</div>
{% else %}
<div class="card px-6 py-12 text-center">
  <p class="text-sm text-ink-dim">No data for the selected filters.</p>
</div>
{% endif %}

{% endblock %}


# =============================================================================
# ./templates/403.html
# =============================================================================
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Access Denied — SettleUp</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@400;500&display=swap" rel="stylesheet" />
  <style>body { background-color: #0f1117; color: #f1f5f9; font-family: 'DM Sans', sans-serif; }</style>
</head>
<body class="min-h-screen flex items-center justify-center">
  <div class="text-center">
    <p class="text-7xl font-bold text-green-400 font-mono mb-4">403</p>
    <h1 class="text-xl font-bold mb-2" style="font-family: 'Playfair Display', serif;">Access Denied</h1>
    <p class="text-slate-400 text-sm mb-6">You don't have permission to view this page.</p>
    <a href="/" class="bg-green-400 text-slate-900 font-semibold px-5 py-2 rounded-lg hover:bg-green-300 transition-colors text-sm">Go home</a>
  </div>
</body>
</html>


# =============================================================================
# ./templates/404.html
# =============================================================================
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Not Found — SettleUp</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@400;500&display=swap" rel="stylesheet" />
  <style>body { background-color: #0f1117; color: #f1f5f9; font-family: 'DM Sans', sans-serif; }</style>
</head>
<body class="min-h-screen flex items-center justify-center">
  <div class="text-center">
    <p class="text-7xl font-bold text-green-400 font-mono mb-4">404</p>
    <h1 class="text-xl font-bold mb-2" style="font-family: 'Playfair Display', serif;">Page Not Found</h1>
    <p class="text-slate-400 text-sm mb-6">The page you're looking for doesn't exist.</p>
    <a href="/" class="bg-green-400 text-slate-900 font-semibold px-5 py-2 rounded-lg hover:bg-green-300 transition-colors text-sm">Go home</a>
  </div>
</body>
</html>


# =============================================================================
# ./templates/500.html
# =============================================================================
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Server Error — SettleUp</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@400;500&display=swap" rel="stylesheet" />
  <style>body { background-color: #0f1117; color: #f1f5f9; font-family: 'DM Sans', sans-serif; }</style>
</head>
<body class="min-h-screen flex items-center justify-center">
  <div class="text-center">
    <p class="text-7xl font-bold text-green-400 font-mono mb-4">500</p>
    <h1 class="text-xl font-bold mb-2" style="font-family: 'Playfair Display', serif;">Something went wrong</h1>
    <p class="text-slate-400 text-sm mb-6">An unexpected error occurred. Please try again.</p>
    <a href="/" class="bg-green-400 text-slate-900 font-semibold px-5 py-2 rounded-lg hover:bg-green-300 transition-colors text-sm">Go home</a>
  </div>
</body>
</html>
