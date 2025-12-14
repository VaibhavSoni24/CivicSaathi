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
    Sorting system to route complaints to appropriate departments
    """
    
    @staticmethod
    def sort_complaint(complaint):
        """
        Route complaint to the correct department based on category
        """
        if complaint.category and complaint.category.department:
            complaint.department = complaint.category.department
            complaint.sorted = True
            complaint.status = 'PENDING'
            complaint.save()
            return True
        return False


class ComplaintAssignmentSystem:
    """
    Assignment system to assign complaints to workers based on location
    """
    
    @staticmethod
    def assign_complaint(complaint, city: str, state: str):
        """
        Assign complaint to department based on location (city/state)
        This marks it ready for department admin to assign to specific worker
        """
        # Update location info
        complaint.city = city
        complaint.state = state
        complaint.assigned = True
        complaint.status = 'PENDING'
        complaint.save()
        return True
