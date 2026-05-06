"""Export transactions as ODS spreadsheet."""

import asyncio
import io
from datetime import date

from odf.opendocument import OpenDocumentSpreadsheet  # type: ignore[import-untyped]
from odf.style import Style, TableCellProperties, TextProperties  # type: ignore[import-untyped]
from odf.table import Table, TableCell, TableRow  # type: ignore[import-untyped]
from odf.text import P  # type: ignore[import-untyped]

from adh6.entity import AbstractMembership, Member, Membership
from adh6.member.interfaces import MemberRepository, MembershipRepository
from adh6.treasury.interfaces import PaymentMethodRepository, TransactionRepository


class ExportManager:
    def __init__(
        self,
        transaction_repository: TransactionRepository,
        payment_method_repository: PaymentMethodRepository,
        member_repository: MemberRepository,
        membership_repository: MembershipRepository,
    ):
        self.transaction_repository = transaction_repository
        self.payment_method_repository = payment_method_repository
        self.member_repository = member_repository
        self.membership_repository = membership_repository

    async def _fetch_members(self, author_ids: set[int]) -> dict[int, Member]:
        results = await asyncio.gather(*[self.member_repository.get_by_id(aid) for aid in author_ids])
        return {m.id: m for m in results if m is not None and m.id is not None}

    async def _fetch_memberships(self, uuids: set[str]) -> dict[str, Membership]:
        async def _get(uuid: str) -> Membership | None:
            items, _ = await self.membership_repository.search(limit=1, filter_=AbstractMembership(uuid=uuid))
            return items[0] if items else None

        results = await asyncio.gather(*[_get(u) for u in uuids])
        return {m.uuid: m for m in results if m is not None}

    async def export(self, from_date: date, to_date: date) -> bytes:
        transactions = await self.transaction_repository.search_for_export(from_date, to_date)

        payment_methods, _ = await self.payment_method_repository.search_by(limit=100)
        pm_map = {pm.id: pm.name for pm in payment_methods if pm.id is not None}

        author_ids = {t.author for t in transactions if t.author is not None}
        membership_uuids = {t.membership_uuid for t in transactions if t.membership_uuid is not None}

        members_map, memberships_map = await asyncio.gather(
            self._fetch_members(author_ids),
            self._fetch_memberships(membership_uuids),
        )

        doc = OpenDocumentSpreadsheet()

        header_style = Style(name="Header", family="table-cell")
        header_style.addElement(TextProperties(fontweight="bold"))
        header_style.addElement(TableCellProperties(backgroundcolor="#4472C4"))
        doc.styles.addElement(header_style)

        table = Table(name="Transactions")

        headers = [
            "Date",
            "Intitulé",
            "Montant (€)",
            "Moyen de paiement",
            "Type",
            "Produit ID",
            "Auteur (identifiant)",
            "Auteur (nom)",
            "Clé API (ID)",
            "UUID adhésion",
            "Adhésion : statut",
            "Adhésion : durée (mois)",
            "Adhésion : chambre",
            "Adhésion : première fois",
            "Adhésion : date création",
        ]

        header_row = TableRow()
        for h in headers:
            cell = TableCell(valuetype="string", stylename="Header")
            cell.addElement(P(text=h))
            header_row.addElement(cell)
        table.addElement(header_row)

        for t in transactions:
            row = TableRow()

            def add_cell(value: str) -> None:
                cell = TableCell(valuetype="string")
                cell.addElement(P(text=str(value) if value is not None else ""))
                row.addElement(cell)

            member = members_map.get(t.author) if t.author is not None else None
            membership = memberships_map.get(t.membership_uuid) if t.membership_uuid else None

            add_cell(t.timestamp.strftime("%Y-%m-%d %H:%M:%S") if t.timestamp else "")
            add_cell(t.name or "")
            add_cell(str(t.value) if t.value is not None else "")
            add_cell(pm_map.get(t.payment_method, str(t.payment_method)) if t.payment_method else "")
            add_cell(t.product_type or "")
            add_cell(str(t.product_id) if t.product_id is not None else "")
            add_cell(member.username if member else "")
            add_cell(f"{member.first_name} {member.last_name}" if member else "")
            add_cell(str(t.api_key_id) if t.api_key_id is not None else "")
            add_cell(t.membership_uuid or "")
            add_cell(membership.status if membership else "")
            add_cell(str(membership.duration) if membership and membership.duration is not None else "")
            add_cell("Oui" if membership and membership.has_room else ("Non" if membership else ""))
            add_cell("Oui" if membership and membership.first_time else ("Non" if membership else ""))
            add_cell(
                membership.created_at.strftime("%Y-%m-%d %H:%M:%S") if membership and membership.created_at else ""
            )

            table.addElement(row)

        doc.spreadsheet.addElement(table)  # type: ignore[attr-defined]

        buf = io.BytesIO()
        doc.save(buf)
        return buf.getvalue()
