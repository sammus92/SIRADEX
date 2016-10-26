# coding: utf8

import datetime
import os.path
from pprint    import pprint
from datetime  import time
from uuid      import uuid4
from reportlab.platypus   import *
from reportlab.lib.units  import *
from reportlab.lib        import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums  import *

def gestionar():
	if session.usuario != None:
		if(session.usuario["tipo"] == "DEX"):
			admin = 2
		elif(session.usuario["tipo"] == "Administrador"):
			admin = 1
		else:
			admin = 0
	else:
		redirect(URL(c ="default",f="index"))

	rows = db(db.PRODUCTO.ci_usu_creador==session.usuario['cedula']).select()
	detalles = {}
	nombres = {}
	cant_esp = 0
	cant_val = 0
	cant_rec = 0

	for row in rows:
		dict_campos = dict()
		dict_nombres = dict()

		campos = db((db.PRODUCTO_TIENE_CAMPO.id_campo == db.CAMPO.id_campo)
					& (db.PRODUCTO_TIENE_CAMPO.id_prod == row.id_producto)).select()

		for campo in campos:
			dict_campos[campo.CAMPO.nombre] = campo.PRODUCTO_TIENE_CAMPO.valor_campo

		detalles[row] = dict_campos

		nombres_act = db((db.PRODUCTO.id_tipo == db.TIPO_ACTIVIDAD.id_tipo)
					& (db.PRODUCTO.id_producto == row.id_producto)).select()

		for nombre in nombres_act:
			print nombre.TIPO_ACTIVIDAD.nombre
			nombres[row] = nombre.TIPO_ACTIVIDAD.nombre

		if row["estado"] == "En espera":
			cant_esp += 1
		elif row["estado"] == "Validada":
			cant_val += 1
		elif row["estado"] == "Rechazada":
			cant_rec += 1


	# Para el modal de Agregar actividad
	programas = db(db.PROGRAMA.papelera==False).select('nombre')
	formulario = SQLFORM.factory(
		Field('programa', requires=IS_NOT_EMPTY()),
		Field('id_tipo',  requires=IS_NOT_EMPTY()))
	if formulario.process(session=None, formname='crear_tipo').accepted:
		redirect(URL(agregar,args=[formulario.vars.id_tipo]))
	elif formulario.errors:
		response.flash = 'el formulario tiene errores'

	return locals()

def tipos():
	if session.usuario != None:
		if(session.usuario["tipo"] == "DEX"):
			admin = 2
		elif(session.usuario["tipo"] == "Administrador"):
			admin = 1
		else:
			admin = 0
	else:
		redirect(URL(c ="default",f="index"))

	rows = db(db.TIPO_ACTIVIDAD.papelera==False).select()
	return locals()


