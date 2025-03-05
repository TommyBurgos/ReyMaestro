# Generated by Django 4.2.19 on 2025-02-07 18:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_rol_tipousuario_user_rol_user_tipo_usuario'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contenido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=200)),
                ('tipo_contenido', models.CharField(choices=[('video', 'Video'), ('documento', 'Documento')], max_length=10)),
                ('url_contenido', models.URLField()),
                ('fecha_subida', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Curso',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=200)),
                ('descripcion', models.TextField(blank=True)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('profesor', models.ForeignKey(limit_choices_to={'rol__nombre': 'Profesor'}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProgresoUsuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('completado', models.BooleanField(default=False)),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True)),
                ('contenido', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.contenido')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Pago',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monto', models.DecimalField(decimal_places=2, max_digits=10)),
                ('fecha_pago', models.DateTimeField(auto_now_add=True)),
                ('metodo_pago', models.CharField(max_length=50)),
                ('estado_pago', models.CharField(choices=[('pendiente', 'Pendiente'), ('completado', 'Completado'), ('fallido', 'Fallido')], default='pendiente', max_length=20)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Nivel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=200)),
                ('descripcion', models.TextField(blank=True)),
                ('orden', models.PositiveIntegerField()),
                ('curso', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.curso')),
            ],
        ),
        migrations.CreateModel(
            name='Inscripcion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_inscripcion', models.DateTimeField(auto_now_add=True)),
                ('estado', models.CharField(choices=[('activo', 'Activo'), ('inactivo', 'Inactivo'), ('completado', 'Completado')], default='activo', max_length=10)),
                ('curso', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.curso')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='contenido',
            name='nivel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.nivel'),
        ),
        migrations.CreateModel(
            name='Calificacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('calificacion', models.DecimalField(decimal_places=2, max_digits=5)),
                ('fecha_calificacion', models.DateTimeField(auto_now_add=True)),
                ('contenido', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.contenido')),
                ('inscripcion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.inscripcion')),
            ],
        ),
    ]
