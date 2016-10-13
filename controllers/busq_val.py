# Funcion para busquedas publicas
def busqueda():


    if request.vars.Programa == "all" and request.vars.TipoActividad == "all":
        sql = "SELECT nombre FROM PRODUCTO WHERE nombre LIKE \'%" + request.vars.Producto \
         + "%\' AND ci_usu_creador IN (SELECT ci FROM usuario WHERE nombres LIKE \'%" + request.vars.Autor + "%\') AND estado=\'Validada\';" 

        productos = db.executesql(sql)

    elif request.vars.Programa != "all" and request.vars.TipoActividad == "all":
        sql = "SELECT nombre FROM PRODUCTO WHERE nombre LIKE \'%" + request.vars.Producto \
         + "%\' AND ci_usu_creador IN (SELECT ci FROM usuario WHERE nombres LIKE \'%" + request.vars.Autor\
         + "%\') AND id_tipo IN (SELECT id_tipo FROM TIPO_ACTIVIDAD WHERE id_programa=" + request.vars.Programa + ") AND estado=\'Validada\';"

        productos = db.executesql(sql)

    elif request.vars.Programa == "all" and request.vars.TipoActividad != "all":
        sql = "SELECT nombre FROM PRODUCTO WHERE nombre LIKE \'%" + request.vars.Producto \
         + "%\' AND ci_usu_creador IN (SELECT ci FROM usuario WHERE nombres LIKE \'%" + request.vars.Autor\
         + "%\') AND id_tipo=\'" + request.vars.TipoActividad + "\' AND estado=\'Validada\';" 

        productos = db.executesql(sql)

    else:
        sql = "SELECT nombre FROM PRODUCTO WHERE nombre LIKE \'%" + request.vars.Producto \
         + "%\' AND ci_usu_creador IN (SELECT ci FROM usuario WHERE nombres LIKE \'%" + request.vars.Autor\
         + "%\') AND id_tipo IN (SELECT id_tipo FROM TIPO_ACTIVIDAD WHERE id_programa=" + request.vars.Programa\
         + ") AND id_tipo=\'" + request.vars.TipoActividad + "\' AND estado=\'Validada\';"

        productos = db.executesql(sql)
    return locals()

# Mostrar productos
def ver_producto():
  if session.usuario != None:
    if session.usuario["tipo"] == "DEX" or session.usuario["tipo"] == "Administrador":
      if(session.usuario["tipo"] == "DEX"):
        admin = 2
      elif(session.usuario["tipo"] == "Administrador"):
        admin = 1
      else:
        admin = 0
    else:
      redirect(URL(c ="default",f="vMenuPrincipal"))
  else:
    redirect(URL(c ="default",f="index"))

  id_producto = int(request.args(0))
  producto = db(db.PRODUCTO.id_producto == id_producto).select().first()
  usuario_producto = db(db.USUARIO.ci == producto.ci_usu_creador).select().first()
  usuario_nombre = usuario_producto.nombres + " " + usuario_producto.apellidos
  tipo_actividad = db(db.TIPO_ACTIVIDAD.id_tipo == producto.id_tipo).select().first()
  programa_nombre = db(db.PROGRAMA.id_programa == tipo_actividad.id_programa).select().first().nombre


  form = SQLFORM.factory(
            Field("Nombre_Producto", default=producto.nombre,writable = False),
            Field('Descripcion',default=producto.descripcion,writable = False),
            Field('Fecha_de_Relaizacion', default=producto.fecha_realizacion,writable=False),
            Field('Lugar', default=producto.lugar,writable=False),            
            readonly=True)

  #Agregamos los otros elementos de los campos
  campos = db(db.PRODUCTO_TIENE_CAMPO.id_prod == producto.id_producto).select()
  
  elementos = []
  for campo_valor in campos:
    campo = db(db.CAMPO.id_campo == campo_valor.id_campo).select().first()
    nombre_campo = campo.nombre
    nombre_campo = nombre_campo.replace(" ", "_")
    try :
      if int(nombre_campo[0]):
        nombre_campo = "campo_"+nombre_campo
    except:
      pass

    elementos.append(Field(nombre_campo, default=campo_valor.valor_campo, writable=False))

  if len(elementos) != 0:
    form_datos = SQLFORM.factory(*elementos, readonly=True)

  form_validado = SQLFORM(
            db.PRODUCTO,            
            fields=['nombre'],            
            labels={'nombre':'Nuevo nombre'},
            col3={'nombre':'Este es el nombre que aparecera al momento de exportar las actividades'}

  )
  form_validado.element(_type='submit')['_class']="btn blue-add btn-block btn-border"
  form_validado.element(_type='submit')['_value']="Actualizar"

  print "El var request es:"
  print request.var
  if request.var:
    print "holaaa aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    print request.var

  return locals()



