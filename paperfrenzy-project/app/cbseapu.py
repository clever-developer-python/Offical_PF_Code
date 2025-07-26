import os
import re
import django
import sys
import traceback
import shutil
from pathlib import Path

# Setup Django environment
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paperfrenzy.settings')
django.setup()

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.files import File
from app.models import papers, markscheme

# Define consistent media path - must match Django settings
MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT', os.path.join(settings.BASE_DIR, 'media'))
UPLOADS_DIR = os.path.join(MEDIA_ROOT, 'uploads')

# Ensure uploads directory exists
os.makedirs(UPLOADS_DIR, exist_ok=True)

# Create a local file system storage instance
local_storage = FileSystemStorage(location=MEDIA_ROOT)

def process_file(file_path, subject, year, grade):
    """
    Process a single file and save it to the database.
    
    Args:
        file_path: Path to the file
        subject: Subject name
        year: Year of the paper
        grade: Grade level
    
    Returns:
        (success, error_message) tuple
    """
    try:
        filename = os.path.basename(file_path)
        print(f"Processing file: {filename} for subject: {subject}")
        
        # Only process PDF files
        if not filename.lower().endswith('.pdf'):
            return False, "Not a PDF file"
        
        # Determine if this is a question paper or mark scheme
        is_markscheme = any(keyword in filename.lower() for keyword in 
                          ['ms', 'mark', 'scheme', 'solution', 'answer'])
        
        # The set field will be the paper name (without extension)
        paper_name = os.path.splitext(filename)[0]
        
        # Generate a subject-specific filename to avoid collisions between subjects
        subject_filename = f"{subject}_{filename}"
        dest_path = os.path.join(UPLOADS_DIR, subject_filename)
        
        print(f"Copying {filename} to {dest_path}")
        shutil.copy2(file_path, dest_path)
        
        # Open the file for Django to handle
        with open(dest_path, 'rb') as file:
            if is_markscheme:
                # Check if this mark scheme already exists
                existing = markscheme.objects.filter(
                    subject=subject,
                    year=year,
                    sets=paper_name,
                    grade=grade
                ).first()
                
                if existing:
                    print(f"Mark scheme already exists (ID: {existing.id}), replacing file")
                    mark_scheme = existing
                else:
                    # Create new mark scheme
                    mark_scheme = markscheme(
                        subject=subject,
                        year=year,
                        sets=paper_name,
                        grade=grade
                    )
                
                # Save first to get an ID if new
                mark_scheme.save()
                
                # Now attach the file - use subject-specific filename
                django_file = File(file, name=subject_filename)
                mark_scheme.file = django_file
                mark_scheme.save()
                
                return True, None
            else:
                # Check if this paper already exists
                existing = papers.objects.filter(
                    subject=subject,
                    year=year,
                    sets=paper_name,
                    grade=grade
                ).first()
                
                if existing:
                    print(f"Paper already exists (ID: {existing.id}), replacing file")
                    paper = existing
                else:
                    # Create new paper
                    paper = papers(
                        subject=subject,
                        year=year,
                        sets=paper_name,
                        grade=grade
                    )
                
                # Save first to get an ID if new
                paper.save()
                
                # Now attach the file - use subject-specific filename
                django_file = File(file, name=subject_filename)
                paper.file = django_file
                paper.save()
                
                return True, None
    
    except Exception as e:
        error_msg = f"Error processing {filename}: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        return False, error_msg

