# Generated by Django 5.0.4 on 2024-06-07 06:05

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('job_type', models.CharField(blank=True, choices=[('partTime', 'Part-Time'), ('fullTime', 'Full-Time')], max_length=50, null=True)),
                ('min_budget', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('max_budget', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('posted_by_user_id', models.IntegerField()),
                ('education', models.CharField(blank=True, choices=[('primary-education', 'Primary Education'), ('higher-education', 'Higher Education'), ('graduate-degree', 'Graduate Degree'), ('masters-degree', 'Masters Degree'), ('doctoral-degree', 'Doctoral Degree')], help_text='Education level required', max_length=50, null=True)),
                ('milestones', models.PositiveIntegerField(blank=True, help_text='Number of milestones for the job', null=True)),
                ('job_level', models.CharField(blank=True, choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')], help_text='Job difficulty level (hard, medium, or easy)', max_length=50, null=True)),
                ('comapanyName', models.CharField(blank=True, max_length=255, null=True)),
                ('location', models.CharField(blank=True, max_length=255, null=True)),
                ('posted_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