def agregar():
	if session.usuario != None:
		if(session.usuario["tipo"] == "DEX"):
			admin = 2
		elif(session.usuario["tipo"] == "Administrador"):
			admin = 1
		else:
			admin = 0
	else:
		redirect(URL(c ="default",f="index"))

	# Para la fecha maxima de realizacion
	now = datetime.datetime.now()
	if now.month < 10 :
		mes = "-0" +  str(now.month)
	else:
		mes = "-" +  str(now.month)
	if now.day < 10 :
		dia = "-0" +  str(now.day)
	else:
		dia = "-" +  str(now.month)
	fecha_max = str(now.year) + mes + dia


	tipo =  int(request.args(0))

	campos_id = db(db.ACT_POSEE_CAMPO.id_tipo_act == tipo).select()
	tipo_actividad = db(db.TIPO_ACTIVIDAD.id_tipo == tipo).select().first()

	nombre_actividad = tipo_actividad.nombre
	descripcion_actividad = tipo_actividad.descripcion

	fields = []
	fields.append(Field('nombre','string',requires=[IS_NOT_EMPTY(),IS_LENGTH(50)]))
	fields.append(Field('descripcion','string',requires=[IS_NOT_EMPTY(),IS_LENGTH(250)]))
	fields.append(Field('fecha_realizacion','date',requires=[IS_NOT_EMPTY(),IS_DATE(format=T('%Y-%m-%d'),error_message='Fecha invalida, debe ser: AAA-MM-DD')]))
	fields.append(Field('lugar','string',requires=[IS_NOT_EMPTY(),IS_LENGTH(50)]))

	for row in campos_id:
		rows_campo = db(db.CAMPO.id_campo == row.id_campo).select().first()
		nombre = rows_campo.nombre.replace(" ", "_")
		try :
			if int(nombre[0]):
				nombre = "campo_"+nombre
		except:
			pass

		obligatorio = rows_campo.obligatorio
		tipo_campo = rows_campo.tipo_campo
		if obligatorio:
			if tipo_campo in   ['Fecha']:             fields.append(Field(nombre,'date',requires=[IS_NOT_EMPTY(),IS_DATE(format=T('%Y-%m-%d'),error_message='Fecha invalida, debe ser: AAA-MM-DD')]))
			elif tipo_campo in ['Texto Corto']:       fields.append(Field(nombre,'string',requires=[IS_NOT_EMPTY(error_message='Inserte texto')]))
			elif tipo_campo in ['Cedula']:            fields.append(Field(nombre,'string',requires=[IS_NOT_EMPTY(),IS_MATCH('\d{2}.\d{3}.\d{3}$', error_message='CI invalida, debe ser: XX.XXX.XXX')]))
			elif tipo_campo in ['Documento']:         fields.append(Field(nombre,'upload',uploadfolder=URL('static/archivos'),requires=[IS_NOT_EMPTY(error_message='Debe subirse un archivo')]))
			elif tipo_campo in ['Telefono']:          fields.append(Field(nombre,'string',requires=[IS_NOT_EMPTY(),IS_MATCH('\(0\d{3}\)\d{3}-\d{2}-\d{2}$', error_message='Telefeno invalido, debe ser: (0xxx)xxx-xx-xx')]))
			elif tipo_campo in ['Cantidad Entera']:   fields.append(Field(nombre,'string',requires=[IS_NOT_EMPTY(),IS_INT_IN_RANGE(-9223372036854775800, 9223372036854775807)]))
			elif tipo_campo in ['Cantidad Decimal']:  fields.append(Field(nombre,'string',requires=[IS_NOT_EMPTY(),IS_DECIMAL_IN_RANGE(-9223372036854775800, 9223372036854775807, dot=".",error_message='El numero debe ser de la forma X.X, donde X esta entre -9223372036854775800 y 9223372036854775807')]))
			elif tipo_campo in ['Texto Largo']:           fields.append(Field(nombre,'texto',requires=IS_NOT_EMPTY()))

		else:
			if tipo_campo in   ['Fecha']:             fields.append(Field(nombre,'date',requires=IS_EMPTY_OR(IS_DATE(format=T('%Y-%m-%d'),error_message='Fecha invalida, debe ser: AAA-MM-DD'))))
			elif tipo_campo in ['Texto Corto']:       fields.append(Field(nombre,'string'))
			elif tipo_campo in ['Cedula']:            fields.append(Field(nombre,'string',requires=IS_EMPTY_OR(IS_MATCH('\d{2}.\d{3}.\d{3}$', error_message='CI invalida, debe ser: XX.XXX.XXX'))))
			elif tipo_campo in ['Documento']:         fields.append(Field(nombre,'upload',requires=IS_EMPTY_OR(IS_UPLOAD_FILENAME()),uploadfolder=URL('static/archivos')))
			elif tipo_campo in ['Telefono']:          fields.append(Field(nombre,'string',requires=IS_EMPTY_OR(IS_MATCH('\(0\d{3}\)\d{3}-\d{2}-\d{2}$', error_message='Telefeno invalido, debe ser: (0xxx)xxx-xx-xx'))))
			elif tipo_campo in ['Cantidad Entera']:   fields.append(Field(nombre,'string',requires=IS_EMPTY_OR(IS_INT_IN_RANGE(-9223372036854775800, 9223372036854775807))))
			elif tipo_campo in ['Cantidad Decimal']:  fields.append(Field(nombre,'string',requires=IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(-9223372036854775800, 9223372036854775807, dot=".",error_message='El numero debe ser de la forma X.X, donde X esta entre -9223372036854775800 y 9223372036854775807'))))
			elif tipo_campo in ['Texto Largo']:           fields.append(Field(nombre,'texto',requires=IS_NOT_EMPTY()))


	#fields.append(Field(nombre,requires=IS_IN_SET([(1,'Method1'), (2,'Method2'), (3,'Method3')], zero='Select')))
	form=SQLFORM.factory(*fields)
	form.element(_type='submit')['_class']="btn blue-add btn-block btn-border"
	form.element(_type='submit')['_value']="Agregar"

	if form.process().accepted:
		no = ['nombre','descripcion','fecha_realizacion','lugar']
		dicc_producto = db.PRODUCTO.insert(id_tipo = tipo,nombre=form.vars.nombre, descripcion=form.vars.descripcion,\
									  estado='En espera',fecha_realizacion=form.vars.fecha_realizacion, fecha_modificacion=now, \
									  lugar = form.vars.lugar, ci_usu_creador= session.usuario['cedula'])
		id_producto = dicc_producto['id_producto']
		for var in form.vars:
			if not(var in no):

				try:
					print var[0:6]
					if (var[0:6]=="campo_"):
						campo = var[6:]
				except:
					pass

				campo = campo.replace("_"," ")
				print "Lo imprimes: " + campo
				id_camp = db(db.CAMPO.nombre==campo).select().first().id_campo
				print id_camp
				valor = getattr(form.vars ,var)
				db.PRODUCTO_TIENE_CAMPO.insert(id_prod=id_producto,id_campo=id_camp,valor_campo= valor)
		redirect(URL('gestionar'))
	elif form.errors:
		response.flash = 'el formulario tiene errores'



	return locals()