def upload_papers_from_directory(base_directory, year='2023', grade=10):
    """
    Uploads CBSE papers from a directory structure, with subject mapping.
    Checks for PDF files in the subject directory and immediate subdirectories.
    
    Args:
        base_directory: The base directory containing subject folders
        year: The year to assign to these papers
        grade: The grade level to assign to these papers
    """
    print(f"\n{'='*60}\nUploading papers from {base_directory}\n{'='*60}")
    
    # Validate the base directory
    if not os.path.isdir(base_directory):
        print(f"Error: {base_directory} is not a directory or doesn't exist")
        return [], []
    
    # Get all subject directories
    subject_dirs = [d for d in os.listdir(base_directory) 
                   if os.path.isdir(os.path.join(base_directory, d))]
    
    if not subject_dirs:
        print(f"No subject directories found in {base_directory}")
        return [], []
    
    print(f"Found {len(subject_dirs)} subject directories")
    
    overall_successful = []
    overall_failed = []
    
    # Process each subject directory
    for subject_dir in sorted(subject_dirs):
        subject_path = os.path.join(base_directory, subject_dir)
        subject = subject_dir  # Ensure subject name matches directory name
        
        print(f"\n{'*'*60}\nProcessing subject: {subject} at {subject_path}\n{'*'*60}")
        
        successful_uploads = []
        failed_uploads = []
        
        # Initialize list to store all PDF files for this subject
        subject_pdf_files = []
        
        # Get all PDF files in the subject directory (non-recursive)
        pdf_files = [f for f in os.listdir(subject_path) 
                    if os.path.isfile(os.path.join(subject_path, f)) and 
                    f.lower().endswith('.pdf')]
        
        # Add all PDF files from the main directory
        for pdf_file in pdf_files:
            subject_pdf_files.append(os.path.join(subject_path, pdf_file))
        
        # Check for immediate subdirectories and get their PDF files too
        for item in os.listdir(subject_path):
            item_path = os.path.join(subject_path, item)
            if os.path.isdir(item_path):
                print(f"Checking subdirectory: {item}")
                sub_pdfs = [f for f in os.listdir(item_path) 
                           if os.path.isfile(os.path.join(item_path, f)) and 
                           f.lower().endswith('.pdf')]
                
                if sub_pdfs:
                    print(f"Found {len(sub_pdfs)} PDF files in subdirectory {item}")
                    for pdf_file in sub_pdfs:
                        subject_pdf_files.append(os.path.join(item_path, pdf_file))
        
        if not subject_pdf_files:
            print(f"No PDF files found in {subject_path} or its immediate subdirectories")
        else:
            print(f"Found {len(subject_pdf_files)} total PDF files for subject {subject}")
            
            # Process each PDF file
            for file_path in sorted(subject_pdf_files):
                filename = os.path.basename(file_path)
                success, error_msg = process_file(file_path, subject, year, grade)
                
                if success:
                    successful_uploads.append(filename)
                else:
                    failed_uploads.append((filename, error_msg))
        
        # Report subject results
        print(f"Subject {subject} results:")
        print(f"Successful uploads: {len(successful_uploads)}")
        print(f"Failed uploads: {len(failed_uploads)}")
        
        # Add to overall results
        overall_successful.extend(successful_uploads)
        overall_failed.extend(failed_uploads)
    
    # Report overall results
    print(f"\nOverall Summary:")
    print(f"Total successful uploads: {len(overall_successful)}")
    print(f"Total failed uploads: {len(overall_failed)}")
    
    if overall_failed:
        print("\nFailed Files:")
        for file, error in overall_failed:
            print(f"{file}: {error}")
    
    return overall_successful, overall_failed

def upload_papers_recursively(base_directory, year='2023', grade=10):
    """
    Recursively uploads CBSE papers from a directory structure,
    preserving subject hierarchy.
    
    Args:
        base_directory: The base directory containing subject folders
        year: The year to assign to these papers
        grade: The grade level to assign to these papers
    """
    print(f"\n{'='*60}\nRecursively uploading papers from {base_directory}\n{'='*60}")
    
    # Validate the base directory
    if not os.path.isdir(base_directory):
        print(f"Error: {base_directory} is not a directory or doesn't exist")
        return [], []
    
    # Get all subject directories
    subject_dirs = [d for d in os.listdir(base_directory) 
                   if os.path.isdir(os.path.join(base_directory, d))]
    
    if not subject_dirs:
        print(f"No subject directories found in {base_directory}")
        return [], []
    
    print(f"Found {len(subject_dirs)} subject directories")
    
    overall_successful = []
    overall_failed = []
    
    # Process each subject directory
    for subject_dir in sorted(subject_dirs):
        subject_path = os.path.join(base_directory, subject_dir)
        subject = subject_dir  # The subject name is the directory name
        
        print(f"\n{'*'*60}\nProcessing subject: {subject} at {subject_path}\n{'*'*60}")
        
        successful_uploads = []
        failed_uploads = []
        
        # Use a list to keep track of all PDF files for this subject
        subject_pdf_files = []
        
        # Walk through the subject directory and collect all PDF files
        for root, dirs, files in os.walk(subject_path):
            pdf_files = [f for f in files if f.lower().endswith('.pdf')]
            if pdf_files:
                print(f"Found {len(pdf_files)} PDF files in {root}")
                for pdf_file in pdf_files:
                    subject_pdf_files.append((os.path.join(root, pdf_file), pdf_file))
        
        if not subject_pdf_files:
            print(f"No PDF files found for subject {subject}")
            continue
        
        print(f"Total PDF files for subject {subject}: {len(subject_pdf_files)}")
        
        # Process each PDF file
        for file_path, filename in subject_pdf_files:
            success, error_msg = process_file(file_path, subject, year, grade)
            
            if success:
                successful_uploads.append(filename)
            else:
                failed_uploads.append((filename, error_msg))
        
        # Report subject results
        print(f"Subject {subject} results:")
        print(f"Successful uploads: {len(successful_uploads)}")
        print(f"Failed uploads: {len(failed_uploads)}")
        
        # Add to overall results
        overall_successful.extend(successful_uploads)
        overall_failed.extend(failed_uploads)
    
    # Report overall results
    print(f"\nOverall Summary:")
    print(f"Total successful uploads: {len(overall_successful)}")
    print(f"Total failed uploads: {len(overall_failed)}")
    
    if overall_failed:
        print("\nFailed Files:")
        for file, error in overall_failed:
            print(f"{file}: {error}")
    
    return overall_successful, overall_failed

