import os
import re
import django
import sys
import traceback
from pathlib import Path

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paperfrenzy.settings')
django.setup()

from django.core.files import File
from app.models import IGCSE, IGCSEMarkscheme, IGCSEInsert
from django.db import IntegrityError

def upload_papers_from_directories(directory_paths, year='2024 oct/nov'):
    overall_successful = []
    overall_failed = []

    for directory_path in directory_paths:
        if not os.path.isdir(directory_path):
            print(f"Skipping: {directory_path} is not a directory")
            continue

        # Remove 'Markscheme' or 'markscheme' from subject
        clean_subject = os.path.basename(directory_path).replace('Marking Scheme', '').replace('Marking Scheme', '')
        
        subject = clean_subject
        successful_uploads = []
        failed_uploads = []

        for filename in os.listdir(directory_path):
            # Skip files that don't have 'qp', 'ms', or 'in' in the name
            if 'qp' not in filename.lower() and 'ms' not in filename.lower() and 'in' not in filename.lower():
                continue
            
            file_path = os.path.join(directory_path, filename)
            
            if os.path.isdir(file_path):
                continue
            
            try:
                # Debug print
                print(f"Processing file: {filename}")
                
                with open(file_path, 'rb') as file:
                    # Handling question papers (qp)
                    if 'qp' in filename.lower():
                        # Extract set from filename
                        match = re.search(r'qp_(\d+)', filename)
                        sets = f"Paper {match.group(1)}" if match else ''
                        
                        print(f"Question Paper Details:")
                        print(f"Subject: {subject}")
                        print(f"Filename: {filename}")
                        print(f"Sets: {sets}")
                        
                        paper = IGCSE(
                            subject=subject,
                            file=File(file, name=filename),
                            year=year,
                            sets=sets,
                            grade=15
                        )
                        
                        try:
                            paper.full_clean()
                            paper.save()
                            print("Question paper saved successfully")
                            successful_uploads.append(filename)
                        except Exception as validation_error:
                            print(f"Question Paper Error: {validation_error}")
                            print(traceback.format_exc())
                            failed_uploads.append((filename, str(validation_error)))
                    
                    # Handling mark schemes (ms)
                    elif 'ms' in filename.lower():
                        # Remove 'markscheme' from name and clean subject
                        ms_subject = subject.replace(' Marking Scheme', '').strip()
                        clean_filename = filename.replace('markscheme', '').replace('Markscheme', '')
                        
                        # Extract set from filename
                        match = re.search(r'ms_(\d+)', clean_filename)
                        sets = f"Paper {match.group(1)}" if match else ''
                        
                        # Verbose debugging for mark schemes
                        print(f"Mark Scheme Details:")
                        print(f"Subject: {ms_subject}")
                        print(f"Filename: {clean_filename}")
                        print(f"Sets: {sets}")
                        print(f"Year: {year}")
                        
                        # Try reopening the file as it may have been closed
                        with open(file_path, 'rb') as ms_file:
                            mark_scheme = IGCSEMarkscheme(
                                subject=ms_subject,
                                file=File(ms_file, name=clean_filename),
                                year=year,
                                sets=sets
                            )
                            
                            try:
                                mark_scheme.full_clean()  # Validate model before saving
                                mark_scheme.save()
                                print("Mark scheme saved successfully")
                                successful_uploads.append(filename)
                            except Exception as validation_error:
                                print(f"Mark Scheme Error: {validation_error}")
                                print(traceback.format_exc())
                                failed_uploads.append((filename, str(validation_error)))
                    
                    # Handling insert papers (in)
                    elif 'in' in filename.lower():
                        # Extract set from filename
                        match = re.search(r'in_(\d+)', filename)
                        sets = f"Paper {match.group(1)}" if match else ''
                        
                        print(f"Insert Paper Details:")
                        print(f"Subject: {subject}")
                        print(f"Filename: {filename}")
                        print(f"Sets: {sets}")
                        
                        insert_paper = IGCSEInsert(
                            subject=subject,
                            file=File(file, name=filename),
                            year=year,
                            sets=sets
                        )
                        
                        try:
                            insert_paper.full_clean()
                            insert_paper.save()
                            print("Insert paper saved successfully")
                            successful_uploads.append(filename)
                        except Exception as validation_error:
                            print(f"Insert Paper Error: {validation_error}")
                            print(traceback.format_exc())
                            failed_uploads.append((filename, str(validation_error)))
                
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                print(traceback.format_exc())
                failed_uploads.append((filename, str(e)))
        
        print(f"Upload Summary for {subject}:")
        print(f"Successful uploads: {len(successful_uploads)}")
        print(f"Failed uploads: {len(failed_uploads)}")
        
        overall_successful.extend(successful_uploads)
        overall_failed.extend(failed_uploads)

    print("\nOverall Summary:")
    print(f"Total successful uploads: {len(overall_successful)}")
    print(f"Total failed uploads: {len(overall_failed)}")
    
    if overall_failed:
        print("\nFailed Files:")
        for file, error in overall_failed:
            print(f"{file}: {error}")
    
    return overall_successful, overall_failed
