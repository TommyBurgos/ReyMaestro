# Generated by Django 4.2.19 on 2025-02-21 23:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_contenido_archivo_contenido_curso_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Foro',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=200)),
                ('descripcion', models.TextField()),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('curso', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.curso')),
            ],
        ),
        migrations.AddField(
            model_name='inscripcion',
            name='progreso',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=5),
        ),
        migrations.AddField(
            model_name='inscripcion',
            name='ultima_actividad',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.CreateModel(
            name='RegistroConexion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_conexion', models.DateTimeField(auto_now_add=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ParticipacionForo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad_comentarios', models.PositiveIntegerField(default=0)),
                ('foro', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.foro')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ComentarioForo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contenido', models.TextField()),
                ('fecha_comentario', models.DateTimeField(auto_now_add=True)),
                ('foro', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.foro')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