def verify_uploaded_files():
    """
    Verify that uploaded files are correctly referenced in the database
    """
    print("\nVerifying uploaded papers...")
    
    # Check question papers
    all_papers = papers.objects.all()
    print(f"Found {len(all_papers)} question papers in database")
    
    for paper in all_papers[:5]:  # Check first 5 papers
        print(f"Paper ID: {paper.id}")
        print(f"  Subject: {paper.subject}")
        print(f"  Year: {paper.year}")
        print(f"  Sets: {paper.sets}")
        print(f"  File name: {paper.file.name if paper.file else 'No file'}")
        
        # Check if file exists locally
        if paper.file and paper.file.name:
            local_path = os.path.join(MEDIA_ROOT, paper.file.name)
            print(f"  Local path: {local_path}")
            print(f"  File exists locally: {os.path.exists(local_path)}")
    
    # Check mark schemes
    all_schemes = markscheme.objects.all()
    print(f"\nFound {len(all_schemes)} mark schemes in database")
    
    for scheme in all_schemes[:5]:  # Check first 5 schemes
        print(f"Mark Scheme ID: {scheme.id}")
        print(f"  Subject: {scheme.subject}")
        print(f"  Year: {scheme.year}")
        print(f"  Sets: {scheme.sets}")
        print(f"  File name: {scheme.file.name if scheme.file else 'No file'}")
        
        # Check if file exists locally
        if scheme.file and scheme.file.name:
            local_path = os.path.join(MEDIA_ROOT, scheme.file.name)
            print(f"  Local path: {local_path}")
            print(f"  File exists locally: {os.path.exists(local_path)}")

def find_missing_files():
    """
    Find any files that are referenced in the database but don't exist locally.
    """
    print("\nChecking for missing files...")
    
    missing_papers = []
    missing_schemes = []
    
    # Check question papers
    all_papers = papers.objects.all()
    for paper in all_papers:
        if paper.file and paper.file.name:
            local_path = os.path.join(MEDIA_ROOT, paper.file.name)
            if not os.path.exists(local_path):
                missing_papers.append((paper.id, paper.subject, paper.sets, paper.file.name))
    
    # Check mark schemes
    all_schemes = markscheme.objects.all()
    for scheme in all_schemes:
        if scheme.file and scheme.file.name:
            local_path = os.path.join(MEDIA_ROOT, scheme.file.name)
            if not os.path.exists(local_path):
                missing_schemes.append((scheme.id, scheme.subject, scheme.sets, scheme.file.name))
    
    print(f"Found {len(missing_papers)} missing question papers")
    if missing_papers:
        print("Missing question papers:")
        for paper_id, subject, sets, filename in missing_papers[:10]:  # Show first 10
            print(f"  ID: {paper_id}, Subject: {subject}, Sets: {sets}, File: {filename}")
    
    print(f"Found {len(missing_schemes)} missing mark schemes")
    if missing_schemes:
        print("Missing mark schemes:")
        for scheme_id, subject, sets, filename in missing_schemes[:10]:  # Show first 10
            print(f"  ID: {scheme_id}, Subject: {subject}, Sets: {sets}, File: {filename}")
    
    return missing_papers, missing_schemes

