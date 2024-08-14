"""
This method select randomly an element from a list of elements and pop that element from the list.
"""

import random
import time
from typing import List, Any

def prob_based_pick(elements) -> Any:
    """
    Selects a random element from a list and removes it from the list.

    Parameters:
    ----------
    elements : List[Any]
        A list of elements to choose from.

    Returns:
    -------
    Any
        The randomly selected element that has been removed from the list.

    Raises:
    ------
    ValueError:
        If the list is empty, raises a ValueError.
    """
    if not elements:
        raise ValueError("The list is empty and no elements can be popped.")
    print(elements)
    time.sleep(2)
    index = random.randint(0, len(elements) - 1)
    return elements.pop(index)




def relevance_based_pick(elements: List[str],context) -> Any:
    
    pass
