"""Definição de permissões e perfis de acesso."""

from app.extensions import db

# code -> (label, módulo para agrupamento na UI)
PERMISSIONS = {
    "dashboard.view": ("Dashboard", "dashboard"),
    "students.view": ("Estudantes — visualizar", "students"),
    "students.manage": ("Estudantes — cadastrar e editar", "students"),
    "projects.view": ("Projetos — visualizar", "projects"),
    "projects.manage": ("Projetos — cadastrar e editar", "projects"),
    "projects.delete": ("Projetos — excluir", "projects"),
    "projects.article": ("Projetos — artigo científico", "projects"),
    "groups.view": ("Grupos — visualizar", "groups"),
    "groups.manage": ("Grupos — cadastrar e editar", "groups"),
    "groups.delete": ("Grupos — excluir", "groups"),
    "schedule.view": ("Cronograma — visualizar", "schedule"),
    "schedule.manage": ("Cronograma — cadastrar e editar", "schedule"),
    "schedule.delete": ("Cronograma — excluir", "schedule"),
    "activities.view": ("Atividades — visualizar", "activities"),
    "activities.manage": ("Atividades — registrar e editar", "activities"),
    "meetings.view": ("Reuniões — visualizar", "meetings"),
    "meetings.manage": ("Reuniões — agendar e editar", "meetings"),
    "minutes.view": ("Atas — visualizar", "minutes"),
    "minutes.manage": ("Atas — registrar", "minutes"),
    "evidence.view": ("Evidências — visualizar", "evidence"),
    "evidence.manage": ("Evidências — registrar", "evidence"),
    "reports.view": ("Relatórios — visualizar", "reports"),
    "reports.export": ("Relatórios — exportar PDF", "reports"),
    "settings.roles": ("Perfis e permissões", "admin"),
}

MODULE_LABELS = {
    "dashboard": "Dashboard",
    "students": "Estudantes",
    "projects": "Projetos",
    "groups": "Grupos",
    "schedule": "Cronograma",
    "activities": "Atividades",
    "meetings": "Reuniões",
    "minutes": "Atas",
    "evidence": "Evidências",
    "reports": "Relatórios",
    "admin": "Administração",
}

ROLE_LABELS = {
    "admin": "Administrador",
    "leader": "Gerente",
    "participant": "Participante",
}

ALL_PERMISSION_CODES = list(PERMISSIONS.keys())

# Permissões que não podem ser removidas de perfis editáveis (evita bloqueio total).
REQUIRED_PERMISSIONS = ["dashboard.view"]

DEFAULT_ROLE_PERMISSIONS = {
    "admin": ALL_PERMISSION_CODES,
    "leader": [
        "dashboard.view",
        "projects.view", "projects.manage", "projects.article",
        "groups.view", "groups.manage",
        "schedule.view", "schedule.manage",
        "activities.view", "activities.manage",
        "meetings.view", "meetings.manage",
        "minutes.view", "minutes.manage",
        "evidence.view", "evidence.manage",
        "reports.view", "reports.export",
    ],
    "participant": [
        "dashboard.view",
        "projects.view", "projects.article",
        "groups.view",
        "schedule.view", "schedule.manage",
        "activities.view", "activities.manage",
        "meetings.view",
        "minutes.view",
        "evidence.view", "evidence.manage",
        "reports.view",
    ],
}


LANDING_ROUTES = [
    ("dashboard.view", "dashboard.index"),
    ("projects.view", "projects.index"),
    ("groups.view", "groups.index"),
    ("schedule.view", "schedule.index"),
    ("activities.view", "activities.index"),
    ("meetings.view", "meetings.index"),
    ("minutes.view", "minutes.index"),
    ("evidence.view", "evidence.timeline"),
    ("reports.view", "reports.index"),
    ("students.view", "students.index"),
    ("settings.roles", "admin.roles_index"),
]


def normalize_permissions(selected):
    """Garante lista válida e inclui permissões mínimas obrigatórias."""
    valid = [code for code in selected if code in PERMISSIONS]
    merged = list(dict.fromkeys(REQUIRED_PERMISSIONS + valid))
    return merged, set(REQUIRED_PERMISSIONS) - set(valid)


def restore_role_defaults(slug):
    from app.models import RoleProfile

    if slug not in DEFAULT_ROLE_PERMISSIONS:
        return None

    profile = RoleProfile.query.filter_by(slug=slug).first()
    if not profile:
        return None

    profile.permissions = list(DEFAULT_ROLE_PERMISSIONS[slug])
    profile.name = get_role_label(slug)
    db.session.commit()
    return profile


def landing_url_for(user):
    from flask import url_for

    for code, endpoint in LANDING_ROUTES:
        if user_has_permission(user, code):
            return url_for(endpoint)
    return None


def get_role_label(slug):
    return ROLE_LABELS.get(slug, slug)


def get_role_permissions(slug):
    from app.models import RoleProfile

    profile = RoleProfile.query.filter_by(slug=slug).first()
    if profile and profile.permissions:
        return list(profile.permissions)
    return DEFAULT_ROLE_PERMISSIONS.get(slug, [])


def user_has_permission(user, code):
    if not user or not user.is_authenticated:
        return False
    if user.role == "admin":
        return True
    return code in get_role_permissions(user.role)


def permissions_by_module():
    grouped = {}
    for code, (label, module) in PERMISSIONS.items():
        grouped.setdefault(module, []).append({"code": code, "label": label})
    return grouped


def seed_role_profiles():
    from app.models import RoleProfile

    for slug, perms in DEFAULT_ROLE_PERMISSIONS.items():
        profile = RoleProfile.query.filter_by(slug=slug).first()
        if not profile:
            profile = RoleProfile(
                slug=slug,
                name=get_role_label(slug),
                description=f"Perfil padrão: {get_role_label(slug)}",
                permissions=perms,
            )
            db.session.add(profile)
        elif not profile.permissions:
            profile.permissions = perms
        else:
            merged, _ = normalize_permissions(profile.permissions)
            if merged != list(profile.permissions):
                profile.permissions = merged
    db.session.commit()
