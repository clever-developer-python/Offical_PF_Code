import os
import requests
from bs4 import BeautifulSoup
import urllib.parse

def generate_igcse_urls():
    """Generate a dictionary of IGCSE subject URLs with names and codes."""
    subjects = {
    "accounting-9706": "Accounting (9706)",
    "biology-9700": "Biology (9700)",
    "business9609": "Business (9609)",
    "chemistry-9701": "Chemistry (9701)",
    "chinese-language-9715": "Chinese Language (9715)",
    "economics-9708": "Economics (9708)",
    "english-9093": "English Language (9093)",
    "english-literature-9695": "English Literature (9695)",
    "environmental-management-8291": "Environmental Management (8291)",
    "french-9716": "French (9716)",
    "geography-9696": "Geography (9696)",
    "german-9717": "German (9717)",
    "global-perspectives-and-research-9239": "Global Perspectives and Research (9239)",
    "history-9389": "History (9389)",
    "information-technology-9626": "Information Technology (9626)",
    "law-9084": "Law (9084)",
    "literature-in-english-9695": "Literature in English (9695)",
    "marine-science-9695": "Marine Science (9695)",
    "mathematics-9231": "Mathematics (9231)",
    "mathematics-9709": "Further Mathematics (9709)",
    "music-9483": "Music (9483)",
    "physical-education-9396": "Physical Education (9396)",
    "physics-9702": "Physics (9702)",
    "psychology-9698": "Psychology (9698)",
    "religious-studies-9084": "Religious Studies (9084)",
    "sociology-9699": "Sociology (9699)",
    "spanish-9715": "Spanish (9715)",
    "theatre-studies-9609": "Theatre Studies (9609)",
    "travel-and-tourism-9395": "Travel and Tourism (9395)",
    "turkish-9681": "Turkish (9681)",
    "urdu-9676": "Urdu (9676)",
    "us-history-8041": "US History (8041)",
    "media-studies-9607": "Media Studies (9607)",
    "it-9626": "Information Technology (9626)",
    "marine-science-9695": "Marine Science (9695)",
    "chinese-language-literature-9868": "Chinese Language & Literature (9868)",
    "global-perspectives-and-research-9239": "Global Perspectives and Research (9239)",
    "history-9489": "History (9489)",
    "information-technology-9626": "Information Technology (9626)",
    "law-9084": "Law (9084)",
    "english-literature-9695": "Literature in English (9695)",
    "marine-science-9695": "Marine Science (9695)"
}


    exam_sessions = [
        "2024-oct-nov"
    ]
    
    base_url = "https://pastpapers.papacambridge.com/papers/caie/as-and-a-level-{subject}-{session}/"
    
    # Generate URLs for all combinations
    urls = {}
    for subject_code, subject_name in subjects.items():
        subject_urls = []
        for session in exam_sessions:
            url = base_url.format(subject=subject_code, session=session)
            subject_urls.append((url, subject_name))
        urls[subject_code] = subject_urls
    
    return urls

def download_question_papers(url, qp_folder, ms_folder):
    # Add headers to mimic browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Send a GET request to the webpage with headers
    try:
        response = requests.get(url, headers=headers)
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Create directories to save papers if they don't exist
        os.makedirs(qp_folder, exist_ok=True)
        os.makedirs(ms_folder, exist_ok=True)
        
        # Find all links
        download_links = soup.find_all('a', href=True)
        
        # Counter for downloaded papers
        papers_downloaded = 0
        
        # Filter and download question papers
        for link in download_links:
            href = link['href']
            
            # Check if the link is related to the download script (download_file.php)
            if "download_file.php?files=" in href:
                # Construct the correct download URL
                full_url = urllib.parse.urljoin(url, href)
                
                # Extract the real file URL (the one that starts with "https://")
                file_url = href.split("files=")[-1]
                
                # Check if file_url contains a .pdf (to ensure it's a valid PDF link)
                if file_url.lower().endswith('.pdf'):
                    # Determine if it's a question paper or marking scheme
                    if 'ms' in file_url.lower():
                        # Marking Scheme file
                        filename = os.path.join(ms_folder, os.path.basename(file_url))
                    else:
                        # Question Paper file
                        filename = os.path.join(qp_folder, os.path.basename(file_url))
                    
                    # Download the file
                    try:
                        # Directly request the PDF file with the correct URL
                        paper_response = requests.get(file_url, headers=headers, allow_redirects=True)
                        
                        # Check if response is successful
                        if paper_response.status_code == 200:
                            with open(filename, 'wb') as file:
                                file.write(paper_response.content)
                            print(f"Downloaded: {filename}")
                            papers_downloaded += 1
                            
                            # Check if the file contains "in", "qp", or "ms" before deleting it
                            if not any(substring in filename.lower() for substring in ['in', 'qp', 'ms']):
                                os.remove(filename)  # Delete file if condition is met
                                print(f"Deleted file: {filename}")
                        else:
                            print(f"Failed to download {file_url}. Status code: {paper_response.status_code}")
                    except Exception as e:
                        print(f"Error downloading {file_url}: {e}")
        
        print(f"Total papers downloaded: {papers_downloaded}")
    
    except requests.RequestException as e:
        print(f"Error accessing URL {url}: {e}")

def main():
    # Generate URLs for all subjects
    subject_urls = generate_igcse_urls()
    
    # Base directory for downloads
    base_download_dir = 'downloaded_papers'
    os.makedirs(base_download_dir, exist_ok=True)
    
    # Download papers for each subject and session
    for subject_code, urls in subject_urls.items():
        for url, subject_name in urls:
            print(f"\nDownloading papers for {subject_name}:")
            # Create subject-specific folders for QP and MS
            qp_folder = os.path.join(base_download_dir, f"{subject_name}")
            ms_folder = os.path.join(base_download_dir, f"{subject_name} Marking Scheme")
            
            print(f"Checking URL: {url}")
            download_question_papers(url, qp_folder, ms_folder)

if __name__ == "__main__":
    main()
