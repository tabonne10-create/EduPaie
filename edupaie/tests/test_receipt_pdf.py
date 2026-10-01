from types import SimpleNamespace

from edupaie.models.paiement import Paiement
from edupaie.receipts.pdf_generator import generer_recu_pdf


def test_generer_recu_pdf_cree_un_pdf_complet(tmp_path):
    paiement = Paiement(
        id=1,
        eleve_id=4,
        montant=50000,
        date_paiement="2026-10-01",
        mode="especes",
        numero_recu="REC-2026-000001",
        solde_apres=25000,
        cree_le="2026-10-01 10:00:00",
    )
    fiche = {
        "eleve": SimpleNamespace(
            nom="Diallo",
            prenom="Aminata",
            annee_scolaire="2026-2027",
        ),
        "nom_classe": "Terminale A",
    }
    parametres = {
        "nom_etablissement": "École de Démonstration",
        "adresse": "12 rue de l'Éducation",
        "telephone": "+221 77 000 00 00",
        "email": "contact@example.test",
        "devise": "FCFA",
    }
    destination = tmp_path / "recu.pdf"

    resultat = generer_recu_pdf(paiement, fiche, parametres, destination)

    contenu = resultat.read_bytes()
    assert resultat == destination
    assert contenu.startswith(b"%PDF-")
    assert len(contenu) > 1000
    assert b"REC-2026-000001" in contenu
