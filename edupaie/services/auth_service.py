"""Authentification locale, rôles, permissions et options de l'application."""

import base64
import hashlib
import hmac
import secrets
from dataclasses import dataclass

from edupaie.database.connection import readonly_connection
from edupaie.database.transaction import transaction
from edupaie.services.exceptions import ValidationError


_ITERATIONS_PBKDF2 = 390_000


@dataclass(frozen=True)
class SessionUtilisateur:
    id: int
    nom_complet: str
    identifiant: str
    roles: frozenset[str]
    permissions: frozenset[str]
    classes: frozenset[int]

    @property
    def est_directeur(self) -> bool:
        return "directeur" in self.roles

    def autorise(self, permission: str) -> bool:
        return permission in self.permissions


class AuthService:
    """Gère les comptes locaux et l'autorisation de l'utilisateur connecté."""

    def __init__(self):
        self.session = None

    def _exiger(self, permission: str) -> None:
        if self.session is None or not self.session.autorise(permission):
            raise ValidationError("Permission administrative insuffisante")

    def installation_requise(self) -> bool:
        with readonly_connection() as conn:
            return conn.execute("SELECT COUNT(*) FROM utilisateurs").fetchone()[0] == 0

    @staticmethod
    def _hash_mot_de_passe(mot_de_passe: str) -> str:
        sel = secrets.token_bytes(16)
        empreinte = hashlib.pbkdf2_hmac(
            "sha256", mot_de_passe.encode("utf-8"), sel, _ITERATIONS_PBKDF2
        )
        sel_encode = base64.urlsafe_b64encode(sel).decode("ascii")
        empreinte_encode = base64.urlsafe_b64encode(empreinte).decode("ascii")
        return f"pbkdf2_sha256${_ITERATIONS_PBKDF2}${sel_encode}${empreinte_encode}"

    @staticmethod
    def _verifier_mot_de_passe(mot_de_passe: str, stockage: str) -> bool:
        try:
            algorithme, iterations, sel_encode, empreinte_attendue = stockage.split("$", 3)
            if algorithme != "pbkdf2_sha256":
                return False
            sel = base64.urlsafe_b64decode(sel_encode.encode("ascii"))
            empreinte = hashlib.pbkdf2_hmac(
                "sha256", mot_de_passe.encode("utf-8"), sel, int(iterations)
            )
            empreinte_encode = base64.urlsafe_b64encode(empreinte).decode("ascii")
            return hmac.compare_digest(empreinte_encode, empreinte_attendue)
        except (ValueError, TypeError):
            return False

    def creer_premier_directeur(self, nom_complet: str, identifiant: str, mot_de_passe: str) -> SessionUtilisateur:
        nom_complet = nom_complet.strip()
        identifiant = identifiant.strip()
        self._valider_compte(nom_complet, identifiant, mot_de_passe)
        with transaction() as conn:
            if conn.execute("SELECT 1 FROM utilisateurs LIMIT 1").fetchone():
                raise ValidationError("Le compte directeur initial existe déjà")
            curseur = conn.execute(
                "INSERT INTO utilisateurs (nom_complet, identifiant, mot_de_passe_hash) VALUES (?, ?, ?)",
                (nom_complet, identifiant, self._hash_mot_de_passe(mot_de_passe)),
            )
            user_id = curseur.lastrowid
            conn.execute(
                "INSERT INTO utilisateur_roles (utilisateur_id, role_code) VALUES (?, 'directeur')",
                (user_id,),
            )
        return self._charger_session(user_id)

    def authentifier(self, identifiant: str, mot_de_passe: str) -> SessionUtilisateur:
        with readonly_connection() as conn:
            row = conn.execute(
                "SELECT id, mot_de_passe_hash, actif FROM utilisateurs WHERE identifiant = ? COLLATE NOCASE",
                (identifiant.strip(),),
            ).fetchone()
        if row is None or not row["actif"] or not self._verifier_mot_de_passe(
            mot_de_passe, row["mot_de_passe_hash"]
        ):
            raise ValidationError("Identifiant ou mot de passe incorrect")

        with transaction() as conn:
            conn.execute(
                "UPDATE utilisateurs SET derniere_connexion = CURRENT_TIMESTAMP WHERE id = ?",
                (row["id"],),
            )
        return self._charger_session(row["id"])

    @staticmethod
    def _valider_compte(nom_complet: str, identifiant: str, mot_de_passe: str) -> None:
        if not nom_complet:
            raise ValidationError("Le nom complet est obligatoire")
        if len(identifiant) < 3:
            raise ValidationError("L'identifiant doit contenir au moins 3 caractères")
        if len(mot_de_passe) < 10:
            raise ValidationError("Le mot de passe doit contenir au moins 10 caractères")

    @staticmethod
    def _charger_session(user_id: int) -> SessionUtilisateur:
        with readonly_connection() as conn:
            user = conn.execute(
                "SELECT id, nom_complet, identifiant FROM utilisateurs WHERE id = ? AND actif = 1",
                (user_id,),
            ).fetchone()
            roles = frozenset(row[0] for row in conn.execute(
                "SELECT role_code FROM utilisateur_roles WHERE utilisateur_id = ?", (user_id,)
            ))
            permissions = frozenset(row[0] for row in conn.execute(
                "SELECT DISTINCT rp.permission_code FROM role_permissions rp "
                "JOIN utilisateur_roles ur ON ur.role_code = rp.role_code "
                "WHERE ur.utilisateur_id = ?", (user_id,)
            ))
            classes = frozenset(row[0] for row in conn.execute(
                "SELECT classe_id FROM utilisateur_classes WHERE utilisateur_id = ?", (user_id,)
            ))
        if user is None:
            raise ValidationError("Compte utilisateur inactif ou introuvable")
        return SessionUtilisateur(
            user["id"], user["nom_complet"], user["identifiant"], roles, permissions, classes
        )

    def lister_utilisateurs(self):
        self._exiger("users.manage")
        with readonly_connection() as conn:
            return conn.execute(
                "SELECT u.id, u.nom_complet, u.identifiant, u.actif, "
                "GROUP_CONCAT(r.nom, ', ') AS roles "
                "FROM utilisateurs u LEFT JOIN utilisateur_roles ur ON ur.utilisateur_id = u.id "
                "LEFT JOIN roles r ON r.code = ur.role_code "
                "GROUP BY u.id ORDER BY u.nom_complet COLLATE NOCASE"
            ).fetchall()

    def lister_roles(self):
        self._exiger("users.manage")
        with readonly_connection() as conn:
            return conn.execute("SELECT code, nom, systeme FROM roles ORDER BY systeme DESC, nom").fetchall()

    def lister_permissions(self, role_code: str):
        self._exiger("permissions.manage")
        with readonly_connection() as conn:
            return conn.execute(
                "SELECT p.code, p.libelle, rp.permission_code IS NOT NULL AS active "
                "FROM permissions p LEFT JOIN role_permissions rp "
                "ON rp.permission_code = p.code AND rp.role_code = ? ORDER BY p.libelle",
                (role_code,),
            ).fetchall()

    def creer_utilisateur(
        self,
        nom_complet: str,
        identifiant: str,
        mot_de_passe: str,
        role_code: str,
        classes: list[int] | None = None,
    ) -> int:
        self._exiger("users.manage")
        nom_complet = nom_complet.strip()
        identifiant = identifiant.strip()
        self._valider_compte(nom_complet, identifiant, mot_de_passe)
        with transaction() as conn:
            if conn.execute("SELECT 1 FROM roles WHERE code = ?", (role_code,)).fetchone() is None:
                raise ValidationError("Rôle introuvable")
            cursor = conn.execute(
                "INSERT INTO utilisateurs (nom_complet, identifiant, mot_de_passe_hash) VALUES (?, ?, ?)",
                (nom_complet, identifiant, self._hash_mot_de_passe(mot_de_passe)),
            )
            user_id = cursor.lastrowid
            conn.execute(
                "INSERT INTO utilisateur_roles (utilisateur_id, role_code) VALUES (?, ?)",
                (user_id, role_code),
            )
            conn.executemany(
                "INSERT INTO utilisateur_classes (utilisateur_id, classe_id) VALUES (?, ?)",
                [(user_id, classe_id) for classe_id in (classes or [])],
            )
        return user_id

    def definir_role_actif(self, utilisateur_id: int, actif: bool) -> None:
        self._exiger("users.manage")
        with transaction() as conn:
            role = conn.execute(
                "SELECT r.code FROM roles r JOIN utilisateur_roles ur ON ur.role_code = r.code "
                "WHERE ur.utilisateur_id = ?", (utilisateur_id,)
            ).fetchall()
            if not actif and any(row[0] == "directeur" for row in role):
                directeurs_actifs = conn.execute(
                    "SELECT COUNT(*) FROM utilisateurs u JOIN utilisateur_roles ur ON ur.utilisateur_id = u.id "
                    "WHERE ur.role_code = 'directeur' AND u.actif = 1 AND u.id != ?",
                    (utilisateur_id,),
                ).fetchone()[0]
                if directeurs_actifs == 0:
                    raise ValidationError("Il faut conserver au moins un compte directeur actif")
            conn.execute("UPDATE utilisateurs SET actif = ? WHERE id = ?", (int(actif), utilisateur_id))

    def definir_permission_role(self, role_code: str, permission_code: str, active: bool) -> None:
        self._exiger("permissions.manage")
        if role_code == "directeur" and not active:
            raise ValidationError("Le rôle Directeur conserve toutes les permissions")
        if role_code == "directeur" and permission_code == "users.manage" and not active:
            raise ValidationError("Le directeur ne peut pas retirer la gestion des comptes")
        with transaction() as conn:
            if active:
                conn.execute(
                    "INSERT OR IGNORE INTO role_permissions (role_code, permission_code) VALUES (?, ?)",
                    (role_code, permission_code),
                )
            else:
                conn.execute(
                    "DELETE FROM role_permissions WHERE role_code = ? AND permission_code = ?",
                    (role_code, permission_code),
                )

    def lister_fonctionnalites(self):
        self._exiger("features.manage")
        with readonly_connection() as conn:
            return conn.execute(
                "SELECT code, nom, active FROM fonctionnalites ORDER BY nom"
            ).fetchall()

    def fonctionnalite_active(self, code: str) -> bool:
        with readonly_connection() as conn:
            row = conn.execute(
                "SELECT active FROM fonctionnalites WHERE code = ?", (code,)
            ).fetchone()
            return bool(row[0]) if row else False

    def definir_fonctionnalite(self, code: str, active: bool) -> None:
        self._exiger("features.manage")
        with transaction() as conn:
            conn.execute("UPDATE fonctionnalites SET active = ? WHERE code = ?", (int(active), code))

    def creer_role(self, nom: str) -> str:
        self._exiger("permissions.manage")
        nom = nom.strip()
        if len(nom) < 2:
            raise ValidationError("Le nom du rôle doit contenir au moins 2 caractères")
        code = "role_" + secrets.token_hex(5)
        with transaction() as conn:
            conn.execute("INSERT INTO roles (code, nom, systeme) VALUES (?, ?, 0)", (code, nom))
        return code

    def modifier_roles_utilisateur(self, utilisateur_id: int, role_codes: list[str]) -> None:
        self._exiger("users.manage")
        if not role_codes:
            raise ValidationError("Chaque compte doit avoir au moins un rôle")
        with transaction() as conn:
            utilisateur = conn.execute(
                "SELECT actif FROM utilisateurs WHERE id = ?", (utilisateur_id,)
            ).fetchone()
            anciens_roles = {
                row[0] for row in conn.execute(
                    "SELECT role_code FROM utilisateur_roles WHERE utilisateur_id = ?",
                    (utilisateur_id,),
                )
            }
            perd_son_role_directeur = "directeur" in anciens_roles and "directeur" not in role_codes
            if utilisateur and utilisateur["actif"] and perd_son_role_directeur:
                autres_directeurs = conn.execute(
                    "SELECT COUNT(*) FROM utilisateurs u JOIN utilisateur_roles ur "
                    "ON ur.utilisateur_id = u.id WHERE ur.role_code = 'directeur' "
                    "AND u.actif = 1 AND u.id != ?",
                    (utilisateur_id,),
                ).fetchone()[0]
                if autres_directeurs == 0:
                    raise ValidationError("Il faut conserver au moins un directeur actif")
            conn.execute("DELETE FROM utilisateur_roles WHERE utilisateur_id = ?", (utilisateur_id,))
            conn.executemany(
                "INSERT INTO utilisateur_roles (utilisateur_id, role_code) VALUES (?, ?)",
                [(utilisateur_id, role_code) for role_code in set(role_codes)],
            )

    def definir_classes_utilisateur(self, utilisateur_id: int, classe_ids: list[int]) -> None:
        self._exiger("users.manage")
        with transaction() as conn:
            conn.execute("DELETE FROM utilisateur_classes WHERE utilisateur_id = ?", (utilisateur_id,))
            conn.executemany(
                "INSERT INTO utilisateur_classes (utilisateur_id, classe_id) VALUES (?, ?)",
                [(utilisateur_id, classe_id) for classe_id in set(classe_ids)],
            )

    def lister_classes_utilisateur(self, utilisateur_id: int) -> set[int]:
        """
        Liste les classes affectées à un utilisateur.

        Args:
            utilisateur_id: ID de l'utilisateur

        Returns:
            Ensemble des IDs des classes
        """
        with readonly_connection() as conn:
            return {row[0] for row in conn.execute(
                "SELECT classe_id FROM utilisateur_classes WHERE utilisateur_id = ?",
                (utilisateur_id,),
            )}
