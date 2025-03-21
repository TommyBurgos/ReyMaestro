# Generated by Django 4.2.19 on 2025-02-11 00:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_contenido_curso_progresousuario_pago_nivel_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='contenido',
            name='archivo',
            field=models.FileField(blank=True, null=True, upload_to='documentos/'),
        ),
        migrations.AddField(
            model_name='contenido',
            name='curso',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='user.curso'),
        ),
        migrations.AddField(
            model_name='contenido',
            name='descripcion',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='contenido',
            name='imagen',
            field=models.ImageField(blank=True, null=True, upload_to='imagenes/'),
        ),
        migrations.AlterField(
            model_name='contenido',
            name='nivel',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='user.nivel'),
        ),
        migrations.AlterField(
            model_name='contenido',
            name='tipo_contenido',
            field=models.CharField(choices=[('video', 'Video'), ('documento', 'Documento'), ('texto', 'Texto')], max_length=10),
        ),
        migrations.AlterField(
            model_name='contenido',
            name='url_contenido',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='inscripcion',
            name='estado',
            field=models.CharField(choices=[('en_progreso', 'En Progreso'), ('completado', 'Completado')], default='en_progreso', max_length=20),
        ),
    ]
