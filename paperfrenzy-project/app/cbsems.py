#cbsems.py - CBSE Mark Scheme Auto Upload Program

import os
import re
import django
import sys
import traceback
import shutil
import PyPDF2
from pathlib import Path
import logging
from difflib import SequenceMatcher
import fitz  # PyMuPDF
import google.generativeai as genai

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configure Google Gemini API
API_KEY = "AIzaSyCp4IpVzRAkibC_M7jzVk3iW8mrldIS94M"
genai.configure(api_key=API_KEY)

# Set up Django environment
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paperfrenzy.settings')
django.setup()

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.files import File
from app.models import papers, markscheme

# Define paths
MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT', os.path.join(settings.BASE_DIR, 'media'))
UPLOADS_DIR = os.path.join(MEDIA_ROOT, 'uploads')

# Ensure uploads directory exists
os.makedirs(UPLOADS_DIR, exist_ok=True)

def count_pdf_pages(pdf_path):
    """Count the number of pages in a PDF file."""
    try:
        doc = fitz.open(pdf_path)
        return doc.page_count
    except Exception as e:
        logger.error(f"Error counting pages in {pdf_path}: {e}")
        try:
            # Fallback to PyPDF2
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                return len(reader.pages)
        except Exception as e2:
            logger.error(f"PyPDF2 also failed: {e2}")
            return 0

def find_pdf_files(directory):
    """Recursively find all PDF files in a directory and its subdirectories."""
    pdf_files = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(root, file))
                
    return pdf_files

def normalize_name(name):
    """Replace spaces with underscores in names."""
    return name.replace(' ', '_')

def sanitize_filename(filename):
    """Remove file extension and sanitize filename for use as a paper set."""
    # Remove file extension
    name_without_ext = os.path.splitext(filename)[0]
    
    # Replace spaces with underscores
    sanitized = name_without_ext.replace(' ', '_')
    
    # Remove any problematic characters
    sanitized = re.sub(r'[^\w\-_]', '', sanitized)
    
    return sanitized

def validate_mapping_with_ai(mapping_data):
    """Use Gemini to validate the mapping between mark schemes and papers."""
    if not mapping_data:
        return "No mappings to validate."
    
    # Format the mapping data for easier review
    formatted_data = "Mark Scheme Mappings:\n\n"
    for item in mapping_data:
        formatted_data += f"- {item}\n"
    
    prompt = f"""
    Please review these mark scheme to paper mappings for a CBSE (Central Board of Secondary Education) system.
    
    {formatted_data}
    
    Analyze the mappings and identify any potential issues:
    1. Are there any obvious mismatches between subjects?
    2. Are filenames correctly mapped to appropriate papers?
    3. Are there any patterns of errors or inconsistencies?
    4. What improvements would you suggest?
    
    Provide a detailed analysis of the quality of these mappings and specific recommendations for improvement.
    """
    
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Error using Gemini API: {e}")
        return f"Could not validate mappings with AI due to error: {str(e)}"

def load_papers_from_report(report_path="renamed_papers_report.txt"):
    """Load papers from the renamed_papers_report.txt file."""
    papers_by_subject = {}
    try:
        with open(report_path, "r") as f:
            current_subject = None
            for line in f:
                line = line.strip()
                if not line:
                    continue
                    
                if line.endswith(':'):
                    # This is a subject line
                    current_subject = line[:-1]  # Remove the colon
                    papers_by_subject[current_subject] = []
                elif line.startswith('* '):
                    # This is a paper entry
                    paper_name = line[2:]  # Remove the "* " prefix
                    if current_subject:
                        papers_by_subject[current_subject].append(paper_name)

        logger.info(f"Loaded papers from {report_path}: {len(papers_by_subject)} subjects found")
    except Exception as e:
        logger.error(f"Error loading paper report from {report_path}: {e}")
        papers_by_subject = {}
    
    return papers_by_subject

