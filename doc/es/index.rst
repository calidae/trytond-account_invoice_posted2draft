=======================================
Cambiar facturas confirmadas a borrador
=======================================

Permite cambiar facturas confirmadas a borrador (eliminando el asiento contable de la factura) para poder modificar la información de la factura.

Configuración
-------------

Para poder cambiar el estado de las facturas confirmadas abra el menú |menú_account_journal| y marque la opción **Permitir cancelar asientos** de los diarios de tipo **Ingresos** (para las facturas de cliente) o **Gastos** (para las facturas de proveedor).

.. |menú_account_journal| tryref:: account.menu_journal_configuration/complete_name

Módulos de los que depende
==========================

Instalados
----------

.. toctree::
   :maxdepth: 1

   /account_invoice/index

Dependencias
------------

* `Facturación`_

.. _Facturación: ../account_invoice/index.html
