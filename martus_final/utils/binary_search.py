def binary_search(sorted_list: list, target: str) -> tuple:
    """
    Search for `target` in a sorted list of strings (case-insensitive).

    Returns (index, steps_log).
      index     : position found, or -1 if not found
      steps_log : human-readable list showing each comparison step
    """
    target = target.strip().upper()
    low, high = 0, len(sorted_list) - 1
    steps = []
    step_num = 0

    while low <= high:
        step_num += 1
        mid = (low + high) // 2
        mid_val = sorted_list[mid].upper()

        steps.append(
            f"Step {step_num}: range [{low}..{high}]  mid={mid}  "
            f"checking '{sorted_list[mid]}'"
        )

        if mid_val == target:
            steps.append(
                f"  Found '{sorted_list[mid]}' at index {mid} "
                f"in {step_num} step(s)."
            )
            return mid, steps
        elif mid_val < target:
            steps.append(
                f"  '{sorted_list[mid]}' < '{target}'  search RIGHT half"
            )
            low = mid + 1
        else:
            steps.append(
                f"  '{sorted_list[mid]}' > '{target}'  search LEFT half"
            )
            high = mid - 1

    steps.append(f"  '{target}' not found after {step_num} step(s).")
    return -1, steps