def process_mark_schemes(ms_directory, year='2024comp', grade=10):
    """Process all mark schemes in the directory and link them to papers."""
    
    successful_uploads = []
    failed_uploads = []
    
    # For logging mappings
    mapping_log = []
    
    # Check base directory exists
    if not os.path.isdir(ms_directory):
        logger.error(f"Error: {ms_directory} does not exist")
        alt_path = os.path.join(os.getcwd(), ms_directory)
        if os.path.isdir(alt_path):
            ms_directory = alt_path
        else:
            logger.error("Mark scheme directory not found")
            return [], [], []
    
    # First, get all available papers from the database to check for existing entries
    all_papers = list(papers.objects.all())
    existing_paper_subjects = {paper.subject for paper in all_papers}
    logger.info(f"Found {len(existing_paper_subjects)} unique paper subjects in database")
    
    # Load papers from renamed_papers_report.txt
    papers_by_subject = load_papers_from_report()
    
    # Process each subject directory
    for subject_dir in os.listdir(ms_directory):
        subject_path = os.path.join(ms_directory, subject_dir)
        
        # Skip if not a directory
        if not os.path.isdir(subject_path):
            continue
            
        # Use the directory name as the subject - replace underscores with spaces for display
        display_subject = subject_dir.replace('_', ' ')
        normalized_subject = normalize_name(display_subject)
        
        logger.info(f"\nProcessing mark schemes for subject: {display_subject}")
        
        # Find all PDF files in the subject directory and subdirectories
        pdf_files = find_pdf_files(subject_path)
        
        if not pdf_files:
            logger.warning(f"Warning: No PDF files found in {subject_path}")
            continue
            
        logger.info(f"Found {len(pdf_files)} PDF files for processing")
        
        # Find matching subject in our papers list
        matching_subject = None
        for report_subject in papers_by_subject:
            # Normalize both for comparison
            if normalize_name(report_subject).lower() == normalized_subject.lower():
                matching_subject = report_subject
                break
                
        if matching_subject:
            logger.info(f"Found matching subject in report: {matching_subject} with {len(papers_by_subject[matching_subject])} papers")
        
        # Process each mark scheme file
        for file_path in pdf_files:
            filename = os.path.basename(file_path)
            
            try:
                logger.info(f"Processing mark scheme: {filename}")
                
                # Use the filename (without extension) as the paper set
                paper_set = sanitize_filename(filename)
                logger.info(f"Using paper set: {paper_set}")
                
                # Check if this is an "allms" file
                if "allms" in paper_set.lower():
                    # This is a mark scheme for all papers in this subject
                    logger.info(f"Found 'allms' mark scheme for {display_subject}")
                    
                    if matching_subject and papers_by_subject[matching_subject]:
                        # Found papers for this subject
                        papers_list = papers_by_subject[matching_subject]
                        logger.info(f"Found {len(papers_list)} papers to link to this mark scheme")
                        
                        # Process mark scheme once
                        dest_filename = f"MS_{normalized_subject}_{paper_set}.pdf"
                        dest_path = os.path.join(UPLOADS_DIR, dest_filename)
                        shutil.copy2(file_path, dest_path)
                        logger.info(f"Copied to {dest_path}")
                        
                        # Create mark scheme entries for each paper
                        for paper_filename in papers_list:
                            paper_set_name = sanitize_filename(paper_filename)
                            try:
                                # Create or update mark scheme entry
                                existing = markscheme.objects.filter(
                                    subject=normalized_subject,
                                    year=year,
                                    sets=paper_set_name,
                                    grade=grade
                                ).first()
                                
                                with open(dest_path, 'rb') as file:
                                    if existing:
                                        mark_scheme = existing
                                        logger.info(f"Mark scheme already exists for {paper_set_name}, updating")
                                    else:
                                        mark_scheme = markscheme(
                                            subject=normalized_subject,
                                            year=year,
                                            sets=paper_set_name,
                                            grade=grade
                                        )
                                    
                                    mark_scheme.save()
                                    django_file = File(file, name=dest_filename)
                                    mark_scheme.file = django_file
                                    mark_scheme.save()
                                
                                mapping_log.append(f"{normalized_subject} - {paper_set_name} ---> {subject_dir} -- {filename} (allms)")
                                successful_uploads.append(f"{paper_filename} (via allms)")
                                
                            except Exception as e:
                                logger.error(f"Error linking allms to {paper_filename}: {e}")
                                failed_uploads.append((paper_filename, f"allms linking error: {str(e)}"))
                    else:
                        logger.warning(f"No matching papers found for subject {display_subject} in renamed_papers_report.txt")
                        failed_uploads.append((filename, "No matching papers found in report"))
                else:
                    # Standard mark scheme - create mark scheme entry in database
                    try:
                        # Check if this mark scheme already exists
                        existing = markscheme.objects.filter(
                            subject=normalized_subject,
                            year=year,
                            sets=paper_set,
                            grade=grade
                        ).first()
                        
                        # Copy file to uploads directory
                        dest_filename = f"MS_{normalized_subject}_{paper_set}.pdf"
                        dest_path = os.path.join(UPLOADS_DIR, dest_filename)
                        shutil.copy2(file_path, dest_path)
                        logger.info(f"Copied to {dest_path}")
                        
                        with open(dest_path, 'rb') as file:
                            if existing:
                                logger.info(f"Mark scheme already exists for {paper_set}, updating")
                                mark_scheme = existing
                            else:
                                mark_scheme = markscheme(
                                    subject=normalized_subject,
                                    year=year,
                                    sets=paper_set,
                                    grade=grade
                                )
                            
                            # Save first to get an ID
                            mark_scheme.save()
                            
                            # Attach the file
                            django_file = File(file, name=dest_filename)
                            mark_scheme.file = django_file
                            mark_scheme.save()
                            
                            logger.info(f"Successfully uploaded mark scheme for {paper_set}")
                            mapping_log.append(f"{normalized_subject} - {paper_set} ---> {subject_dir} -- {filename}")
                            successful_uploads.append(filename)
                            
                    except Exception as e:
                        logger.error(f"Error creating mark scheme entry: {e}")
                        logger.error(traceback.format_exc())
                        failed_uploads.append((filename, str(e)))
                        
            except Exception as e:
                logger.error(f"Error processing {filename}: {e}")
                logger.error(traceback.format_exc())
                failed_uploads.append((filename, str(e)))
    
    # Write mapping log to file
    try:
        with open("mark_scheme_mappings.txt", "w") as f:
            f.write("MARK SCHEME MAPPING LOG\n")
            f.write("======================\n\n")
            for mapping in mapping_log:
                f.write(mapping + "\n")
            f.write("\n\nSummary:\n")
            f.write(f"Total successful mappings: {len(mapping_log)}\n")
            f.write(f"Total successful uploads: {len(successful_uploads)}\n")
            f.write(f"Total failed uploads: {len(failed_uploads)}\n")
        logger.info("Mapping log saved to mark_scheme_mappings.txt")
    except Exception as e:
        logger.error(f"Error writing mapping log: {e}")
    
    # Check mappings with AI
    try:
        ai_analysis = validate_mapping_with_ai(mapping_log)
        with open("ai_mapping_analysis.txt", "w") as f:
            f.write("AI ANALYSIS OF MARK SCHEME MAPPINGS\n")
            f.write("=================================\n\n")
            f.write(ai_analysis)
        logger.info("AI analysis saved to ai_mapping_analysis.txt")
    except Exception as e:
        logger.error(f"Error generating AI analysis: {e}")
    
    # Print summary
    logger.info("\nMark Scheme Upload Summary:")
    logger.info(f"Total successful uploads: {len(successful_uploads)}")
    logger.info(f"Total failed uploads: {len(failed_uploads)}")
    
    if failed_uploads:
        logger.info("\nFailed Files:")
        for file, error in failed_uploads:
            logger.info(f"{file}: {error}")
    
    return successful_uploads, failed_uploads, mapping_log

