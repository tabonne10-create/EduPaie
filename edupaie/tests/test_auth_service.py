import pytest

from edupaie.database.connection import init_database
from edupaie.services.auth_service import AuthService
from edupaie.services.exceptions import ValidationError


def test_bootstrap_directeur_authentification_et_permissions(tmp_path, monkeypatch):
    database_path = tmp_path / "auth.db"
    monkeypatch.setattr(
        "edupaie.database.connection.get_database_path",
        lambda: str(database_path),
    )
    init_database()
    service = AuthService()

    assert service.installation_requise()
    session = service.creer_premier_directeur(
        "Awa Diop",
        "directrice",
        "mot-de-passe-long-123",
    )

    assert session.est_directeur
    assert session.autorise("users.manage")
    assert not service.installation_requise()
    assert service.authentifier("DIRECTRICE", "mot-de-passe-long-123").id == session.id

    with pytest.raises(ValidationError, match="incorrect"):
        service.authentifier("directrice", "mauvais-mot-de-passe")
    with pytest.raises(ValidationError, match="existe déjà"):
        service.creer_premier_directeur("Autre", "autre", "mot-de-passe-long-123")


def test_role_enseignant_et_feature_flags_sont_modifiables(tmp_path, monkeypatch):
    database_path = tmp_path / "roles.db"
    monkeypatch.setattr(
        "edupaie.database.connection.get_database_path",
        lambda: str(database_path),
    )
    init_database()
    service = AuthService()
    session_directeur = service.creer_premier_directeur("Directeur", "directeur", "mot-de-passe-long-123")

    # Définir la session du directeur pour créer un utilisateur
    service.session = session_directeur
    enseignant = service.creer_utilisateur(
        "Moussa Fall",
        "moussa",
        "mot-de-passe-enseignant",
        "enseignant",
    )

    session = service.authentifier("moussa", "mot-de-passe-enseignant")
    assert "students.view" in session.permissions
    assert "payments.cancel" not in session.permissions

    service.definir_fonctionnalite("advanced_reports", True)
    assert service.fonctionnalite_active("advanced_reports")
    assert any(row["id"] == enseignant for row in service.lister_utilisateurs())
