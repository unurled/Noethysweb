from django.db import migrations, models

def set_default_label(apps, schema_editor):
    Deduction = apps.get_model('core', 'Deduction')  # Récupère le modèle sans importer models
    Deduction.objects.update(label=1)  # Met à jour tous les enregistrements avec label=1

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0191_auto_20250320_1605'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deduction',
            name='label',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.PROTECT,
                to='core.typededuction',
                verbose_name='Label'
            ),
        ),
        migrations.RunPython(set_default_label),  # Exécute la mise à jour des valeurs
    ]
