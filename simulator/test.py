import utils_file

folder_name = f"{utils_file.getCurrPath()}/logs/test"

print("Using Saved Data")
saved_data = utils_file.openFile(f"{folder_name}")
print(saved_data)