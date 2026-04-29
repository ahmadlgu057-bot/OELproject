"""
Member management service.

Validates inputs and orchestrates CRUD operations for library members,
including registration, updates, search, and deactivation.
"""

from app.models.member import MemberModel
from app.utils.validators import (
    validate_email,
    validate_phone,
    validate_required_fields,
)


class MemberService:
    """Business logic for managing library members."""

    @staticmethod
    def register_member(name: str, email: str, phone: str = "",
                        address: str = "") -> int:
        """
        Register a new library member after input validation.

        Args:
            name:    Full name.
            email:   Email address (must be unique).
            phone:   Contact number.
            address: Postal address.

        Returns:
            The new member's id.

        Raises:
            ValueError: On missing fields, bad email/phone format,
                        or duplicate email.
        """
        missing = validate_required_fields({"Name": name, "Email": email})
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        if not validate_email(email):
            raise ValueError("Invalid email address format.")

        if phone and not validate_phone(phone):
            raise ValueError("Invalid phone number format.")

        return MemberModel.create(name, email, phone, address)

    @staticmethod
    def update_member(member_id: int, **fields) -> None:
        """
        Update member details with validation.

        Args:
            member_id: Primary key.
            **fields:  Columns to update.

        Raises:
            ValueError: If member not found or validation fails.
        """
        member = MemberModel.get_by_id(member_id)
        if member is None:
            raise ValueError("Member not found.")

        if "email" in fields and not validate_email(fields["email"]):
            raise ValueError("Invalid email address format.")

        if "phone" in fields and fields["phone"]:
            if not validate_phone(fields["phone"]):
                raise ValueError("Invalid phone number format.")

        MemberModel.update(member_id, **fields)

    @staticmethod
    def deactivate_member(member_id: int) -> None:
        """
        Soft‑delete a member (set inactive).

        Args:
            member_id: Primary key.

        Raises:
            ValueError: If member not found.
        """
        member = MemberModel.get_by_id(member_id)
        if member is None:
            raise ValueError("Member not found.")
        MemberModel.deactivate(member_id)

    @staticmethod
    def search_members(keyword: str) -> list[dict]:
        """Search members by name, email, or phone."""
        if not keyword.strip():
            return MemberModel.get_all()
        return MemberModel.search(keyword)

    @staticmethod
    def get_all_members() -> list[dict]:
        """Return all active members."""
        return MemberModel.get_all()

    @staticmethod
    def get_member(member_id: int) -> dict | None:
        """Return a single member by id."""
        return MemberModel.get_by_id(member_id)
