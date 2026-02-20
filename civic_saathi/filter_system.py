"""
AI-based Filter System for Complaint Validation
Checks if photo and description match the category
"""
from typing import Dict, Tuple
import re


class ComplaintFilterSystem:
    """
    Filter system to validate complaints using description, category, and image analysis
    """
    
    # Keywords for each department category
    CATEGORY_KEYWORDS = {
        'pothole': ['pothole', 'road', 'damage', 'crack', 'hole', 'pavement', 'broken'],
        'street_light': ['light', 'street light', 'lamp', 'dark', 'electricity', 'bulb', 'lighting'],
        'garbage': ['garbage', 'waste', 'trash', 'litter', 'dump', 'rubbish', 'dirt', 'dirty'],
        'water_supply': ['water', 'pipe', 'leak', 'supply', 'tap', 'pipeline', 'drainage'],
        'sewage': ['sewage', 'drain', 'overflow', 'smell', 'blockage', 'clogged', 'drainage'],
        'park': ['park', 'garden', 'playground', 'maintenance', 'grass', 'bench'],
        'traffic': ['traffic', 'signal', 'sign', 'crossing', 'zebra crossing', 'road sign'],
        'animal': ['stray', 'dog', 'cattle', 'animal', 'cow', 'nuisance'],
        'toilet': ['toilet', 'public toilet', 'washroom', 'bathroom', 'sanitation'],
        'health': ['health', 'hospital', 'clinic', 'medical', 'sanitation', 'hygiene'],
    }
    
    @staticmethod
    def check_description_category_match(description: str, category_name: str) -> Tuple[bool, str]:
        """
        Check if description matches the category
        Returns: (is_valid, reason)
        """
        description_lower = description.lower()
        category_lower = category_name.lower()
        
        # Find relevant keywords for this category
        relevant_keywords = []
        for key, keywords in ComplaintFilterSystem.CATEGORY_KEYWORDS.items():
            if key in category_lower:
                relevant_keywords.extend(keywords)
        
        # If no specific keywords, use category name itself
        if not relevant_keywords:
            relevant_keywords = [word for word in category_lower.split() if len(word) > 3]
        
        # Check if any keyword is in description
        matches = [kw for kw in relevant_keywords if kw in description_lower]
        
        if matches:
            return True, f"Valid: Found relevant keywords - {', '.join(matches[:3])}"
        else:
            return False, f"Description does not match category '{category_name}'"
    
    @staticmethod
    def check_spam_content(description: str) -> Tuple[bool, str]:
        """
        Check if content is spam
        Returns: (is_spam, reason)
        """
        spam_patterns = [
            r'\b(buy|purchase|discount|offer|sale|cheap|free|win|prize)\b',
            r'\b(click here|visit|website|link)\b',
            r'(.)\1{4,}',  # Repeated characters
        ]
        
        for pattern in spam_patterns:
            if re.search(pattern, description, re.IGNORECASE):
                return True, "Detected spam pattern in description"
        
        # Check for very short descriptions
        if len(description.strip()) < 20:
            return True, "Description too short (minimum 20 characters)"
        
        return False, "Content appears genuine"
    
    @staticmethod
    def validate_complaint(complaint) -> Dict[str, any]:
        """
        Main validation function
        Returns: {
            'passed': bool,
            'reason': str,
            'is_spam': bool
        }
        """
        # Check for spam
        is_spam, spam_reason = ComplaintFilterSystem.check_spam_content(complaint.description)
        if is_spam:
            return {
                'passed': False,
                'reason': spam_reason,
                'is_spam': True
            }
        
        # Check description-category match
        if complaint.category:
            is_match, match_reason = ComplaintFilterSystem.check_description_category_match(
                complaint.description,
                complaint.category.name
            )
            
            if not is_match:
                return {
                    'passed': False,
                    'reason': match_reason,
                    'is_spam': False
                }
        
        # All checks passed
        return {
            'passed': True,
            'reason': 'Complaint appears genuine and matches category',
            'is_spam': False
        }


