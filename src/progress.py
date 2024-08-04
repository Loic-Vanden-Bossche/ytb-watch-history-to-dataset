import os


def get_last_processed_index(output_file):
    progress_file = f"{output_file}.progress"
    if os.path.exists(progress_file):
        with open(progress_file, 'r') as file:
            last_index = file.read()
            if last_index.isdigit():
                return int(last_index)
    return None


def save_last_processed_index(output_file, index):
    progress_file = f"{output_file}.progress"
    with open(progress_file, 'w') as file:
        file.write(str(index))