def modificar():
	if session.usuario != None:
		if(session.usuario["tipo"] == "DEX"):
			admin = 2
		elif(session.usuario["tipo"] == "Administrador"):
			admin = 1
		else:
			admin = 0
	else:
		redirect(URL(c ="default",f="index"))

	id_producto = int(request.args(0))

	now = datetime.datetime.now()
	if now.month < 10 :
		mes = "-0" +  str(now.month)
	else:
		mes = "-" +  str(now.month)
	if now.day < 10 :
		dia = "-0" +  str(now.day)
	else:
		dia = "-" +  str(now.month)
	fecha_max = str(now.year) + mes + dia

	# Obtenemos la actividad para mostrarla en el html
	producto = db(db.PRODUCTO.id_producto==id_producto).select().first()
	tipo_actividad = db(db.TIPO_ACTIVIDAD.id_tipo == producto.id_tipo).select().first()

	nombre_actividad = tipo_actividad.nombre
	descripcion_actividad = tipo_actividad.descripcion

	# Creamos el formulario
	rows = db(db.PRODUCTO_TIENE_CAMPO.id_prod == id_producto).select()
	fields = []
	fields.append(Field('nombre','string',requires=[IS_NOT_EMPTY(),IS_LENGTH(50)]))
	fields.append(Field('descripcion','string',requires=[IS_NOT_EMPTY(),IS_LENGTH(250)]))
	fields.append(Field('fecha_realizacion','date',requires=[IS_NOT_EMPTY(),IS_DATE(format=T('%Y-%m-%d'),error_message='Fecha invalida, debe ser: AAA-MM-DD')]))
	fields.append(Field('lugar','string',requires=[IS_NOT_EMPTY(),IS_LENGTH(50)]))

	valores = {}
	valores['nombre'] = producto.nombre
	valores['descripcion'] = producto.descripcion
	valores['fecha_realizacion'] = producto.fecha_realizacion
	valores['lugar'] = producto.lugar


	for row in rows:
		rows_campo = db(db.CAMPO.id_campo == row.id_campo).select().first()
		nombre = rows_campo.nombre.replace(" ", "_")
		try :
			if int(nombre[0]):
				nombre = "campo_"+nombre
		except:
			pass

		obligatorio = rows_campo.obligatorio
		tipo_campo = rows_campo.tipo_campo

		if obligatorio:
			if tipo_campo in   ['Fecha']:             fields.append(Field(nombre,'date',requires=[IS_NOT_EMPTY(),IS_DATE(format=T('%Y-%m-%d'),error_message='Fecha invalida, debe ser: AAA-MM-DD')]))
			elif tipo_campo in ['Texto Corto']:       fields.append(Field(nombre,'string',requires=[IS_NOT_EMPTY(error_message='Inserte texto')]))
			elif tipo_campo in ['Cedula']:            fields.append(Field(nombre,'string',requires=[IS_NOT_EMPTY(),IS_MATCH('\d{2}.\d{3}.\d{3}$', error_message='CI invalida, debe ser: XX.XXX.XXX')]))
			elif tipo_campo in ['Documento']:         fields.append(Field(nombre,'upload',uploadfolder=URL('static/archivos'),requires=[IS_NOT_EMPTY(error_message='Debe subirse un archivo')]))
			elif tipo_campo in ['Telefono']:          fields.append(Field(nombre,'string',requires=[IS_NOT_EMPTY(),IS_MATCH('\(0\d{3}\)\d{3}-\d{2}-\d{2}$', error_message='Telefeno invalido, debe ser: (0xxx)xxx-xx-xx')]))
			elif tipo_campo in ['Cantidad Entera']:   fields.append(Field(nombre,'string',requires=[IS_NOT_EMPTY(),IS_INT_IN_RANGE(-9223372036854775800, 9223372036854775807)]))
			elif tipo_campo in ['Cantidad Decimal']:  fields.append(Field(nombre,'string',requires=[IS_NOT_EMPTY(),IS_DECIMAL_IN_RANGE(-9223372036854775800, 9223372036854775807, dot=".",error_message='El numero debe ser de la forma X.X, donde X esta entre -9223372036854775800 y 9223372036854775807')]))
			elif tipo_campo in ['Texto Largo']:           fields.append(Field(nombre,'texto',requires=IS_NOT_EMPTY()))

		else:
			if tipo_campo in   ['Fecha']:             fields.append(Field(nombre,'date',requires=IS_EMPTY_OR(IS_DATE(format=T('%Y-%m-%d'),error_message='Fecha invalida, debe ser: AAA-MM-DD'))))
			elif tipo_campo in ['Texto Corto']:       fields.append(Field(nombre,'string'))
			elif tipo_campo in ['Cedula']:            fields.append(Field(nombre,'string',requires=IS_EMPTY_OR(IS_MATCH('\d{2}.\d{3}.\d{3}$', error_message='CI invalida, debe ser: XX.XXX.XXX'))))
			elif tipo_campo in ['Documento']:         fields.append(Field(nombre,'upload',requires=IS_EMPTY_OR(IS_UPLOAD_FILENAME()),uploadfolder=URL('static/archivos')))
			elif tipo_campo in ['Telefono']:          fields.append(Field(nombre,'string',requires=IS_EMPTY_OR(IS_MATCH('\(0\d{3}\)\d{3}-\d{2}-\d{2}$', error_message='Telefeno invalido, debe ser: (0xxx)xxx-xx-xx'))))
			elif tipo_campo in ['Cantidad Entera']:   fields.append(Field(nombre,'string',requires=IS_EMPTY_OR(IS_INT_IN_RANGE(-9223372036854775800, 9223372036854775807))))
			elif tipo_campo in ['Cantidad Decimal']:  fields.append(Field(nombre,'string',requires=IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(-9223372036854775800, 9223372036854775807, dot=".",error_message='El numero debe ser de la forma X.X, donde X esta entre -9223372036854775800 y 9223372036854775807'))))
			elif tipo_campo in ['Texto Largo']:           fields.append(Field(nombre,'texto',requires=IS_NOT_EMPTY()))

		valores[nombre]=row.valor_campo

	form=SQLFORM.factory(*fields)
	form.element(_type='submit')['_class']="btn blue-add btn-block btn-border"
	form.element(_type='submit')['_value']="Modificar"

	print valores
	# Le escribimos la informacion a las vistas
	for nombre_campo in valores.keys():
		setattr(form.vars, nombre_campo, valores[nombre_campo])

	# Al aceptar el formulario
	if form.process().accepted:
		no = ['nombre','descripcion','fecha_realizacion','fecha_modificacion','lugar']
		sql = "UPDATE PRODUCTO SET estado = 'En espera' WHERE id_producto = '"+str(id_producto)+"';"

		sql2 = "UPDATE PRODUCTO SET fecha_modificacion='"+str(now.date())+"' WHERE id_producto = '"+str(id_producto)+"';"
		print "\n\nel sql quedo:" +sql
		print "\nel otro: "+sql2
		db.executesql(sql)
		print "listo1"
		db.executesql(sql2)
		print "listo 2"

		for var in form.vars:
			print "trabajare con: " + var
			valor_anterior = valores[var]
			print "valor anterior: " + str(valor_anterior)
			print "entrara " + str(not(var in no))
			if not(var in no):
				try:
					if (var[0:6]=="campo_"):
						campo = var[6:]
				except:
					pass
				print "var:" + var
				valor_nuevo = getattr(form.vars ,var)
				print "El valor es: " + valor_nuevo
				if valor_nuevo != valor_anterior:
					campo = campo.replace("_"," ")
					id_campo = db(db.CAMPO.nombre==campo).select().first().id_campo

					sql = "UPDATE PRODUCTO_TIENE_CAMPO SET valor_campo = '" + str(valor_nuevo)
					sql = sql + "' WHERE id_prod = '" + str(id_producto) + "' AND id_campo = '" + str(id_campo) + "';"
					db.executesql(sql)

				else:
					print "next"
			else:
				valor_nuevo = getattr(form.vars ,var)
				if valor_nuevo != valor_anterior:
					sql = "UPDATE PRODUCTO SET "+var+"= '"+str(valor_nuevo)+\
						  "' WHERE id_producto = '"+str(id_producto)+"';"
					db.executesql(sql)
					print " agregada "+ str(var)
				else:
					print "next "+ str(var)


		redirect(URL('gestionar'))

	return locals()