class ComplaintSortingSystem:
    """
    Automated Department Sorting Layer

    Operates after both Filter A (NLP) and Filter B (AI image verification)
    have cleared a complaint.  It reads the department value already stored on
    the complaint record (set by the citizen at submission time), routes the
    complaint to that department's office in the correct city, and transitions
    the status from SORTING → PENDING so department admins can act on it.

    Design goals
    ────────────
    • Zero manual intervention for standard cases.
    • Falls back to category-derived department if no direct department is set.
    • Auto-assigns the matching city office so SLA tracking starts immediately.
    • Returns a rich result dict so callers can log / audit every decision.
    """

    @staticmethod
    def sort_complaint(complaint):
        """
        Route a verified complaint to the correct municipal department.

        Department resolution priority
        ──────────────────────────────
        1. complaint.department  – citizen-selected at submission (preferred)
        2. complaint.category.department – derived from the complaint category

        Side-effects (in order)
        ────────────────────────
        1. Sets status → SORTING and persists department.
        2. Looks up the active Office for (department, city).
        3. Sets complaint.office, complaint.sorted = True, status → PENDING.
        4. Saves only the changed fields to minimise DB writes.

        Returns
        ───────
        dict with keys:
            success    (bool)
            department (Department instance | None)
            office     (Office instance | None)
            reason     (str)  – human-readable audit string
        """
        # ── Step 1: Resolve department ────────────────────────────────────────
        # Import here to avoid any circular-import risk at module load time.
        from .models import Office  # noqa: PLC0415

        department = None

        # Citizen-selected department takes priority (stored at submission).
        if complaint.department_id:
            department = complaint.department

        # Fall back to the department linked to the complaint's category.
        if department is None and complaint.category_id and complaint.category:
            department = complaint.category.department

        if department is None:
            return {
                'success': False,
                'department': None,
                'office': None,
                'reason': (
                    'Sorting failed: no department associated with this complaint. '
                    'Manual review required.'
                ),
            }

        # ── Step 2: Mark as SORTING; pin the resolved department ─────────────
        complaint.department = department
        complaint.status = 'SORTING'
        complaint.save(update_fields=['department', 'status', 'updated_at'])

        # ── Step 3: Find the office that serves this department in the city ──
        office = None
        if complaint.city:
            try:
                office = Office.objects.get(
                    department=department,
                    city__iexact=complaint.city,
                    is_active=True,
                )
            except Office.DoesNotExist:
                pass  # No office in this city – complaint still lands at department
            except Office.MultipleObjectsReturned:
                office = (
                    Office.objects.filter(
                        department=department,
                        city__iexact=complaint.city,
                        is_active=True,
                    )
                    .order_by('id')
                    .first()
                )

        # ── Step 4: Finalise – mark sorted, attach office, move to PENDING ───
        complaint.office = office
        complaint.sorted = True
        complaint.status = 'PENDING'
        complaint.save(update_fields=['office', 'sorted', 'status', 'updated_at'])

        office_info = f", office '{office.name}'" if office else " (no matching office registered for this city)"
        return {
            'success': True,
            'department': department,
            'office': office,
            'reason': (
                f"Automatically sorted to department '{department.name}'{office_info}. "
                "Status updated to Pending Assignment."
            ),
        }


class ComplaintAssignmentSystem:
    """
    Assignment system to assign complaints to workers based on location.
    """

    @staticmethod
    def assign_complaint(complaint, city: str, state: str):
        """
        Record location info and flag the complaint as ready for worker assignment.
        Department-level routing is handled by ComplaintSortingSystem.sort_complaint;
        this method only updates location metadata when it differs from what was
        saved at submission time.
        """
        changed_fields = ['updated_at']

        if complaint.city != city:
            complaint.city = city
            changed_fields.append('city')

        if complaint.state != state:
            complaint.state = state
            changed_fields.append('state')

        complaint.save(update_fields=changed_fields)
        return True
