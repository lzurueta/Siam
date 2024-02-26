from django.db import models

# Create your models here.
class Proveedor(models.Model):
    razon_social = models.CharField(max_length=150, null=True, blank=True, verbose_name="Razon Social")
    cuit = models.CharField(max_length=11, null=True, blank=True, verbose_name="CUIT")

    def __str__(self):
        return self.razon_social


class CPOPAGO(models.Model):
    proveedor = models.ForeignKey(Proveedor, verbose_name='Proveedor', on_delete=models.CASCADE, null=True, blank=True)
    cpopanio = models.IntegerField(null=True, blank=True, verbose_name="Ejercicio del Pago")
    cpopnro = models.IntegerField(null=True, blank=True, verbose_name="Nro. de Pago")
    copaanio = models.IntegerField(null=True, blank=True, verbose_name="Ejercicio de la Ord. de Pago")
    cjurcod  = models.CharField(max_length=1, null=True, blank=True, verbose_name="Jurisdiccion")
    crepudo = models.CharField(max_length=4, null=True, blank=True, verbose_name="UDO (Unidad de Organización)")
    copanro = models.IntegerField(null=True, blank=True, verbose_name="Nro. de Ord. De Pago")
    cbencui = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name="CUIT")
    cpoptip = models.CharField(max_length=1, null=True, blank=True, verbose_name="Tipo de Pago")
    cchqnum = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Nro. de Cheque")
    cchqcta = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Nro de Cuenta")
    cchqtip = models.CharField(max_length=4, null=True, blank=True, verbose_name="Tipo de Cheque")
    cpopimp = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Importe")
    cpopfpg = models.DateTimeField(null=True, blank=True, verbose_name="Fec. De Pago")
    corbanio = models.IntegerField(null=True, blank=True, verbose_name="Ejer. Orden bancaria")
    corbnro = models.IntegerField(null=True, blank=True, verbose_name="Nro Orden Bancaria")
    cndbanio = models.IntegerField(null=True, blank=True, verbose_name="Ejer. Nota de Debito")
    cndbnro = models.IntegerField(null=True, blank=True, verbose_name="Nro. Nota de Debito")
    cpop096 = models.CharField(max_length=10, null=True, blank=True, verbose_name="Usuario Alta")
    cpop097 = models.DateTimeField(null=True, blank=True, verbose_name="Fec.Alta")
    cpop098 = models.CharField(max_length=10, null=True, blank=True, verbose_name="Usuario Modif")
    cpop099 = models.DateTimeField(null=True, blank=True, verbose_name="Fec.Modif")
    cpopest = models.CharField(max_length=1, null=True, blank=True, verbose_name="Estado del Pago")
    cpopjur = models.CharField(max_length=1, null=True, blank=True, verbose_name="Jur Origen del Pago")
    cpopudo = models.CharField(max_length=4, null=True, blank=True, verbose_name="UDO origen del Pago")
    cpophab = models.CharField(max_length=1, null=True, blank=True, verbose_name="Habilitacion")
    copapgd = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Pagado")
    copasdo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Saldo")
    cchqfpg = models.DateTimeField(null=True, blank=True, verbose_name="Fec.Entrega Cheque")
    cchq097 = models.DateTimeField(null=True, blank=True, verbose_name="Fec.Ingreso Mes.Entrada")
    cchqest = models.CharField(max_length=1, null=True, blank=True, verbose_name="Estado Cheq")
    cchqant = models.CharField(max_length=1, null=True, blank=True, verbose_name="Anticipo Cheque")
    cchqtic = models.CharField(max_length=1, null=True, blank=True, verbose_name="Tipo de cheque")
    copafue = models.IntegerField(null=True, blank=True, verbose_name="Fuente OP")
    cchqben = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Beneficiario del Cheque")
    cla2suc = models.IntegerField(null=True, blank=True, verbose_name="Sucursal Banco")
    cla2cta = models.CharField(max_length=20, null=True, blank=True, verbose_name="Nro.Cta Acred.Banco")
    cla2imp = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Importe Acreditado")
    ctippag = models.CharField(max_length=1, null=True, blank=True, verbose_name="Pago Bancarizado")
    copaest = models.IntegerField(null=True, blank=True, verbose_name="Estado OP")

    def __str__(self):
        return self.proveedor.razon_social