if __name__ == "__main__":
    upload_papers_from_directories([

    #markschemes
"/Users/kavan/Desktop/pdf-gen/downloaded_papers/Accounting (9706) Marking Scheme",
"/Users/kavan/Desktop/pdf-gen/downloaded_papers/Art and Design (9704) Marking Scheme",
"/Users/kavan/Desktop/pdf-gen/downloaded_papers/Biology (9700) Marking Scheme",
"/Users/kavan/Desktop/pdf-gen/downloaded_papers/Business (9609) Marking Scheme",
"/Users/kavan/Desktop/pdf-gen/downloaded_papers/Chemistry (9701) Marking Scheme",
"/Users/kavan/Desktop/pdf-gen/downloaded_papers/Chinese Language (9715) Marking Scheme",
"/Users/kavan/Desktop/pdf-gen/downloaded_papers/Classical Civilisation (9763) Marking Scheme",
"/Users/kavan/Desktop/pdf-gen/downloaded_papers/Computer Science (9608) Marking Scheme",
"/Users/kavan/Desktop/pdf-gen/downloaded_papers/Economics (9708) Marking Scheme",
"/Users/kavan/Desktop/pdf-gen/downloaded_papers/English Language (9093) Marking Scheme",
"/Users/kavan/Desktop/pdf-gen/downloaded_papers/English Literature (9695) Marking Scheme",
"/Users/kavan/Desktop/pdf-gen/downloaded_papers/Environmental Management (8291) Marking Scheme",
"/Users/kavan/Desktop/pdf-gen/downloaded_papers/French (9716) Marking Scheme",
"/Users/kavan/Desktop/pdf-gen/downloaded_papers/Geography (9696) Marking Scheme",
"/Users/kavan/Desktop/pdf-gen/downloaded_papers/German (9711) Marking Scheme",
"/Users/kavan/Desktop/pdf-gen/downloaded_papers/Global Perspectives and Research (9239) Marking Scheme",
"/Users/kavan/Desktop/pdf-gen/downloaded_papers/History (9389) Marking Scheme",
"/Users/kavan/Desktop/pdf-gen/downloaded_papers/Information Technology (9608) Marking Scheme",
"/Users/kavan/Desktop/pdf-gen/downloaded_papers/Law (9084) Marking Scheme",
"/Users/kavan/Desktop/pdf-gen/downloaded_papers/Literature in English (9695) Marking Scheme",
"/Users/kavan/Desktop/pdf-gen/downloaded_papers/Marine Science (9695) Marking Scheme",
"/Users/kavan/Desktop/pdf-gen/downloaded_papers/Mathematics (9709) Marking Scheme",
"/Users/kavan/Desktop/pdf-gen/downloaded_papers/Further Mathematics (9709) Marking Scheme",
"/Users/kavan/Desktop/pdf-gen/downloaded_papers/Music (9703) Marking Scheme",
"/Users/kavan/Desktop/pdf-gen/downloaded_papers/Philosophy (9694) Marking Scheme",
"/Users/kavan/Desktop/pdf-gen/downloaded_papers/Physical Education (9396) Marking Scheme",
"/Users/kavan/Desktop/pdf-gen/downloaded_papers/Physics (9702) Marking Scheme",
"/Users/kavan/Desktop/pdf-gen/downloaded_papers/Psychology (9698) Marking Scheme",
"/Users/kavan/Desktop/pdf-gen/downloaded_papers/Religious Studies (9084) Marking Scheme",
"/Users/kavan/Desktop/pdf-gen/downloaded_papers/Sociology (9699) Marking Scheme",
"/Users/kavan/Desktop/pdf-gen/downloaded_papers/Spanish (9715) Marking Scheme",
"/Users/kavan/Desktop/pdf-gen/downloaded_papers/Theatre Studies (9609) Marking Scheme",
"/Users/kavan/Desktop/pdf-gen/downloaded_papers/Travel and Tourism (9395) Marking Scheme",
"/Users/kavan/Desktop/pdf-gen/downloaded_papers/Turkish (9681) Marking Scheme",
"/Users/kavan/Desktop/pdf-gen/downloaded_papers/Urdu (9676) Marking Scheme",
"/Users/kavan/Desktop/pdf-gen/downloaded_papers/US History (8041) Marking Scheme",
"/Users/kavan/Desktop/pdf-gen/downloaded_papers/Media Studies (9607) Marking Scheme",
"/Users/kavan/Desktop/pdf-gen/downloaded_papers/Information Technology (9626) Marking Scheme",
"/Users/kavan/Desktop/pdf-gen/downloaded_papers/Chinese Language & Literature (9868) Marking Scheme",
"/Users/kavan/Desktop/pdf-gen/downloaded_papers/Global Perspectives and Research (9239) Marking Scheme",
"/Users/kavan/Desktop/pdf-gen/downloaded_papers/History (9389) Marking Scheme",
"/Users/kavan/Desktop/pdf-gen/downloaded_papers/Information Technology (9626) Marking Scheme",
"/Users/kavan/Desktop/pdf-gen/downloaded_papers/Law (9084) Marking Scheme",
"/Users/kavan/Desktop/pdf-gen/downloaded_papers/Literature in English (9695) Marking Scheme",
"/Users/kavan/Desktop/pdf-gen/downloaded_papers/Marine Science (9695) Marking Scheme"

    ], year='2024 oct/nov')