def verify_mark_scheme_links():
    """Verify that uploaded mark schemes are correctly linked to papers."""
    logger.info("\nVerifying mark scheme to paper links...")
    
    # Get all papers
    all_papers = papers.objects.all()
    paper_sets = {f"{p.subject}_{p.sets}": p for p in all_papers}
    
    # Get all mark schemes
    all_schemes = markscheme.objects.all()
    
    linked_count = 0
    unlinked_count = 0
    
    for scheme in all_schemes:
        paper_key = f"{scheme.subject}_{scheme.sets}"
        if paper_key in paper_sets:
            linked_count += 1
        else:
            unlinked_count += 1
            logger.warning(f"No matching paper found for mark scheme: Subject={scheme.subject}, Sets={scheme.sets}")
    
    logger.info(f"Mark schemes with matching papers: {linked_count}")
    logger.info(f"Mark schemes without matching papers: {unlinked_count}")
    
    return linked_count, unlinked_count

def check_directory_structure(ms_directory):
    """Check and print the directory structure to help diagnose issues."""
    logger.info("\nChecking directory structure:")
    
    if not os.path.exists(ms_directory):
        logger.error(f"Main directory not found: {ms_directory}")
        return
        
    logger.info(f"Main directory exists: {ms_directory}")
    
    # Check subdirectories
    subjects = []
    total_pdfs = 0
    
    for item in os.listdir(ms_directory):
        item_path = os.path.join(ms_directory, item)
        if os.path.isdir(item_path):
            subjects.append(item)
            
            # Count PDFs in this subject directory (including subdirectories)
            pdfs = find_pdf_files(item_path)
            pdf_count = len(pdfs)
            total_pdfs += pdf_count
            
            logger.info(f"Subject directory: {item} - Contains {pdf_count} PDF files")
            
            # List some PDFs if found
            if pdf_count > 0:
                logger.info("  PDF examples:")
                for pdf in pdfs[:3]:  # Show up to 3 examples
                    logger.info(f"  - {os.path.basename(pdf)}")
    
    logger.info(f"\nFound {len(subjects)} subject directories with {total_pdfs} total PDF files")
    
    if total_pdfs == 0:
        logger.warning("\nNo PDF files found! Please check that your directory structure is correct.")
        logger.info("Expected structure: cbse_ms/Subject_Name/mark_scheme_file.pdf or in subdirectories")

