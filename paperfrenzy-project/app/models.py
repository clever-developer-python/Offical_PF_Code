#models.py

from django.db import models

# Create your models here.

class papers(models.Model):
    subject = models.CharField(max_length=70,blank=True,null=True)
    file = models.FileField(blank=True, null=True,upload_to='uploads/')
    year = models.CharField(max_length=10, blank=True,null=True)
    sets = models.CharField(max_length=50, blank=True, null=True)
    grade = models.IntegerField(blank=True, null=True)

    def __str__(self):
        parts = []
        if self.subject:
            parts.append(self.subject)
        if self.year:
            parts.append(self.year)
        if self.grade is not None:
            parts.append(f"Grade {self.grade}")
        
        if parts:
            return " - ".join(parts)
        else:
            return f"Paper {self.id}"


class markscheme(models.Model):
    subject = models.CharField(max_length=70,blank=True,null=True)
    file = models.FileField(blank=True, null=True,upload_to='uploads/')
    year = models.CharField(max_length=10, blank=True,null=True)
    sets = models.CharField(max_length=50, blank=True, null=True)
    grade = models.IntegerField(blank=True, null=True)
    
    def __str__(self):
        parts = []
        if self.subject:
            parts.append(self.subject)
        if self.year:
            parts.append(self.year)
        if self.grade is not None:
            parts.append(f"Grade {self.grade}")
        
        if parts:
            return " - ".join(parts)
        else:
            return f"Marking scheme {self.id}"


class feedbacks(models.Model):
    Email = models.CharField(max_length=100)
    Feedback = models.TextField(max_length=300)

from django.db import models

# Create your models here.

class NEETpapers(models.Model):
    subject = models.CharField(max_length=70,blank=True,null=True)
    file = models.FileField(blank=True, null=True,upload_to='uploads/')
    year = models.CharField(max_length=10, blank=True,null=True)
    sets = models.CharField(max_length=50, blank=True, null=True)
    grade = models.IntegerField(blank=True, null=True)

    def __str__(self):
        parts = []
        if self.subject:
            parts.append(self.subject)
        if self.year:
            parts.append(self.year)
        if self.grade is not None:
            parts.append(f"Grade {self.grade}")
        
        if parts:
            return " - ".join(parts)
        else:
            return f"Paper {self.id}"


class NEETmarkscheme(models.Model):
    subject = models.CharField(max_length=70,blank=True,null=True)
    file = models.FileField(blank=True, null=True,upload_to='uploads/')
    year = models.CharField(max_length=10, blank=True,null=True)
    sets = models.CharField(max_length=50, blank=True, null=True)
    grade = models.IntegerField(blank=True, null=True)
    
    def __str__(self):
        parts = []
        if self.subject:
            parts.append(self.subject)
        if self.year:
            parts.append(self.year)
        if self.grade is not None:
            parts.append(f"Grade {self.grade}")
        
        if parts:
            return " - ".join(parts)
        else:
            return f"Marking scheme {self.id}"
        

class SamplePapers10(models.Model):
    subject = models.CharField(max_length=70, blank=True, null=True)
    file = models.FileField(blank=True, null=True, upload_to='uploads/')
    year = models.CharField(max_length=10, blank=True, null=True)
    sets = models.CharField(max_length=50, blank=True, null=True)
    grade = models.IntegerField(blank=True, null=True)

    def __str__(self):
        parts = []
        if self.subject:
            parts.append(self.subject)
        if self.year:
            parts.append(self.year)
        if self.grade is not None:
            parts.append(f"Grade {self.grade}")
        
        if parts:
            return " - ".join(parts)
        else:
            return f"Sample Paper {self.id}"
        

class class10samplemarkscheme(models.Model):
    subject = models.CharField(max_length=70,blank=True,null=True)
    file = models.FileField(blank=True, null=True,upload_to='uploads/')
    year = models.CharField(max_length=10, blank=True,null=True)
    sets = models.CharField(max_length=50, blank=True, null=True)
    grade = models.IntegerField(blank=True, null=True)
    
    def __str__(self):
        parts = []
        if self.subject:
            parts.append(self.subject)
        if self.year:
            parts.append(self.year)
        if self.grade is not None:
            parts.append(f"Grade {self.grade}")
        
        if parts:
            return " - ".join(parts)
        else:
            return f"Marking scheme {self.id}"
        
from django.db import models

class IGCSE(models.Model):
    subject = models.CharField(max_length=70, blank=True, null=True)
    file = models.FileField(blank=True, null=True, upload_to='uploads/')
    year = models.CharField(max_length=50, blank=True, null=True, default="2024 May/June")
    sets = models.CharField(max_length=50, blank=True, null=True)
    grade = models.IntegerField(blank=True, null=True, default=14)

    def save(self, *args, **kwargs):
        # Automatically set the grade to 14 for IGCSE
        if self.grade is None:
            self.grade = 14
        
        # Automatically set the year to "2024 May/June"
        if not self.year:
            self.year = "2024 may/june"
       
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.subject} - {self.year} - {self.sets}"


class IGCSEMarkscheme(models.Model):
    subject = models.CharField(max_length=70, blank=True, null=True)
    file = models.FileField(blank=True, null=True, upload_to='uploads/')
    year = models.CharField(max_length=50, blank=True, null=True, default="2024 May/June")
    sets = models.CharField(max_length=50, blank=True, null=True)
    grade = models.IntegerField(blank=True, null=True, default=14)

    def save(self, *args, **kwargs):
        # Automatically set the grade to 14 for IGCSEMarkscheme
        if self.grade is None:
            self.grade = 14
        
        # Automatically set the year to "2024 May/June"
        if not self.year:
            self.year = "2024 May/June"
        
    
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.subject} - {self.year} - {self.sets}"


class IGCSEInsert(models.Model):
    subject = models.CharField(max_length=70, blank=True, null=True)
    file = models.FileField(blank=True, null=True, upload_to='uploads/')
    year = models.CharField(max_length=50, blank=True, null=True, default="2024 May/June")
    sets = models.CharField(max_length=50, blank=True, null=True)
    grade = models.IntegerField(blank=True, null=True, default=14)

    def save(self, *args, **kwargs):
        # Automatically set the grade to 14 for IGCSEInsert
        if self.grade is None:
            self.grade = 14
        
        # Automatically set the year to "2024 May/June"
        if not self.year:
            self.year = "2024 May/June"
        

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.subject} - {self.year} - {self.sets}"

