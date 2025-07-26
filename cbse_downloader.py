import os
import requests
import zipfile
import io

def generate_cbse_subject_urls(year, exam_type, class_level):
    """Generate URLs for CBSE paper downloads based on subject."""
    subjects = [
        "Accountancy", 
        "Biology", 
        "Business-Studies",
        "Chemistry", 
        "Computer-Science", 
        "Economics", 
        "English-Core", 
        "Geography",
        "Hindi-Core", 
        "History", 
        "Mathematics", 
        "Physics", 
        "Political-Science",
        "Psychology", 
        "Sociology"
    ]
    
    base_url = f"https://www.cbse.gov.in/cbsenew/question-paper/{year}-{exam_type}/XII/{{}}.zip"
    
    # Generate URLs for all subjects
    urls = {}
    for subject in subjects:
        url = base_url.format(subject)
        urls[subject] = url
    
    return urls

def download_and_extract_zip(url, output_folder):
    """Download a ZIP file and extract its contents to the specified folder."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    try:
        print(f"Downloading from: {url}")
        response = requests.get(url, headers=headers, stream=True)
        
        if response.status_code == 200:
            # Load the zip file from memory
            z = zipfile.ZipFile(io.BytesIO(response.content))
            
            # Extract all files
            z.extractall(output_folder)
            
            # Count the number of files extracted
            file_count = len(z.namelist())
            print(f"✓ Successfully extracted {file_count} files to {output_folder}")
            return True
        else:
            print(f"✗ Failed to download {url}. Status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Error processing {url}: {e}")
        return False

def main():
    # Settings
    year = "2024"  # Change to desired year
    exam_type = "COMPTT"  # Options might include: COMPTT, MAIN, etc.
    
    # Base directory for downloads
    base_download_dir = 'cbse_papers'
    
    # Generate URLs for all subjects
    subject_urls = generate_cbse_subject_urls(year, exam_type, "XII")
    
    # Keep track of successful downloads
    successful_downloads = 0
    
    # Download and extract each subject's papers
    for subject, url in subject_urls.items():
        # Create subject-specific folder
        subject_folder = os.path.join(base_download_dir, f"{subject}")
        
        print(f"\nProcessing {subject}...")
        
        # Download and extract
        if download_and_extract_zip(url, subject_folder):
            successful_downloads += 1
    
    print(f"\nDownload complete. Successfully downloaded papers for {successful_downloads} out of {len(subject_urls)} subjects.")
    print(f"Papers saved in: {os.path.abspath(base_download_dir)}")

if __name__ == "__main__":
    main()