def count_papers_by_subject():
    """
    Count how many papers and mark schemes are available for each subject.
    """
    print("\nCounting papers by subject...")
    
    subject_stats = {}
    
    # Count question papers
    for paper in papers.objects.all():
        if paper.subject not in subject_stats:
            subject_stats[paper.subject] = {'papers': 0, 'markschemes': 0}
        subject_stats[paper.subject]['papers'] += 1
    
    # Count mark schemes
    for scheme in markscheme.objects.all():
        if scheme.subject not in subject_stats:
            subject_stats[scheme.subject] = {'papers': 0, 'markschemes': 0}
        subject_stats[scheme.subject]['markschemes'] += 1
    
    # Display stats
    print("\nSubject Statistics:")
    print("-" * 60)
    print(f"{'Subject':<30} {'Question Papers':<15} {'Mark Schemes':<15}")
    print("-" * 60)
    
    for subject, counts in sorted(subject_stats.items()):
        print(f"{subject:<30} {counts['papers']:<15} {counts['markschemes']:<15}")
    
    print("-" * 60)
    total_papers = sum(stats['papers'] for stats in subject_stats.values())
    total_schemes = sum(stats['markschemes'] for stats in subject_stats.values())
    print(f"{'TOTAL':<30} {total_papers:<15} {total_schemes:<15}")
    
    return subject_stats

def clean_database_entries():
    """
    Fix any database entries where subject names might be incorrect.
    """
    print("\nChecking for inconsistent subject names in database...")
    
    # Get all unique subjects in the database
    paper_subjects = set(papers.objects.values_list('subject', flat=True).distinct())
    scheme_subjects = set(markscheme.objects.values_list('subject', flat=True).distinct())
    all_subjects = paper_subjects.union(scheme_subjects)
    
    print(f"Found {len(all_subjects)} unique subjects in database")
    print(f"Subjects: {', '.join(sorted(all_subjects))}")
    
    # Ask for confirmation before proceeding
    if input("\nWould you like to remove any incorrect subjects? (y/n): ").lower() == 'y':
        incorrect_subject = input("Enter the incorrect subject name to remove: ")
        
        if incorrect_subject in all_subjects:
            # Get all papers with this subject
            incorrect_papers = papers.objects.filter(subject=incorrect_subject)
            incorrect_schemes = markscheme.objects.filter(subject=incorrect_subject)
            
            print(f"Found {incorrect_papers.count()} papers and {incorrect_schemes.count()} "
                  f"mark schemes with subject '{incorrect_subject}'")
            
            if input(f"Delete all entries for subject '{incorrect_subject}'? (y/n): ").lower() == 'y':
                # Delete all entries for this subject
                incorrect_papers.delete()
                incorrect_schemes.delete()
                print(f"Deleted all entries for subject '{incorrect_subject}'")
        else:
            print(f"Subject '{incorrect_subject}' not found in database")

def main():
    """
    Main function to handle command line arguments and run the appropriate functions.
    """
    # Directory containing CBSE papers organized by subject
    default_dir = "cbse_papers"
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Upload CBSE papers to database')
    parser.add_argument('directory', nargs='?', default=default_dir,
                        help='Directory containing CBSE papers')
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='Process directories recursively')
    parser.add_argument('-y', '--year', default='2023',
                        help='Year for the papers')
    parser.add_argument('-g', '--grade', type=int, default=10,
                        help='Grade level for the papers')
    parser.add_argument('-v', '--verify', action='store_true',
                        help='Verify uploaded files')
    parser.add_argument('-c', '--clean', action='store_true',
                        help='Clean database entries')
    parser.add_argument('-s', '--stats', action='store_true',
                        help='Show subject statistics')
    args = parser.parse_args()
    
    # Check for the directory
    if not os.path.isdir(args.directory):
        print(f"Directory not found: {args.directory}")
        print("Checking alternative paths...")
        
        # Try different possible paths
        possible_paths = [
            args.directory,
            os.path.join(os.getcwd(), args.directory),
            os.path.abspath(args.directory),
            f"paperfrenzy-project/app/{args.directory}"
        ]
        
        found_path = None
        for path in possible_paths:
            if os.path.isdir(path):
                found_path = path
                print(f"Found directory at: {path}")
                break
        
        if found_path:
            args.directory = found_path
        else:
            print("Could not find a valid directory in any of the attempted locations.")
            print("Please specify the correct path to the CBSE papers directory.")
            return
    
    # Run requested operations
    if args.clean:
        clean_database_entries()
    
    if args.recursive:
        print("Running in recursive mode")
        upload_papers_recursively(args.directory, year=args.year, grade=args.grade)
    else:
        print("Running in non-recursive mode")
        upload_papers_from_directory(args.directory, year=args.year, grade=args.grade)
    
    if args.verify:
        verify_uploaded_files()
        find_missing_files()
    
    if args.stats:
        count_papers_by_subject()

if __name__ == "__main__":
    main()