# Vista de validaciones
def gestionar_validacion():

    if session.usuario != None:
        if session.usuario["tipo"] == "DEX" or session.usuario["tipo"] == "Administrador":
            if(session.usuario["tipo"] == "DEX"):
                admin = 2
            elif(session.usuario["tipo"] == "Administrador"):
                admin = 1
            else:
                admin = 0
        else:
            redirect(URL(c ="default",f="vMenuPrincipal"))
    else:
        redirect(URL(c ="default",f="index"))


    # Hago el query Espera

    sqlValidadas = "select producto.id_producto, producto.nombre, tipo_actividad.nombre from producto inner join tipo_actividad"\
    + " on producto.id_tipo=tipo_actividad.id_tipo where producto.estado='Validada';"
    sqlEspera = "select producto.id_producto, producto.nombre, tipo_actividad.nombre from producto inner join tipo_actividad"\
    + " on producto.id_tipo=tipo_actividad.id_tipo where producto.estado='En espera';"
    sqlRechazadas = "select producto.id_producto, producto.nombre, tipo_actividad.nombre from producto inner join tipo_actividad"\
    + " on producto.id_tipo=tipo_actividad.id_tipo where producto.estado='Rechazada';"
    productosV= db.executesql(sqlValidadas)
    productosE = db.executesql(sqlEspera)
    productosR = db.executesql(sqlRechazadas)

    return locals()

# Metodo para validar un producto
def validar():
    if session.usuario != None:
        if session.usuario["tipo"] == "DEX" or session.usuario["tipo"] == "Administrador":
            if(session.usuario["tipo"] == "DEX"):
                admin = 2
            elif(session.usuario["tipo"] == "Administrador"):
                admin = 1
            else:
                admin = 0
        else:
            redirect(URL(c ="default",f="vMenuPrincipal"))
    else:
        redirect(URL(c ="default",f="index"))

    id_act = int(request.args[0])
    ''''
    formulario = SQLFORM(db.PRODUCTO,id_act)
    if formulario.process(session=None, formname='validar_producto').accepted:
        print "se envio"
        redirect(URL('gestionar_validacion'))
    elif formulario.errors:
        print "error"
        print formulario.errors
    else:
        print "fatal"
    '''
    db(db.PRODUCTO.id_producto == id_act).update(estado='Validada')
    session.message = 'Producto validado exitosamente'
    redirect(URL('gestionar_validacion.html'))

# Metodo para rechazar una producto
def rechazar():
    if session.usuario != None:
        if session.usuario["tipo"] == "DEX" or session.usuario["tipo"] == "Administrador":
            if(session.usuario["tipo"] == "DEX"):
                admin = 2
            elif(session.usuario["tipo"] == "Administrador"):
                admin = 1
            else:
                admin = 0
        else:
            redirect(URL(c ="default",f="vMenuPrincipal"))
    else:
        redirect(URL(c ="default",f="index"))

    id_act = int(request.args[0])
    db(db.PRODUCTO.id_producto == id_act).update(estado='Rechazada')
    session.message = 'Producto rechazado'
    redirect(URL('gestionar_validacion.html'))
