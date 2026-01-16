import os
import hashlib
import time

Watch_Directory = '.'
Poll_Interval = 3

def calculate_file_hash(filepath):

    #Hash object
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            chunk = f.read(4096)
            while len(chunk) > 0:
                sha256_hash.update(chunk)
                chunk = f.read(4096)

        return sha256_hash.hexdigest()

    except FileNotFoundError:
        return

def start_monitoring():

    baseline = {}
    files = []
    all_items = os.listdir(Watch_Directory)
    for f in all_items:
        full_path = os.path.join(Watch_Directory, f)

        if os.path.isfile(full_path):
            files.append(f)

    for filename in files:
        filepath = os.path.join(Watch_Directory,filename)
        filehash = calculate_file_hash(filepath)
        if filehash:
            baseline[filepath] = filehash

    print(f"Baseline established with {len(baseline)} files.")
    print("Monitoring active... (Press Ctrl+C to stop)")
    print("-------------------------------------------------------")

    #Continuous monitoring
    try:
        while True:
            time.sleep(Poll_Interval)
            
            # Get the current list of files on the disk
            # We use a set for easier comparison logic
            current_files_on_disk = []
            for item in os.listdir(Watch_Directory):
                item_path = os.path.join(Watch_Directory, item)
                if os.path.isfile(item_path):
                    current_files_on_disk.append(item_path)

            for filepath in current_files_on_disk:
                current_hash = calculate_file_hash(filepath)

            # Case A: File is known, check if it changed
                if filepath in baseline:
                    if current_hash != baseline[filepath]:
                        print(f"[ALERT] File MODIFIED: {filepath}")
                        print(f"    Old Hash: {baseline[filepath]}")
                        print(f"    New Hash: {current_hash}")
                        baseline[filepath] = current_hash # Update baseline

               # Case B: File is new (not in baseline)
                else:
                    print(f"[ALERT] New File CREATED: {filepath}")
                    baseline[filepath] = current_hash # Add to baseline

            # CHECK 2: File Deletions
            # If it's in the baseline but NOT on the disk anymore
            # We convert lists to sets to do 'subtraction' easily
            baseline_paths = set(baseline.keys())
            disk_paths = set(current_files_on_disk)
            
            # (Items in Baseline) - (Items on Disk) = Deleted Files
            deleted_files = baseline_paths - disk_paths
            
            for filepath in deleted_files:
                print(f"[ALERT] File DELETED: {filepath}")
                del baseline[filepath] # Remove from baseline

    except KeyboardInterrupt:
        # This handles the Ctrl+C stop 
        print("\nStopping monitor. Goodbye!")

# --- EXECUTION ---
if __name__ == "__main__":
    start_monitoring()

    
    