def eliminar():
	id_act = int(request.args(0))


	set_tiene_campo = db(db.PRODUCTO_TIENE_CAMPO.id_prod == id_act)
	set_tiene_campo.delete()
	producto = db(db.PRODUCTO.id_producto == id_act)
	producto.delete()

	redirect(URL('gestionar'))

	#return "producto {} eliminada".format(producto)
	return locals()


# Funcion utilizada para el ajax en el agregar
def obtener_actividades():

	programa = db(db.PROGRAMA.nombre==request.vars.programa).select().first()
	tiposA = db(db.TIPO_ACTIVIDAD.id_programa==programa.id_programa).select(db.TIPO_ACTIVIDAD.nombre,
		db.TIPO_ACTIVIDAD.id_tipo).as_list()

	concat = '<option></option>'

	for tipo in tiposA:

		concat += '<option value='+str(tipo['id_tipo'])+'>'+tipo['nombre']+'</option>'


	return "jQuery('#lista_tipos').empty().append('"+concat+"')"

# Funcion utilizada para el ajax cuando se elige la actividad para que aparezcan los campos
def seleccion_actividad():
	if request.vars.id_tipo=="":
		tipo_global = None
		respuesta = "jQuery('#nombre_actividad').empty();"
		respuesta += "jQuery('#descripcion_actividad').empty();"
		respuesta += "jQuery('#campos_actividad').empty()"
		return respuesta

	tipo =  request.vars.id_tipo
	tipo_global = tipo
	posibles_campos = {'Fecha':'date', 'Telefono':'string', 'Texto Corto':'string','Documento':'upload', 'Numero Entero':'integer', 'Texto Largo':'text'}

	campos_id = db(db.ACT_POSEE_CAMPO.id_tipo_act == tipo).select()
	tipo_actividad = db(db.TIPO_ACTIVIDAD.id_tipo == tipo).select().first()
	nombre_actividad = tipo_actividad.nombre
	descripcion_actividad = tipo_actividad.descripcion

	respuesta_inputs = ""

	for row in campos_id:

		rows_campo = db(db.CAMPO.id_campo == row.id_campo).select().first()
		nombre_campo = rows_campo.nombre
		nombre_campo_input = nombre_campo.replace(" ", "_").replace("-", "_")
		obligatorio_campo = rows_campo.obligatorio
		tipo_campo = rows_campo.tipo_campo
		es_obligatorio = ""

		if obligatorio_campo:
			nombre_campo += " (*)"
			es_obligatorio += " obligatorio"


		html_input = '<div class="form-group">'+\
						'<label for="'+nombre_campo_input+'" class = "control-label col-sm-3">'+nombre_campo+'</label>'+\
						'<div class="col-sm-8">'+\
							'<input class="form-control input-'+posibles_campos[tipo_campo]+es_obligatorio+'" type="'+posibles_campos[tipo_campo]+'" name="'+nombre_campo_input+'"/>'+\
						'</div>'+\
					'</div>'

		respuesta_inputs += html_input


	respuesta = "jQuery('#nombre_actividad').empty().append('"+nombre_actividad+"');"
	respuesta += "jQuery('#descripcion_actividad').empty().append('"+descripcion_actividad+"');"
	respuesta += "jQuery('#campos_actividad').empty().append('"+respuesta_inputs+"')"

	return respuesta


