# Generated by Django 4.2.7 on 2025-03-26 06:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('classification', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LogSource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Source name (e.g., API Server, Database, Authentication Service)', max_length=100)),
                ('description', models.TextField(blank=True, help_text='Description of the log source')),
                ('type', models.CharField(help_text='Type of source (e.g., Server, Application, Service)', max_length=50)),
                ('is_active', models.BooleanField(default=True, help_text='Whether this log source is currently active')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'log source',
                'verbose_name_plural': 'log sources',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='LogEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('severity', models.CharField(choices=[('DEBUG', 'Debug'), ('INFO', 'Info'), ('WARNING', 'Warning'), ('ERROR', 'Error'), ('CRITICAL', 'Critical')], default='INFO', help_text='Severity level of the log entry', max_length=10)),
                ('message', models.TextField(help_text='Log message content')),
                ('timestamp', models.DateTimeField(help_text='Time when the log event occurred')),
                ('ip_address', models.GenericIPAddressField(blank=True, help_text='IP address related to the log event', null=True)),
                ('user_id', models.CharField(blank=True, help_text='User ID related to the log event, if applicable', max_length=100)),
                ('session_id', models.CharField(blank=True, help_text='Session ID related to the log event, if applicable', max_length=100)),
                ('request_id', models.CharField(blank=True, help_text='Request ID related to the log event, if applicable', max_length=100)),
                ('additional_data', models.JSONField(blank=True, default=dict, help_text='Any additional data related to the log event')),
                ('is_read', models.BooleanField(default=False, help_text='Whether this log has been read/acknowledged')),
                ('is_flagged', models.BooleanField(default=False, help_text='Whether this log has been flagged for attention')),
                ('notes', models.TextField(blank=True, help_text='Additional notes about this log entry')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('classification', models.ForeignKey(blank=True, help_text='Classification of this log entry', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='log_entries', to='classification.logclassification')),
                ('source', models.ForeignKey(help_text='Source of the log entry', on_delete=django.db.models.deletion.CASCADE, related_name='log_entries', to='logs.logsource')),
            ],
            options={
                'verbose_name': 'log entry',
                'verbose_name_plural': 'log entries',
                'ordering': ['-timestamp'],
                'indexes': [models.Index(fields=['severity'], name='logs_logent_severit_938571_idx'), models.Index(fields=['timestamp'], name='logs_logent_timesta_1e81d2_idx'), models.Index(fields=['source'], name='logs_logent_source__7d234e_idx'), models.Index(fields=['user_id'], name='logs_logent_user_id_5f8edf_idx'), models.Index(fields=['is_read'], name='logs_logent_is_read_824e55_idx'), models.Index(fields=['is_flagged'], name='logs_logent_is_flag_5f9533_idx')],
            },
        ),
    ]
