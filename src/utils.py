def format_estimated_time(estimated_seconds):
    total_minutes = estimated_seconds // 60
    seconds = estimated_seconds % 60
    hours = total_minutes // 60
    minutes = total_minutes % 60

    if hours > 0:
        time_str = f"Finish in {int(hours)} hour{'s' if hours > 1 else ''}"
        if minutes > 0:
            time_str += f" and {int(minutes)} minute{'s' if minutes > 1 else ''}"
        if seconds > 0 and minutes == 0:
            time_str += f" and {int(seconds)} second{'s' if seconds > 1 else ''}"
    else:
        if minutes > 0:
            time_str = f"Finish in {int(minutes)} minute{'s' if minutes > 1 else ''}"
        else:
            time_str = f"Finish in {int(seconds)} second{'s' if seconds > 1 else ''}"

    return time_str