def analyze_paper_mark_scheme_coverage():
    """Analyze how many papers have mark schemes and vice versa."""
    all_papers = papers.objects.all()
    all_schemes = markscheme.objects.all()
    
    # Create lookup dictionaries
    papers_by_key = {f"{p.subject}_{p.sets}": p for p in all_papers}
    schemes_by_key = {f"{ms.subject}_{ms.sets}": ms for ms in all_schemes}
    
    # Find papers without mark schemes
    papers_without_ms = []
    for key, paper in papers_by_key.items():
        if key not in schemes_by_key:
            papers_without_ms.append(f"{paper.subject} - {paper.sets}")
    
    # Find mark schemes without papers
    ms_without_papers = []
    for key, scheme in schemes_by_key.items():
        if key not in papers_by_key:
            ms_without_papers.append(f"{scheme.subject} - {scheme.sets}")
    
    # Write analysis to file
    try:
        with open("paper_markscheme_coverage.txt", "w") as f:
            f.write("PAPER AND MARK SCHEME COVERAGE ANALYSIS\n")
            f.write("=====================================\n\n")
            
            f.write(f"Total papers: {len(all_papers)}\n")
            f.write(f"Total mark schemes: {len(all_schemes)}\n")
            f.write(f"Papers without mark schemes: {len(papers_without_ms)}\n")
            f.write(f"Mark schemes without papers: {len(ms_without_papers)}\n\n")
            
            if papers_without_ms:
                f.write("PAPERS WITHOUT MARK SCHEMES:\n")
                f.write("---------------------------\n")
                for p in papers_without_ms:
                    f.write(f"- {p}\n")
                f.write("\n")
            
            if ms_without_papers:
                f.write("MARK SCHEMES WITHOUT PAPERS:\n")
                f.write("---------------------------\n")
                for ms in ms_without_papers:
                    f.write(f"- {ms}\n")
        
        logger.info("Coverage analysis saved to paper_markscheme_coverage.txt")
    except Exception as e:
        logger.error(f"Error writing coverage analysis: {e}")
    
    return len(papers_without_ms), len(ms_without_papers)