'''
def agregar():
	if session.usuario != None:
		if(session.usuario["tipo"] == "DEX"):
			admin = 2
		elif(session.usuario["tipo"] == "Administrador"):
			admin = 1
		else:
			admin = 0
	else:
		redirect(URL(c ="default",f="index"))

	# Para la fecha maxima de realizacion
	now = datetime.datetime.now()
	if now.month < 10 :
		mes = "-0" +  str(now.month)
	else:
		mes = "-" +  str(now.month)
	if now.day < 10 :
		dia = "-0" +  str(now.day)
	else:
		dia = "-" +  str(now.month)
	fecha_max = str(now.year) + mes + dia

	# Lista de programas para listarlos en el select
	programas =  db(db.PROGRAMA).select(db.PROGRAMA.nombre,db.PROGRAMA.id_programa).as_list()


	formulario = SQLFORM(db.PRODUCTO)
	if formulario.process(session=None, formname='crear_tipo').accepted:
		print formulario.vars
		redirect(URL('gestionar'))
		id = db.PRODUCTO.insert(**db.PRODUCTO._filter_fields(formulario.vars))
		formulario.vars.PRODUCTO=id
		id = db.PRODUCTO_TIENE_CAMPO.insert(**db.PRODUCTO_TIENE_CAMPO._filter_fields(formulario.vars))
	elif formulario.errors:
		print "error"
		formulario.errors.fecha = T('mala fecha')
		print formulario.errors
	else:
		print "fatal"


	return locals()
'''


