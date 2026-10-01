"""Génération des reçus de paiement au format PDF."""

from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A5
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from edupaie.utils.format import formater_montant


BORDEAUX = colors.HexColor("#8B0000")
GRIS = colors.HexColor("#555555")


def generer_recu_pdf(paiement, fiche: dict, parametres: dict[str, str], chemin: str | Path) -> Path:
    """Génère un reçu PDF A5 et retourne son chemin."""
    destination = Path(chemin)
    destination.parent.mkdir(parents=True, exist_ok=True)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="ReceiptTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=19,
        leading=23,
        textColor=BORDEAUX,
        alignment=TA_CENTER,
        spaceAfter=4 * mm,
    ))
    styles.add(ParagraphStyle(
        name="ReceiptInstitution",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        alignment=TA_CENTER,
        textColor=BORDEAUX,
    ))
    styles.add(ParagraphStyle(
        name="ReceiptSmall",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        textColor=GRIS,
        alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name="ReceiptBody",
        parent=styles["Normal"],
        fontSize=10,
        leading=15,
        alignment=TA_LEFT,
    ))

    devise = parametres.get("devise") or "FCFA"
    eleve = fiche["eleve"]
    nom_etablissement = parametres.get("nom_etablissement") or "Établissement scolaire"
    entete = [Paragraph(escape(nom_etablissement), styles["ReceiptInstitution"])]

    details_etablissement = [
        parametres.get("sigle", ""),
        parametres.get("adresse", ""),
        parametres.get("telephone", ""),
        parametres.get("email", ""),
    ]
    details_etablissement = [escape(value.strip()) for value in details_etablissement if value and value.strip()]
    if details_etablissement:
        entete.append(Paragraph("<br/>".join(details_etablissement), styles["ReceiptSmall"]))

    try:
        date_paiement = datetime.strptime(paiement.date_paiement, "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError:
        date_paiement = paiement.date_paiement

    modes = {
        "especes": "Espèces",
        "cheque": "Chèque",
        "virement": "Virement",
        "mobile_money": "Mobile Money",
    }
    nom_eleve = f"{eleve.prenom} {eleve.nom}"
    informations = [
        ["N° de reçu", escape(paiement.numero_recu)],
        ["Date", escape(date_paiement)],
        ["Reçu de", escape(nom_eleve)],
        ["Classe", escape(fiche.get("nom_classe", ""))],
        ["Année scolaire", escape(eleve.annee_scolaire)],
    ]
    tableau_informations = Table(informations, colWidths=[34 * mm, 80 * mm], hAlign="LEFT")
    tableau_informations.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (0, -1), GRIS),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 2 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2 * mm),
        ("LINEBELOW", (0, -1), (-1, -1), 0.6, colors.lightgrey),
    ]))

    resume_paiement = Table([
        ["Montant reçu", "Mode de paiement"],
        [formater_montant(paiement.montant, devise), modes.get(paiement.mode, paiement.mode)],
    ], colWidths=[57 * mm, 57 * mm], hAlign="LEFT")
    resume_paiement.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BORDEAUX),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 3 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3 * mm),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.lightgrey),
    ]))

    elements = [
        *entete,
        Spacer(1, 7 * mm),
        Paragraph("REÇU DE PAIEMENT", styles["ReceiptTitle"]),
        tableau_informations,
        Spacer(1, 6 * mm),
        resume_paiement,
        Spacer(1, 8 * mm),
        Paragraph(
            f"Solde restant après paiement : <b>{formater_montant(paiement.solde_apres, devise)}</b>",
            styles["ReceiptBody"],
        ),
        Spacer(1, 12 * mm),
        Paragraph("Merci de votre règlement.", styles["ReceiptSmall"]),
        Spacer(1, 10 * mm),
        Paragraph("Signature et cachet", styles["ReceiptSmall"]),
    ]

    document = SimpleDocTemplate(
        str(destination),
        pagesize=A5,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=13 * mm,
        bottomMargin=13 * mm,
        title=f"Reçu {paiement.numero_recu}",
        author=nom_etablissement,
    )
    document.build(elements)
    return destination
