# Generated by Django 4.2.19 on 2025-02-22 18:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0006_contenido_orden_curso_destacado_curso_estado_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Nivel',
            new_name='Modulo',
        ),
        migrations.CreateModel(
            name='Leccion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=200)),
                ('tipo_contenido', models.CharField(choices=[('video', 'Video'), ('documento', 'Documento'), ('texto', 'Texto')], max_length=10)),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('url_contenido', models.URLField(blank=True, null=True)),
                ('archivo', models.FileField(blank=True, null=True, upload_to='lecciones/')),
                ('imagen', models.ImageField(blank=True, null=True, upload_to='imagenes_lecciones/')),
                ('orden', models.PositiveIntegerField(default=1)),
                ('fecha_subida', models.DateTimeField(auto_now_add=True)),
                ('modulo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.modulo')),
            ],
        ),
    ]