#Funcion para exportar PDF de un producto
def get_pdf():

	producto = db.PRODUCTO(request.args(0))
	creador= db(db.USUARIO.ci == producto .ci_usu_creador).select()[0]
	tmpfilename = os.path.join(request.folder,'private',str(uuid4()))
	doc = SimpleDocTemplate(tmpfilename)
	elements = []

	# Definimos los estilos para el documento
	estilo = getSampleStyleSheet()

	estilo_titulo = estilo["Normal"]
	estilo_titulo.alignment = TA_CENTER
	estilo_titulo.fontName = "Helvetica"
	estilo_titulo.fontSize = 12
	estilo_titulo.leading = 15

	estilo_tabla = estilo["BodyText"]
	estilo_tabla.alignment = TA_LEFT
	estilo_tabla.fontName = "Helvetica"
	estilo_tabla.fontSize = 10
	estilo_tabla.leading = 12

	estilo_footer = estilo["Italic"]
	estilo_footer.alignment = TA_CENTER
	estilo_footer.fontName = "Helvetica"
	estilo_footer.fontSize = 10
	estilo_footer.leading = 12

	# Agrega el footer al documento
	def addFooter(canvas, doc):

		footer1 = Paragraph('''<br/>Sartenejas, Baruta, Edo. Miranda - Apartado 89000 Cable Unibolivar Caracas Venezuela. Teléfono +58 0212-9063111
		 					   <br/>Litoral. Camurí Grande, Edo. Vargas Parroquia Naiguatá. Teléfono +58 0212-9069000	''', estilo_footer)
		w, h = footer1.wrap(doc.width, doc.bottomMargin)
		footer1.drawOn(canvas, doc.leftMargin, h)


	usb_logo_url = os.path.join(request.folder, 'static/images','usblogo.png')
	usblogo = Image(usb_logo_url)
	usblogo.drawHeight = 70
	usblogo.drawWidth  = 100

	elements.append(usblogo)
	elements.append(Paragraph('Universidad Simón Bolívar' , estilo_titulo))
	elements.append(Paragraph('Deacanato de Extensión' , estilo_titulo))
	elements.append(Paragraph('Sistema de Registro de Actividades de Extensión (SIRADEX)' , estilo_titulo))
	elements.append(Paragraph('<br/><br/>DATOS DEL PRODUCTO' , estilo_titulo))

	data = [
	[''],
	['', Paragraph('<b>NOMBRE DEL PRODUCTO:</b> ', estilo_tabla),  str(producto.nombre), ''],
	['', Paragraph('<b>REALIZADO POR: </b>' , estilo_tabla),  str(creador.nombres +' '+ creador.apellidos),''],
	['', Paragraph('<b>CI:</b> ' , estilo_tabla),  str(creador.ci),''],
	['', Paragraph('<b>DESCRIPCIÓN:</b> ', estilo_tabla) ,  str (producto.descripcion), ''],
	['', Paragraph('<b>LUGAR DE REALIZACIÓN:</b>', estilo_tabla),  str (producto.lugar), ''],
	['', Paragraph('<b>FECHA DE CREACIÓN:</b> ', estilo_tabla) ,  str (producto.fecha_realizacion), ''],
	['', Paragraph('<b>ÚLTIMA FECHA DE MODIFICACIÓN: </b>' , estilo_tabla) ,  str (producto.fecha_modificacion), ''],
	['', Paragraph('<b>STATUS DEL PRODUCTO: </b>', estilo_tabla) ,  str (producto.estado), '']
	]

	t=Table(data, colWidths=(2*inch))

	elements.append(t)

	# construimos el documento
	doc.build(elements, onFirstPage=addFooter)
	data = open(tmpfilename,"rb").read()
	os.unlink(tmpfilename)
	response.headers['Content-Type']='application/pdf'

	return data
