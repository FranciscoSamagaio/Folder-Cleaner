import os 
import shutil
import logging

# Folder to track 
    # ex: "C:\\Users\\UserName\\Downloads"
SOURCE_DIR = "C:\\Users\\ksama\\Downloads"
DESTINATIONS = {
    "Music" : os.path.join(SOURCE_DIR, "Musics"),
    "Videos" : os.path.join(SOURCE_DIR, "Videos"),
    "Images" : os.path.join(SOURCE_DIR, "Images"),
    "Documents" : os.path.join(SOURCE_DIR, "Documents"),
    "Presentations" : os.path.join(SOURCE_DIR, "Documents\\Presentations"),
    "Excel" : os.path.join(SOURCE_DIR, "Documents\\Excel"),
}

# Extensions from differnte files 
EXTENSIONS = {
    # Image types
    "Images" : [".jpg", ".jpeg", ".jpe", ".jif", ".jfif", ".jfi", ".png", ".gif", ".webp", ".tiff", ".tif", ".psd", ".raw", ".arw", ".cr2", ".nrw",
                        ".k25", ".bmp", ".dib", ".heif", ".heic", ".ind", ".indd", ".indt", ".jp2", ".j2k", ".jpf", ".jpf", ".jpx", ".jpm", ".mj2", ".svg", ".svgz", ".ai", ".eps", ".ico"],
    # Video types
    "Videos" : [".webm", ".mpg", ".mp2", ".mpeg", ".mpe", ".mpv", ".ogg",
                        ".mp4", ".mp4v", ".m4v", ".avi", ".wmv", ".mov", ".qt", ".flv", ".swf", ".avchd"],
    # Audio types
    "Music" : [".m4a", ".flac", "mp3", ".wav", ".wma", ".aac"],
    # Document types
    "Documents" : [".doc", ".docx", ".odt", ".pdf", ".txt"],
    # Presentations types
    "Presentations" : [".ppt", ".pptx"],
    # Excel types
    "Excel" : [".csv", ".xls", ".xlsx"]
}


def RenameFile(dest, name):
    '''
    Rename a file to avoid overwriting an existing file with the same name in the specified destination.
    @param dest: str, The destination directory where the file should be renamed.
    @param name: str, The original name of the file.
    @return name: str, The new name for the file that does not conflict with existing files in the destination.
    Example:
        >> RenameFile("/path/to/destination", "example.txt")
        Output: "example(1).txt" (or the next available variation if "example.txt" already exists)
    '''
    filename, extension = os.path.splitext(name)
    counter = 1
    while os.path.exists(f"{dest}/{name}"):
        name = f"{filename}({str(counter)}){extension}"
        counter += 1

    return name


def CreateSubfolder(subfolder_path):
    '''
    Creates a subfolder in the specified path if it doesn't already exist.
    @param subfolder_path: str, The path where the subfolder should be created.
    @return subfolder_path: str, The path of the created subfolder or the existing subfolder if it already exists.
    Example:
        >> CreateSubfolder("/path/to/subfolder")
        Output: "/path/to/subfolder" (created if not exists or existing if already present)
    '''
    # Check if the subfolder already exists
    if not os.path.exists(subfolder_path):
        # Create the subfolder if it doesn't exist
        os.makedirs(subfolder_path)
    
    return subfolder_path


def MoveFile(file_path, filename, destination):
    '''
    Move a file to a specified destination, ensuring no overwriting occurs by renaming the file if needed.
    @param file_path: str, The current path of the file to be moved.
    @param filename: str, The name of the file to be moved.
    @param destination: str, The destination directory where the file should be moved.
    @return: none 
    Example:
        >> MoveFile("/path/to/source", "example.txt", "/path/to/destination")
        (Moves "example.txt" from "/path/to/source" to "/path/to/destination", handles renaming if necessary)
    '''
    # Form the full path of the file in the destination
    destination_file_path = os.path.join(destination, filename)

    # Check if a file with the same name already exists in the destination
    if os.path.exists(destination_file_path):
        # If so, rename the file to avoid overwriting
        unique_name = RenameFile(destination, filename)
        new_destination_file_path = os.path.join(destination, unique_name)
        
        # Move the existing file with the same name to the new unique name
        shutil.move(destination_file_path, new_destination_file_path)

    # Move the original file to the specified destination
    shutil.move(file_path, destination)


def CleanFolder(folder_path):
    '''
    Organizes files into subfolders based on file type.
    @param folder_path: str, The path to the folder containing files to be organized.
    @return: None
    Example:
        >> CleanFolder("/path/to/source_folder")
        (Organizes files in "/path/to/source_folder" into subfolders based on file type)
    '''
    # Iterate through files in the specified folder
    for filename in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, filename)):
            # Get file extension and file path
            _, file_extension = os.path.splitext(filename)
            file_extension = file_extension.lower()
            file_path = os.path.join(folder_path, filename)
            
            # Check file extensions and move accordingly
            for category, extensions in EXTENSIONS.items():
                if file_extension in extensions:
                    # Moves a file to the specified subfolder.
                    CreateSubfolder(DESTINATIONS[category])
                    try:
                        MoveFile(file_path, filename, DESTINATIONS[category])
                        logging.info("Moved: %s -> %s", filename, DESTINATIONS[category])
                    except Exception as e:
                        logging.error("Error moving %s: %s", filename, str(e))
                    break


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    
    logging.info(f"{os.path.basename(SOURCE_DIR)} Cleaner Script")

    if os.path.isdir(SOURCE_DIR):
        CleanFolder(SOURCE_DIR)
        logging.info("Cleaning complete.")
    else:
        logging.error(f"Invalid folder {os.path.basename(SOURCE_DIR)}. Please ensure the path is correct and try again.")
