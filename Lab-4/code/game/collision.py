"""
collision: figures out whether a falling object is within the basket.
"""


def is_caught(basket_rect, obj):
    """An object is caught only once it has reached basket height and
    overlaps the basket horizontally."""
    reached_basket = obj.y + obj.radius >= basket_rect.top
    within_x = basket_rect.left <= obj.x <= basket_rect.right
    return reached_basket and within_x
