import os  
import shutil
import time 
import logging

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# The sleep interval in seconds, controlling how often the script checks for changes.
SLEEP_INTERVAL = 10
# The frequency at which processing updates are logged, in seconds.
LOGGING_FREQUENCY_SECONDS = 60


# Folder to track 
    # ex: "C:\\Users\\UserName\\Downloads"
SOURCE_DIR = "Folder path"
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
    "Music" : [".m4a", ".flac", ".mp3", ".wav", ".wma", ".aac"],
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


class CleanFolder(FileSystemEventHandler):
    '''
    A class that handles cleaning and organizing files in a folder based on their types.
    Inherits from FileSystemEventHandler to react to file system events.
    '''

    def on_modified(self, event):
        '''
        This method will run whenever there is a change in the monitored directory.
        @param event: Event, The file system event that triggered the method.
        '''
        if event.is_directory:
            return

        # Get information about the modified file
        file_path = event.src_path
        filename = os.path.basename(file_path)

        # Extract file extension and convert to lowercase
        _, file_extension = os.path.splitext(filename)
        file_extension = file_extension.lower()

        # Check if the file still exists before processing
        if os.path.exists(file_path):
            # Iterate through defined file categories and their extensions
            for category, extensions in EXTENSIONS.items():
                if file_extension in extensions:
                    # Moves a file to the specified subfolder.
                    CreateSubfolder(DESTINATIONS[category])
                    try:
                        MoveFile(file_path, filename, DESTINATIONS[category])
                        logging.info("Moved: %s -> %s", filename, DESTINATIONS[category])
                    except Exception as e:
                        logging.error("Error moving %s: %s", filename, str(e))
                    print(f"Moved: {filename} -> {DESTINATIONS[category]}")
                    break


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # Initialize CleanFolder event handler and Observer
    event_handler = CleanFolder()
    observer = Observer()

    # Schedule the event handler to monitor the source directory recursively
    observer.schedule(event_handler, SOURCE_DIR, recursive=True)
    observer.start()

    # Log information about the start of the observation
    logging.info("Watching for changes in %s", SOURCE_DIR)

    try:
        # Run the script indefinitely, sleeping in intervals
        while True:
            time.sleep(SLEEP_INTERVAL)

            # Log processing updates at the specified frequency
            if time.time() % LOGGING_FREQUENCY_SECONDS == 0:
                logging.info("Processing every minute")

    except KeyboardInterrupt:
        # Stop the observer and wait for it to finish
        observer.stop()
    observer.join()

