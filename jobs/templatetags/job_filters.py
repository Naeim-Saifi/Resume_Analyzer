from django import template

register = template.Library()

@register.filter
def dict_get(dictionary, key):
    """Get a value from a dictionary using a key"""
    if isinstance(dictionary, dict):
        return dictionary.get(key, 0)
    return 0

@register.filter
def status_badge_class(status):
    """Return CSS classes for status badges"""
    status_classes = {
        'pending': 'bg-yellow-100 text-yellow-800',
        'under_review': 'bg-blue-100 text-blue-800',
        'interview_scheduled': 'bg-purple-100 text-purple-800',
        'accepted': 'bg-green-100 text-green-800',
        'rejected': 'bg-red-100 text-red-800',
        'withdrawn': 'bg-gray-100 text-gray-800',
    }
    return status_classes.get(status, 'bg-gray-100 text-gray-800')

@register.filter
def status_icon(status):
    """Return appropriate icon for status"""
    status_icons = {
        'pending': '⏳',
        'under_review': '👀',
        'interview_scheduled': '📅',
        'accepted': '✅',
        'rejected': '❌',
        'withdrawn': '🚫',
    }
    return status_icons.get(status, '⏳')
