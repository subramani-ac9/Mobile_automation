"""
Tenant Configuration Module
============================
Centralized configuration for tenant-specific field labels, features, and workflow variations.
All tenant-specific logic should reference this configuration.

Usage:
    from constants.tenant_config import TenantConfig
    
    config = TenantConfig.get_config("india")
    product_label = config.field_labels.product  # Returns "Program"
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(frozen=True)
class FieldLabels:
    """Tenant-specific field labels used in UI locators."""
    product: str
    # first_product: str
    max_attendees: str
    is_private_checkbox: str
    city: str
    zipcode: str
    location_search: str
    # first_location: str
    

@dataclass(frozen=True)
class TenantFeatures:
    """Feature flags indicating what features are available for a tenant."""
    has_languages: bool = False
    has_teaching_assistants: bool = False
    has_volunteers: bool = False
    has_timezone_selection: bool = True
    has_aol_center: bool = False
    has_apex_ic_contribution: bool = False
    has_weekend_timing: bool = False
    can_create_new_contact: bool = False
    requires_end_time: bool = True  # US needs both start/end time, India auto-populates end time


@dataclass(frozen=True)
class EventModeLabels:
    """Event mode button labels."""
    in_person: str = "In-person Button"
    online: str = "Online Button"


@dataclass
class TenantConfiguration:
    """Complete configuration for a tenant."""
    tenant_id: str
    tenant_name: str
    field_labels: FieldLabels
    features: TenantFeatures
    event_mode_labels: EventModeLabels = field(default_factory=EventModeLabels)
    
    def get_field_label(self, field_name: str) -> str:
        """Get a field label by name."""
        return getattr(self.field_labels, field_name, field_name)
    
    def has_feature(self, feature_name: str) -> bool:
        """Check if a feature is enabled for this tenant."""
        return getattr(self.features, feature_name, False)


class TenantConfig:
    """Factory class to get tenant configurations."""
    
    _US_CONFIG = TenantConfiguration(
        tenant_id="us",
        tenant_name="The Art of Living Foundation (US)",
        field_labels=FieldLabels(
            product="Product",
            # first_product="Product 1",
            max_attendees="Max Capacity",
            is_private_checkbox="Private Event Checkbox",
            city="City",
            zipcode="Zipcode",
            location_search="Location",
            # first_location="Location 1",
        ),
        features=TenantFeatures(
            has_languages=False,
            has_teaching_assistants=False,
            has_volunteers=False,
            has_timezone_selection=True,
            has_aol_center=True,
            has_apex_ic_contribution=False,
            has_weekend_timing=False,
            can_create_new_contact=False,
            requires_end_time=True,
        ),
    )
    
    _INDIA_CONFIG = TenantConfiguration(
        tenant_id="india",
        tenant_name="The Art of Living Foundation (India)",
        field_labels=FieldLabels(
            product="Program",
            # first_product="Program 1",
            max_attendees="Max Participants",
            is_private_checkbox="Private Program Checkbox",
            city="City/Town/Village",
            zipcode="Pincode",
            location_search="Address",
            # first_location="Address 1",
        ),
        features=TenantFeatures(
            has_languages=True,
            has_teaching_assistants=True,
            has_volunteers=True,
            has_timezone_selection=False,
            has_aol_center=False,
            has_apex_ic_contribution=True,
            has_weekend_timing=True,
            can_create_new_contact=True,
            requires_end_time=False,
        ),
    )
    
    _CONFIGS: Dict[str, TenantConfiguration] = {
        "us": _US_CONFIG,
        "india": _INDIA_CONFIG,
    }
    
    @classmethod
    def get_config(cls, tenant: str) -> TenantConfiguration:
        """
        Get configuration for a specific tenant.
        
        Args:
            tenant: Tenant identifier (e.g., 'us', 'india')
            
        Returns:
            TenantConfiguration for the specified tenant
            
        Raises:
            ValueError: If tenant is not supported
        """
        tenant_lower = tenant.strip().lower() if tenant else "us"
        
        if tenant_lower not in cls._CONFIGS:
            raise ValueError(
                f"Unsupported tenant: '{tenant}'. "
                f"Supported tenants: {list(cls._CONFIGS.keys())}"
            )
        
        return cls._CONFIGS[tenant_lower]
    
    @classmethod
    def get_supported_tenants(cls) -> List[str]:
        """Get list of supported tenant identifiers."""
        return list(cls._CONFIGS.keys())
    
    @classmethod
    def register_tenant(cls, config: TenantConfiguration) -> None:
        """
        Register a new tenant configuration.
        
        Args:
            config: TenantConfiguration to register
        """
        cls._CONFIGS[config.tenant_id.lower()] = config


# Convenience functions for direct access
def get_field_label(tenant: str, field_name: str) -> str:
    """Get a specific field label for a tenant."""
    return TenantConfig.get_config(tenant).get_field_label(field_name)


def has_feature(tenant: str, feature_name: str) -> bool:
    """Check if a tenant has a specific feature."""
    return TenantConfig.get_config(tenant).has_feature(feature_name)
