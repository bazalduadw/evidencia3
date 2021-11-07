#region Librerias
from collections import namedtuple
import re
import os
import datetime
from datetime import datetime as dt
import sys
import csv
from prettytable import PrettyTable
import sqlite3
from sqlite3 import Error
#endregion

# region Declaracion de variables
LimpiarPantalla = lambda: os.system('cls')
monto_total = 0
diccionario_ventas = {}
regexLetras = "^[a-zA-Z ]+$"
lista_productos = []
#endregion

#region Metodos

def separador():
    print("*" * 20)

def registrarVenta():
    monto_total = 0
    try:
        with sqlite3.connect("ventas.db") as conn: #Puente
            c = conn.cursor()
            c.execute("Select folio from detalle")
            folios = c.fetchall()
            if folios:
                folio_max = max(folios)
                folio = folio_max[0] + 1
            else:
                folio = 0
        # Validar que clave no exista
            switch = True
            clave = int(input("Ingrese la clave de la venta: "))
            c.execute("SELECT COUNT(*) FROM detalle WHERE id_venta = ?",(clave,))
            clave_valida = c.fetchall()
            clave_valida = clave_valida[0]
            if clave_valida[0]>=1:
                input("Error: La clave ya existe...")
            else:
                while switch:
                    folio += 1
                    while True:
                        descripcion = input("Ingrese la descripción del producto: ")
                        if descripcion == "":
                            print("Este dato no puede ser vacío")
                        else:
                            break
                    while True:
                        try:
                            cantidad = int(input("Ingrese la cantidad del producto: "))
                        except Exception:
                            print(f"Ocurrió un problema, debe ingresar un dato numérico entero: {sys.exc_info()[0]}")
                            input("Pulse enter para continuar... ")
                        else:
                            break
                    while True:
                        try:
                            precio = float(input("Ingrese el precio del producto: "))
                        except Exception:
                            print(f"Ocurrió un problema, debe ingresar un dato numérico de tipo entero o float: {sys.exc_info()[0]}")
                            input("Pulse enter para continuar... ")
                        else:
                            break
                    datos_detalle = folio,descripcion,cantidad,precio,clave
                    c.execute("INSERT INTO detalle VALUES(?,?,?,?,?)",datos_detalle)
                    print("Registro agregado exitosamente!")

                    monto = (cantidad * precio)
                    monto_total = monto_total + monto
                    while True:
                        respuesta = input("¿Desea agregar otro producto? [S/N]: ")
                        if respuesta.upper() == "S":
                            LimpiarPantalla()
                            break
                        elif respuesta.upper() == "N":
                            fecha = dt.today().strftime('%d/%m/%Y')
                            switch = False
                            c.execute("INSERT INTO venta VALUES(?,?)",(clave, fecha))

                            IVA = (monto_total * 0.16)
                            LimpiarPantalla()
                            print(f'El monto total a pagar es: {"${:,.2f}".format((monto_total + IVA))}')
                            print(f'El IVA aplicado del 16% es: {"${:,.2f}".format((IVA))}')
                            input("Presione Enter para continuar...")
                            break
                        else:
                            print("Error: Opcion no valida.")
        if conn:
            conn.close()
    except:
        print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")


def consultarVenta():
    LimpiarPantalla()
    monto_total_consulta = 0
    clave = int(input("Ingrese la clave que desea buscar: "))
    try:
        with sqlite3.connect("ventas.db") as conn: #Puente
            mi_cursor = conn.cursor() #Mensajero
            mi_cursor.execute("SELECT v.*, d.* FROM venta as v,detalle as d WHERE v.clave = (?) AND d.id_venta = (?)",(clave,clave))
            registros = mi_cursor.fetchall()
            t = PrettyTable(['Clave','Fecha','Folio','Descripcion','Cantidad','Precio','ID_Venta'])
            for clave,fecha,folio,descripcion,cantidad,precio,id_venta in registros:
                t.add_row([clave,fecha,folio,descripcion,cantidad,precio,id_venta])
                monto = cantidad * precio
                monto_total_consulta = monto_total_consulta + monto
            print(t)
            IVA = monto_total_consulta * 0.16
            print(f"Monto:  {'${:,.2f}'.format(monto_total_consulta)}")
            print(f"Monto total: {'${:,.2f}'.format(monto_total_consulta + IVA)}")
            print(f"El IVA aplicado del 16% fue: {'${:,.2f}'.format(IVA)}")
            separador()
            input("Presiona Enter para continuar...")
        if conn:
            conn.close()
    except Error as e:
        print (e)
    except Exception:
        print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")
    

def consultarVenta_porFecha():
    LimpiarPantalla()
    fecha_buscar = input("Ingrese la fecha a buscar en formato DD/MM/AAAA: ")
    try:
        with sqlite3.connect("ventas.db") as conn: #Puente
            mi_cursor = conn.cursor() #Mensajero
            mi_cursor.execute("SELECT DISTINCT d.id_venta,d.descripcion,d.cantidad,d.precio FROM detalle as d, venta as v WHERE v.fecha = ?",(fecha_buscar,))
            registros = mi_cursor.fetchall()
            t = PrettyTable(['Clave','Descripcion','Cantidad','Precio'])
            for clave,descripcion,cantidad,precio in registros:
                t.add_row([clave,descripcion,cantidad,precio])
            print(t)

            mi_cursor.execute("SELECT clave FROM venta")
            cant_registros = mi_cursor.fetchall()

            print("---Monto total por clave---")
            t = PrettyTable(['Clave','Monto','IVA','Gran Total'])
            for clave in cant_registros:
                mi_cursor.execute("SELECT d.id_venta as clave, SUM(d.cantidad * precio) as monto FROM detalle as d WHERE d.id_venta = ?",clave)
                registros = mi_cursor.fetchall()
                for clave,monto in registros:
                    iva = monto * 0.16
                    monto_total = monto + iva
                    t.add_row([clave,monto,iva,monto_total])
            print(t)
            input("Presiona Enter para continuar...")
        if conn:
            conn.close()
    except Error as e:
        print (e)
    except Exception:
        print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")

def crearTablas():
    try:
        with sqlite3.connect("ventas.db") as conn:
            c = conn.cursor()
            c.execute("CREATE TABLE IF NOT EXISTS venta (clave INTEGER PRIMARY KEY, fecha TEXT NOT NULL) ")
            c.execute("CREATE TABLE IF NOT EXISTS detalle (folio INTEGER PRIMARY KEY, descripcion TEXT NOT NULL, cantidad INTEGER NOT NULL, precio REAL NOT NULL, id_venta INTEGER NOT NULL, FOREIGN KEY(id_venta) REFERENCES venta(clave)) ")
    except Error as e:
        print(e)
    except Exception:
        print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")
    finally:
        if conn:
            conn.close()

def main():
    crearTablas()
    while True:
        LimpiarPantalla()
        print("***MENU VENTA***")
        print("¿Qué desea hacer?")
        print("1: Registrar Venta")
        print("2: Consultar Venta")
        print("3: Reporte de ventas a partir de una fecha")
        print("4: Salir")
        try:
            opcion = int(input("Ingrese una opción: "))
            if opcion == 1:
                registrarVenta()
            elif opcion == 2:
                consultarVenta()
            elif opcion == 3:
                consultarVenta_porFecha()
            elif opcion == 4:
                break
            else:
                print("Opcion no valida")
                input("Pulse enter para continuar... ")
        except ValueError:
            print('Ingrese un dato numérico entero. ')
            input("Pulse enter para continuar... ")
#endregion

# Se manda a llamar el metodo Main
main()