"""
This method select randomly an element from a list of elements and pop that element from the list.
"""

import random
from typing import List, Any

def prob_based_pick(items: List[Any]) -> Any:
    """
    Randomly pick an item from the list.
    """
    if not items:
        raise ValueError("Cannot pick from empty list")
    return random.choice(items)




def relevance_based_pick(elements: List[str],context) -> Any:
    
    pass
