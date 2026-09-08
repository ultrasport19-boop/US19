# -*- coding: utf-8 -*-
"""US19 · las tandas de historias.

Los textos, aparte del dibujo. `historias.py` sabe pintar cuatro pieles;
esto dice QUE se pinta y con cual. Asi rehacer una tanda entera con otra
piel es cambiar una palabra.

REGLAS QUE NO SE NEGOCIAN (Diego es interno de kinesiologia hasta
diciembre de 2026):
  · Nada de «diagnostico», «tratamiento», «rehabilitacion», «paciente»,
    «deficit» ni «riesgo de lesion».
  · Ninguna cifra que no este confirmada.
  · Ninguna promesa de resultado.
  · Antes de la titulacion, NADA que deje entender que ya es kinesiologo.
"""

# =========================================================================
#  TANDA 1 · RECLUTAR — para socios nuevos. Se publica ya.
# =========================================================================
RECLUTAR = [
    dict(piel="papel", eyebrow="constancia",
         titular=["ENTRENAR NO ES", "CASTIGO.", "ES MANTENIMIENTO."], acento=2,
         cuerpo="Al cuerpo no se le arregla una vez. Se le cuida todas las semanas, "
                "como a todo lo que quieres que dure.",
         modulo=("lista", [("Fuerza guiada", "un plan, no una máquina suelta"),
                           ("Grupos reducidos", "ocho personas por hora, no cuarenta"),
                           ("Reevaluación mensual", "incluida en tu plan")])),

    dict(piel="rojo", eyebrow="empieza esta semana",
         titular=["DOS DÍAS", "A LA SEMANA", "CAMBIAN", "EL AÑO."], acento=3,
         cuerpo="No hace falta vivir aquí. Hace falta venir, y que alguien te diga "
                "qué hacer cuando llegas.",
         modulo=("semana", [1, 3])),

    dict(piel="foto", foto="gym-2.jpg", eyebrow="grupos de ocho",
         titular=["AQUÍ NADIE", "ENTRENA SOLO."], acento=1,
         cuerpo="Ocho personas por hora y alguien mirando cómo lo haces. "
                "Esa es toda la diferencia.",
         modulo=("regla", None)),

    dict(piel="dato", eyebrow="lo que no se mide, no se sabe",
         titular=["CADA MES", "TE VOLVEMOS", "A MEDIR."], acento=2,
         cuerpo="Peso, masa muscular, perímetros y fuerza. Los mismos números, "
                "el mismo día del mes, para que veas si vas o no vas.",
         modulo=("cifra", ("1", "reevaluación", "mensual incluida",
                           "en todos los planes, sin costo extra"))),

    dict(piel="papel", eyebrow="para partir",
         titular=["NO NECESITAS", "ESTAR EN FORMA", "PARA EMPEZAR."], acento=2,
         cuerpo="Esa es la parte que se entrena. Llegas como estás y desde ahí "
                "se arma el plan.",
         modulo=("lista", [("Sin experiencia previa", "se empieza por lo básico, bien hecho"),
                           ("A tu ritmo", "la carga la pone tu cuerpo, no el de al lado"),
                           ("Con seguimiento", "alguien mira cómo lo haces")])),

    dict(piel="rojo", eyebrow="capacidad real",
         titular=["OCHO", "PERSONAS", "POR HORA.", "NO CUARENTA."], acento=3,
         cuerpo="Por eso se pueden corregir las cosas mientras las haces, "
                "que es cuando sirve.",
         modulo=("semana", [0, 2, 4])),

    dict(piel="foto", foto="sala-1.jpg", eyebrow="pencahue",
         titular=["NO HAY QUE IRSE", "A TALCA", "PARA ENTRENAR", "EN SERIO."], acento=3,
         cuerpo="Rack, barra, mancuernas, poleas y sala de cardio aparte. "
                "A cinco minutos de tu casa.",
         modulo=("regla", None)),

    dict(piel="dato", eyebrow="antes de opinar, medir",
         titular=["SIN MEDIR,", "TODO ES", "OPINIÓN."], acento=2,
         cuerpo="Bioimpedancia al entrar y todos los meses. No para asustarte: "
                "para saber qué está funcionando y qué no.",
         modulo=("cifra", ("28", "datos", "en cada medición",
                           "peso, masa muscular, agua, perímetros y más"))),

    dict(piel="papel", eyebrow="el primer día",
         titular=["LO DIFÍCIL", "ES LA PUERTA.", "Y DURA", "UNA HORA."], acento=3,
         cuerpo="Después ya sabes dónde va todo, quién te espera y qué toca. "
                "Nadie llega sabiendo.",
         modulo=("lista", [("Te mostramos la sala", "sin apuro y sin público"),
                           ("Medimos", "para tener de dónde partir"),
                           ("Sales con un plan", "escrito, no de memoria")])),

    dict(piel="rojo", eyebrow="ven como estés",
         titular=["TÚ PONES", "LAS GANAS.", "EL PLAN", "LO PONEMOS", "NOSOTROS."], acento=[3, 4],
         cuerpo="No tienes que llegar sabiendo qué hacer. Para eso está el que te acompaña.",
         modulo=("semana", [1, 4])),

    dict(piel="foto", foto="gym-4.jpg", eyebrow="con nombre y apellido",
         titular=["AQUÍ SABEMOS", "CÓMO TE LLAMAS."], acento=1,
         cuerpo="Y qué te duele, qué te cuesta y hasta dónde llegaste el mes pasado. "
                "En un gimnasio de ochenta personas eso no pasa.",
         modulo=("regla", None)),

    dict(piel="dato", eyebrow="tu plan no es fijo",
         titular=["LO QUE HACES", "EN OCTUBRE", "NO ES LO MISMO", "QUE EN JULIO."], acento=3,
         cuerpo="Cada reevaluación cambia las cargas y los ejercicios. "
                "El plan se mueve contigo.",
         modulo=("cifra", ("8", "personas", "por hora, como máximo",
                           "para que se pueda corregir mientras entrenas"))),
]

# =========================================================================
#  RETIRADO · 8-sep-2026
#
#  Habia una tanda de diciembre que jugaba con la titulacion de Diego
#  («algo cambia este mes», «cinco anos de carrera terminan»). El mismo
#  dia la descarto: «no hablemos nada de kinesiologia hasta posterior a
#  mi titulacion».
#
#  REGLA, hasta que el titulo sea real: ni una pieza que hable de
#  kinesiologia, ni que la insinue, ni que anuncie «algo que viene».
#  Tampoco de refilon con «carrera», «cinco anos» o «una capacidad mas».
#  No es solo el texto: es que hoy la web, la ficha de ingreso y el bot
#  dicen por escrito que aqui no se presta atencion de salud, y una
#  historia que sugiera lo contrario contradice eso con fecha.
# =========================================================================
