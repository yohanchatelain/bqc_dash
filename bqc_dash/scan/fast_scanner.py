import os
import re
from pathlib import Path
try:
    import scandir_rs
except ImportError:
    import os as scandir_rs  # Fallback to standard os if scandir_rs not available

from bqc_dash.logger import logger

class FastDirectoryScanner:
    """
    Fast directory scanner using scandir_rs for improved performance.
    Provides fast subject filtering and efficient image loading.
    """
    
    def __init__(self):
        self.subject_map = {}  # Maps subjects to their images
        self.subject_list = []  # Ordered list of subjects
        self.image_list = []    # Flat list of all images
        self.subject_indices = {}  # Maps subjects to their start indices in image_list
        
    def scan_directory(self, input_dir, subject_filter=None):
        """
        Scan directory using fast scandir for better performance.
        Optionally filter subjects by pattern.
        
        Args:
            input_dir: Base directory to scan
            subject_filter: Regex pattern to filter subjects
        
        Returns:
            List of image paths
        """
        logger.info(f"Scanning directory {input_dir} with filter: {subject_filter}")
        
        if not os.path.exists(input_dir):
            logger.warning(f"Directory does not exist: {input_dir}")
            return []
            
        # Reset internal state
        self.subject_map = {}
        self.subject_list = []
        self.image_list = []
        self.subject_indices = {}
        
        # Compile regex pattern if provided
        pattern = None
        if subject_filter:
            try:
                pattern = re.compile(subject_filter)
                logger.info(f"Using regex filter: {subject_filter}")
            except re.error:
                # Fall back to simple string matching if regex is invalid
                logger.warning(f"Invalid regex pattern: {subject_filter}. Using plain text matching.")
                subject_filter = subject_filter.lower()
        
        # First, get all subjects from root GIFs
        gif_dir = Path(input_dir)
        
        # The scandir_rs implementation is much faster for large directories
        try:
            gif_entries = list(scandir_rs.scandir(gif_dir))
            gif_files = [entry.path for entry in gif_entries 
                        if entry.is_file() and entry.name.lower().endswith('.gif')]
        except Exception as e:
            logger.warning(f"Error using scandir_rs, falling back to standard methods: {str(e)}")
            gif_files = list(gif_dir.glob('*.gif'))
            
        # Extract subjects from GIF filenames
        subjects = {}
        for gif_file in gif_files:
            if isinstance(gif_file, str):
                subject = os.path.splitext(os.path.basename(gif_file))[0]
                gif_path = gif_file
            else:
                subject = gif_file.stem
                gif_path = str(gif_file)
            
            # Apply subject filtering
            if pattern:
                if pattern.search(subject):
                    subjects[subject] = gif_path
            elif subject_filter:
                if subject_filter.lower() in subject.lower():
                    subjects[subject] = gif_path
            else:
                subjects[subject] = gif_path
        
        logger.info(f"Found {len(subjects)} subjects after filtering")
        
        # Scan PNG files for each subject
        png_base_dir = os.path.join(input_dir, 'png')
        if not os.path.exists(png_base_dir):
            logger.warning(f"PNG directory does not exist: {png_base_dir}")
            return []
            
        # For each subject, find matching PNG files
        current_index = 0
        
        for subject in sorted(subjects.keys()):
            # Record the start index for this subject
            self.subject_indices[subject] = current_index
            self.subject_list.append(subject)
            
            # Find PNGs for this subject
            subject_dir = os.path.join(png_base_dir, subject)
            if not os.path.exists(subject_dir):
                logger.warning(f"Subject directory not found: {subject_dir}")
                continue
                
            # Use scandir_rs for better performance
            try:
                # Recursive scan for all PNGs in subject directory
                png_files = self._recursive_scan_for_pngs(subject_dir)
            except Exception as e:
                logger.warning(f"Error in fast scan for {subject}, using fallback: {str(e)}")
                # Fallback to standard glob
                png_files = list(Path(subject_dir).glob('**/*.png'))
                png_files = [str(p) for p in png_files]
            
            # Make paths relative to input_dir
            relative_paths = []
            for path in png_files:
                rel_path = os.path.relpath(path, input_dir)
                # Normalize path separators for consistency
                rel_path = rel_path.replace('\\', '/')
                relative_paths.append(rel_path)
            
            # Sort paths naturally
            relative_paths.sort()
            
            # Store in subject map and update flat image list
            self.subject_map[subject] = relative_paths
            self.image_list.extend(relative_paths)
            
            # Update current index
            current_index += len(relative_paths)
            
        logger.info(f"Total images found: {len(self.image_list)}")
        return self.image_list
    
    def _recursive_scan_for_pngs(self, directory):
        """
        Recursively scan a directory for PNG files using scandir_rs.
        Much faster than glob for large directories.
        """
        result = []
        pending_dirs = [directory]
        
        while pending_dirs:
            current_dir = pending_dirs.pop()
            try:
                entries = scandir_rs.scandir(current_dir)
                for entry in entries:
                    if entry.is_dir():
                        pending_dirs.append(entry.path)
                    elif entry.is_file() and entry.name.lower().endswith('.png'):
                        result.append(entry.path)
            except PermissionError:
                logger.warning(f"Permission denied accessing directory: {current_dir}")
            except Exception as e:
                logger.warning(f"Error accessing directory {current_dir}: {str(e)}")
                
        return result
    
    def get_subject_at_index(self, index):
        """
        Get the subject for a given image index.
        """
        if not self.subject_list or index >= len(self.image_list):
            return None
            
        # Find the subject that contains this index
        for i, subject in enumerate(self.subject_list):
            start_idx = self.subject_indices[subject]
            
            # If this is the last subject or the index is before the next subject's start
            if (i == len(self.subject_list) - 1 or 
                index < self.subject_indices[self.subject_list[i+1]]):
                return subject
                
        return None
    
    def get_next_subject_index(self, current_index):
        """
        Get the index of the first image in the next subject.
        Returns None if at the last subject.
        """
        if not self.subject_list or current_index >= len(self.image_list):
            return None
            
        current_subject = self.get_subject_at_index(current_index)
        if not current_subject:
            return 0  # Start at the beginning if no subject found
            
        # Find the index of the current subject in the list
        try:
            subject_idx = self.subject_list.index(current_subject)
        except ValueError:
            return 0
            
        # If we're at the last subject, there's no next subject
        if subject_idx >= len(self.subject_list) - 1:
            return None
            
        # Get the next subject and its start index
        next_subject = self.subject_list[subject_idx + 1]
        return self.subject_indices[next_subject]
    
    def get_prev_subject_index(self, current_index):
        """
        Get the index of the first image in the previous subject.
        Returns None if at the first subject.
        """
        if not self.subject_list or current_index >= len(self.image_list):
            return None
            
        current_subject = self.get_subject_at_index(current_index)
        if not current_subject:
            return 0
            
        # Find the index of the current subject in the list
        try:
            subject_idx = self.subject_list.index(current_subject)
        except ValueError:
            return 0
            
        # If we're at the first subject, there's no previous subject
        if subject_idx <= 0:
            return None
            
        # Get the previous subject and its start index
        prev_subject = self.subject_list[subject_idx - 1]
        return self.subject_indices[prev_subject]
    
    def filter_subjects(self, subject_filter):
        """
        Apply a filter to the existing subject list without rescanning.
        Returns a new filtered image list.
        """
        if not subject_filter:
            return self.image_list
            
        # Try to compile as regex first
        try:
            pattern = re.compile(subject_filter)
            filtered_subjects = [s for s in self.subject_list if pattern.search(s)]
        except re.error:
            # Fall back to simple string matching
            subject_filter = subject_filter.lower()
            filtered_subjects = [s for s in self.subject_list 
                                if subject_filter.lower() in s.lower()]
        
        # Create a filtered image list
        filtered_images = []
        for subject in filtered_subjects:
            filtered_images.extend(self.subject_map[subject])
            
        return filtered_images