def generate_final_report(successful_uploads, failed_uploads, mapping_log):
    """Generate a comprehensive final report."""
    try:
        with open("mark_scheme_upload_report.txt", "w") as f:
            f.write("CBSE MARK SCHEME UPLOAD FINAL REPORT\n")
            f.write("==================================\n\n")
            
            f.write("UPLOAD STATISTICS\n")
            f.write("----------------\n")
            f.write(f"Total mark schemes processed: {len(successful_uploads) + len(failed_uploads)}\n")
            f.write(f"Successfully uploaded: {len(successful_uploads)}\n")
            f.write(f"Failed uploads: {len(failed_uploads)}\n\n")
            
            # Count by subject
            subjects = {}
            for mapping in mapping_log:
                parts = mapping.split(" - ", 1)
                if len(parts) >= 1:
                    subject = parts[0]
                    if subject not in subjects:
                        subjects[subject] = 0
                    subjects[subject] += 1
            
            f.write("UPLOADS BY SUBJECT\n")
            f.write("----------------\n")
            for subject, count in sorted(subjects.items()):
                f.write(f"{subject}: {count}\n")
            
            if failed_uploads:
                f.write("\nFAILED UPLOADS\n")
                f.write("-------------\n")
                for file, error in failed_uploads:
                    f.write(f"{file}: {error}\n")
            
            f.write("\nSYSTEM RECOMMENDATIONS\n")
            f.write("--------------------\n")
            
            if len(successful_uploads) == 0:
                f.write("CRITICAL: No mark schemes were successfully uploaded. Check directory structure and file paths.\n")
            elif len(failed_uploads) > len(successful_uploads):
                f.write("WARNING: More failures than successes. Review error messages and fix file naming issues.\n")
            
            if len(subjects) < 5:
                f.write("WARNING: Very few subjects were processed. Ensure subject folders are correctly named.\n")
            
            # Read AI analysis if available
            try:
                with open("ai_mapping_analysis.txt", "r") as ai_file:
                    ai_content = ai_file.read()
                    f.write("\nAI ANALYSIS SUMMARY\n")
                    f.write("-----------------\n")
                    f.write(ai_content)
            except:
                pass
        
        logger.info("Final report generated at mark_scheme_upload_report.txt")
    except Exception as e:
        logger.error(f"Error generating final report: {e}")

if __name__ == "__main__":
    ms_directory = "cbse_ms"
    
    # Try different possible paths
    possible_ms_paths = [
        ms_directory,
        os.path.join(os.getcwd(), ms_directory),
        os.path.abspath(ms_directory),
        "paperfrenzy-project/app/cbse_ms"
    ]
    
    # Check if paths are provided as command line arguments
    if len(sys.argv) > 1:
        possible_ms_paths.insert(0, sys.argv[1])
    
    # Find valid paths
    found_ms_path = None
    
    for path in possible_ms_paths:
        if os.path.exists(path) and os.path.isdir(path):
            found_ms_path = path
            break
    
    if not found_ms_path:
        logger.error("Could not find valid path for mark schemes directory.")
        logger.info("Please specify path as command line argument:")
        logger.info("python cbsems.py /path/to/cbse_ms")
        sys.exit(1)
    
    logger.info(f"Using mark schemes directory: {found_ms_path}")
    
    # Check directory structure first to diagnose issues
    check_directory_structure(found_ms_path)
    
    # Process mark schemes - simpler approach: folder name = subject, filename = paper set
    successful_uploads, failed_uploads, mapping_log = process_mark_schemes(found_ms_path, year='2024comp', grade=10)
    
    # Verify mark scheme links to papers
    verify_mark_scheme_links()
    
    # Analyze paper and mark scheme coverage
    papers_without_ms, ms_without_papers = analyze_paper_mark_scheme_coverage()
    
    # Generate final report
    generate_final_report(successful_uploads, failed_uploads, mapping_log)