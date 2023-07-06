import streamlit as st

from utils import db

import streamlit as st
from streamlit_chat import message
import streamlit_scrollable_textbox as stx

from langchain.chains import ConversationChain
from langchain.prompts.prompt import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
import datetime

if 'ai' not in st.session_state:
        st.session_state['ai'] = []

today = datetime.datetime.now()
today = today.strftime("%Y-%m-%d")

def ask_patient_hc(context, question):
  

  default_template = f"""Eres un asistente médico inteligente encargado de proporcionar información relevante sobre la historia clínica de un paciente. Las consultas se encuentran organizadas en orden cronológico, de la más antigua a la más reciente, separadas por '###'. Ten en cuenta que las fechas siguen el formato YYYY-MM-DD y que la fecha de hoy es {today}. En la historia clínica, 'Nota médica' refiere a las anotaciones del médico que atendió la consulta, 'Diagnóstico' es el diagnóstico proporcionado por el médico, 'Motivos de consulta' son los síntomas o problemas mencionados por el paciente antes de su atención, 'Tratamiento' son las recomendaciones brindadas por el médico, 'Medicación / Prescripción médica' son los medicamentos recetados y 'Reposo' indica las horas recomendadas de descanso para el paciente. Si la pregunta no está relacionada con el paciente, responde con 'No lo sé'.

Historia clínica:
{context}
"""

  chat_template = default_template + """Historial de chat:
{history}
Human: {input}
AI:"""

  prompt = PromptTemplate(input_variables=["history", "input"], template=chat_template)
  chat = ChatOpenAI(temperature=0,model_name="gpt-4", max_tokens=1500)
  memory = ConversationBufferWindowMemory(k=2)
  if len(st.session_state.ai) == 1:
     memory.save_context({"input": st.session_state.past[-1]}, {"output": st.session_state.ai[0]})
  if len(st.session_state.ai) > 1:
     memory.save_context({"input": st.session_state.past[-2]}, {"output": st.session_state.ai[-2]})
     memory.save_context({"input": st.session_state.past[-1]}, {"output": st.session_state.ai[-1]})
  
  prompt = PromptTemplate(input_variables=["history", "input"], template=chat_template)

  conversation = ConversationChain(
    llm=chat,
    verbose=True,
    memory=memory,
    prompt=prompt)
  response = conversation.predict(input=question)
  st.session_state.ai.append(response)
  return response




def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == 'uma2023':
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

if check_password():

	col1, col2 = st.columns(2)
	# Create the navigation bar for switching between tabs
	with col1:
	    st.title("ÜmaBot 👩‍⚕️\nOpenAI GPT-3.5 🤖 + Langchain ⛓️ + Streamlit ")
	
	    if 'generated' not in st.session_state:
	        st.session_state['generated'] = []
	
	    if 'past' not in st.session_state:
	        st.session_state['past'] = []
	
	    if 'patient_uid' not in st.session_state:
	        st.session_state['patient_uid'] = []
	        
	    if 'patient_data' not in st.session_state:
	        st.session_state['patient_data'] = []
	
	    if "temp" not in st.session_state:
	        st.session_state["temp"] = ""
	    if "user_input" not in st.session_state:
	        st.session_state["user_input"] = []
	
	    def clear_text():
	       st.session_state["temp"] = st.session_state["text"]
	       st.session_state["text"] = ""
	
	
	    def get_text():
	        input_text = st.text_input("You: ", "", key="text",on_change=clear_text)
	        st.session_state['user_input'].append(input_text)
	        if st.session_state['temp'] == "":
	           return "Hola!"
	        else:
	            return st.session_state['temp']
	
	    user_input = get_text()
	
	    if user_input:
	        if user_input == 'Hola!':
	            st.session_state['past'] = []
	            st.session_state['generated'] = []
	            st.session_state.past.append("Hola")
	            st.session_state['generated'].append('¡Hola! Soy ÜmaBot. Por favor, ingresa un número del 1 al 5 como ID de usuario.')
	        else:
	            try:
	                if st.session_state['generated'][-1] == '¡Hola! Soy ÜmaBot. Por favor, ingresa un número del 1 al 5 como ID de usuario.':
	                    st.session_state.patient_uid.append(user_input) 
	                    st.session_state.past.append(user_input)
	                    st.session_state['generated'].append("Haz una consulta sobre la historia clínica del paciente")
	                    
	                else:
	                    # output = generate_response(user_input)
	                    uid = st.session_state.patient_uid[0]
	                    output = ask_patient_hc(st.session_state.patient_data[0], user_input)
	                    st.session_state.past.append(user_input)
	                    st.session_state['generated'].append(output)
	            except:
	                pass
	
	    if st.session_state['generated']:
	        for i in range(len(st.session_state['generated']) - 1, -1, -1):
	            message(st.session_state["generated"][i], key=str(i))
	            message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
	
	with col2:
	    st.title("EHR Patient Data")
	    # Example EHR patient data
	    patient_data1 = """Paciente de 49 años, de sexo Femenino.
	
	Fecha: 2021-05-15
	
	Nota médica: Previamente sana. 
	refiere cuadro clínico de 12 horas con cefalea y diarrea. refire que esta asintomatica a la hora de la consulta. 
	
	Diagnóstico: Cefalea
	
	Destino final: En domicilio con instrucciones 
	
	Tratamiento: solicita certificado por 24 horas ya que ayer no fue a trabajar por cefalea y no alimentacion por todo el dia. indica que tiene mal patron de alimentacion y que ayer no comio nada. 
	
	Reposo: 24 horas
	
	###
	
	Fecha: 2021-06-29
	
	Nota médica: EL DIA 28/6/21 SE COLOCA LA VACUNA DEL COVID 19 , EVOLUCIONA CON FIEBRE, ESCALOFRIOS, MALESTAR GENERAL . 
	SE INDICA ANALGESICOS.
	
	Diagnóstico: Fiebre
	
	Destino final: En domicilio con instrucciones 
	
	Tratamiento: PARACETAMOL 1 GR C6H 
	IBUPROFENO 400 C12H . 
	 
	
	Reposo: 24 horas
	
	###
	
	Fecha: 2021-06-30
	
	Nota médica: Paciente femenina con clinica de dos dias de evolucion caracterizado por cefalea holocraneana, fiebre cuantificada en 38°c, refiere aparicion de los sintomas posterior a la aplicacion de la vacuna Astrazeneca 
	
	Diagnóstico: Fiebre
	
	Destino final: En domicilio con instrucciones 
	
	Medicación / Prescripción médica: ibuprofeno 400 mg ibupirac 400 mg analgesico antiinflam. comp.x 100 Analgésico Antiinflam. 
	
	Reposo: 48 horas
	
	###
	
	Fecha: 2023-04-28
	
	Nota médica: refiere diarrea y vomitos de un dia de evolucion. en beg.hde. se dan pautas de alarma 
	ap no refiere 
	
	Diagnóstico: Gastroenteritis
	
	Destino final: En domicilio con instrucciones 
	
	Tratamiento: hidratacion 
	dieta astringente
	loperamida un comp cada ocho horas 
	reliveran un comp cada ocho horas
	 
	
	Reposo: 24 horas
	
	###
	"""
	    
	    patient_data2 = """Paciente de 24 años, de sexo Femenino.
	
	Fecha: 2022-07-06
	
	Nota médica: Paciente refiere dolor lumbar de 24 hs de evolucion. Niega alergias. 
	
	Diagnóstico: Signos sintomas lumbares
	
	Destino final: En domicilio con instrucciones
	
	Motivos de consulta: Dolor de espalda.lumbalgia.lumbalgia de menos de 24hs de evolución.empeora con el movimiento o cambio de posición.tomo algún analgésico o desinflamatorio 
	
	Medicación / Prescripción médica: meloxicam+pridinol MIO VIROBRON comp.x 10 Antiinflam.Analgésico.Miorrelaja 
	
	Tratamiento: Indico Meloxicam con pridinol cada 12 hs. Aplicación de calor en la zona. Pautas de alarma. En caso de persistir el dolor interconsulta con traumatología. 
	Reposo de 24 hs. 
	 
	
	Reposo: 24 horas
	
	###
	
	Fecha: 2022-08-04
	
	Nota médica:
	CONSULTA POR DOLOR DE GARGANTA, ODINOFAGIA, CONGESTIÓN NASAL. NIEGA OTROS SÍNTOMAS.
	INICIO HACE 72 HS.
	BUEN ESTADO GENERAL.
	NIEGA FAUCES ERITEMATOSAS.
	VACUNACIÓN COVID19 COMPLETA.
	APP: NIEGA. MEDIC HABITUAL: NIEGA. NIEGA ALERGIAS.
	
	Diagnóstico: Faringitis
	
	Destino final: En domicilio con instrucciones
	
	Motivos de consulta: Dolor de garganta.odinofagia.No tiene tos.Tiene moco.Sin antecedentes coronarios.no refiere antecedentes respiratorios.no refiere antecedentes renales 
	
	Medicación / Prescripción médica: desloratadina+betametasona FRENALER CORT comp.rec.x 10 Antialérgico Antiinflamatorio / bencidamina,clorhidrato ERNEX sol.spray x 30 ml Antiinflam.tópico 
	
	Tratamiento: FRENALER CORT 1 COMP X DIA X 3 DIAS.
	ERNEX SPRAY 3 VECES POR DIA.
	VAPOR DE AGUA.
	REPOSO 24 HS
	NUEVA CONSULTA EN 24 HS
	PAUTAS DE ALARMA. 
	
	Reposo: 24 horas
	
	###
	
	Fecha: 2022-09-14
	
	Nota médica: Paciente refiere vómitos y dolor abdominal de 24 hrs de evolución 
	
	Diagnóstico: Vómitos
	
	Destino final: En domicilio con instrucciones
	
	Motivos de consulta: Vómitos.nauseas/vómitos.No tiene tos.Tiene nauseas o vómitos de 1 dia.tolera liquidos.Sin antecedentes coronarios.no refiere antecedentes respiratorios.no refiere antecedentes renales 
	
	Tratamiento: 1.- dieta astringente e hidratacion 
	2.- recomendaciones y pautas de alarma. 
	
	Reposo: 24 horas
	
	###
	
	Fecha: 2022-09-17
	
	Nota médica: paciente quien cursa con cuadro de entorsis de tobillo derecho , posterior a esto con edema , se indica reposo, y manejo manejo analgesico
	
	Diagnóstico: Esguince de tobillo
	
	Destino final: En domicilio con instrucciones
	
	Motivos de consulta: Inflamacion en el tobillo 
	
	Reposo: 24 horas
	
	###
	
	Fecha: 2022-09-19
	
	Nota médica: PACIENTE EN SEGUIMIENTO TRAUMATOLOGICO POR ESGUINCE DE TOBILLO DERECHO DE 2 DIAS DE EVOLUCION, PERSISTE CON DOLOR LOCAL.
	
	Diagnóstico: Esguince de tobillo
	
	Destino final: Indico seguimiento por consultorio externo
	
	Motivos de consulta: Esguince 
	
	Tratamiento: SE INDICA TTO ANALGESICO-REPOSO 48 HS- SE DAN PAUTAS DE ALARMA-CONTROL EVOLUTIVO CON ESPECIALIDAD 
	
	Reposo: 48 horas
	
	###
	
	Fecha: 2022-10-03
	
	Nota médica: paciente quien ursa con cuadro de deposiciones diarreicas de un dia de evolucion , malestra general, seextiende certifiado de reposo
	
	Diagnóstico: Diarrea
	
	Destino final: En domicilio con instrucciones
	
	Motivos de consulta: Diarrea.diarrea.No tiene tos.Fiebre o escalofríos.diarrea 24 de evoución.Menos de 6 deposiciones diarias.materia fecal sin sangre.deposiciones líquidas.Sin antecedentes coronarios.no refiere antecedentes respiratorios.no refiere antecedentes renales 
	
	Medicación / Prescripción médica: trimebutina ALTRIP 200 comp.x 30 Antiespasmódico / saccharomyces boulardii FLORATIL 200 mg caps.x 10 Antidiarreico 
	
	Reposo: 24 horas
	
	###
	
	Fecha: 2022-11-01
	
	Nota médica: Paciente masculino con cuadro de amigdalitis aguda se indica manejo analgesico y cubrimiento antibiotico empirico, se sugiere reposo por 24 horas. 
	
	Diagnóstico: Amigdalitis
	
	Destino final: En domicilio con instrucciones
	
	Motivos de consulta: Fiebre.Dolor de cabeza.Dolor de garganta.Fiebre o escalofríos.odinofagia.cefalea.se siente mareado.No tiene tos.Menos de 48 horas 
	
	Medicación / Prescripción médica: paracetamol TAFIROL 1 G comp.ran.x 24 Analgésico Antifebril / amoxicilina AMOXIDAL 500 mg comp.rec.x 21 Antibiótico 
	
	Tratamiento: Amoxicilina
	Paracetamol 
	
	Reposo: 24 horas
	
	###
	
	Fecha: 2022-11-14
	
	Nota médica: pte masculino, madre refiere que desde ayer esta con tos y expectoracion mas fiebre que cede con paracetamol. se indica pautas de alarma y reposo
	
	Diagnóstico: Infeccion respiratoria aguda del tracto superior
	
	Destino final: En domicilio con instrucciones
	
	Motivos de consulta: Fiebre.Tos.Tos.Fiebre o escalofríos.Tiene moco.Tos con moco.Tos aguda.Sin antecedentes coronarios.no refiere antecedentes respiratorios.no refiere antecedentes renales.Menos de 48 horas.Tos.Fiebre o escalofríos.Tiene moco.Tos con moco.Tos aguda.Sin antecedentes coronarios.no refiere antecedentes respiratorios.no refiere antecedentes renales.Menos de 48 horas 
	
	Tratamiento: paracetamol
	hidratacion
	nebulizacion con sc fisiol 
	
	Reposo: 24 horas
	
	###
	"""
	
	    patient_data3 = """Paciente de 50 años, de sexo Masculino.
	
	Fecha: 2022-04-05
	
	Nota médica: paciente cursando con picos febriles, tos seca, congestion nasal, rinorrea hialina, malestar general, en tratamiento con azitromicina. 
	
	Diagnóstico: Gripe
	
	Destino final: En domicilio con instrucciones 
	
	Tratamiento: manejo sintomatico
	tratamiento antibiotico 
	reposo 24 horas 
	
	Reposo: 24 horas
	
	###
	
	Fecha: 2022-04-07
	
	Nota médica: px confirmado covid-19 positivo se realizo hisopado el dia 06/04 comenzo con sintomas el dia sabado 02/04 actualmente continua con fiebre 
	
	Diagnóstico: COVID19
	
	Destino final: En domicilio con instrucciones 
	
	Tratamiento: se indica tto y reposo 48 hs 
	
	Reposo: 48 horas
	
	###
	
	Fecha: 2022-04-10
	
	Nota médica: 
	
	Diagnóstico: COVID19
	
	Destino final: En domicilio con instrucciones 
	
	Reposo: 48 horas
	
	###
	
	Fecha: 2022-04-12
	
	Nota médica: MASCULINO 49 AÑOS
	EL FDS CURSO CON COVID19 POSITIVO 
	REFIERE CONGESTION NASAL , CANSANCIO
	
	Diagnóstico: COVID19
	
	Destino final: En domicilio con instrucciones 
	
	Tratamiento: ACEMUK 600MG CADA 12H POR 5 DIAS 
	VAPORIZACIONES 
	REPOSO 72 HORAS 
	
	Reposo: 72 horas
	
	###
	
	Fecha: 2022-05-02
	
	Nota médica: Paciente refiere tuvo covid19 el 06 de abril cumplio aislamiento por 10, actualmente con cefalea y adinamia post covid19
	
	Diagnóstico: Síntomas psicológicos mentales
	
	Destino final: En domicilio con instrucciones 
	
	Tratamiento: Paracetamol: 1 gramo cada 8 horas solo si es necesario.
	Valoracion por Neurologia. 
	
	Reposo: 24 horas
	
	###
	
	Fecha: 2022-07-20
	
	Nota médica: PACIENTE CON CUADRO CLINICO DE 03 DIAS DE EVOLUCION CONSISTENTE EN CONGESTION NASAL, ASOCIADO A ODINOFAGIA, MIALGIAS GENERALIZADAS, TOS SECA, CEFALEA GLOBAL, FIEBRE, NO MANEJO. ACTUALMENTE SINTOMATICO.
	
	Diagnóstico: Faringitis aguda
	
	Destino final: En domicilio con instrucciones 
	
	Medicación / Prescripción médica: fexofenadina ALLEGRA 120 mg comp.x 10 Antihistamínico 
	
	Tratamiento: REPOSO
	CONTROL CLINICO EN 48 HORAS 
	HIDRATACION CONTINUA
	TAFIROL COMP 1 GR TOMAR CADA 08 HORAS
	FEXOFENADINA COMP 120 MG TOMAR 1 CADA 12 HORAS POR 5 DIAS.
	 
	
	Reposo: 48 horas
	
	###
	
	Fecha: 2022-08-22
	
	Nota médica: Paciente con fiebre, cefalea, congestion nasal. 
	
	Diagnóstico: Fiebre
	
	Destino final: En domicilio con instrucciones 
	
	Tratamiento: Tratamiento sintomático y reposo de 48 hs 
	
	###
	
	Fecha: 2022-09-22
	
	Nota médica: Paciente quien refiere FIS hace 12 horas dado por nauseas vómitos, y actualmente con evacuaciones liquidas, cefalea.
	
	
	
	Diagnóstico: Gastroenteritis
	
	Destino final: En domicilio con instrucciones 
	
	Tratamiento: Realizar dieta de bajo consumo de azúcares, disminuir el consumo de lácteos, no consumir huevos, pescado, carnes rojas, fiambre, mariscos, no alimentos envasados ni gaseosas.
	
	 
	paracetamol 1 gr cada 8 horas por 3 dias.
	
	 
	
	Reposo: 24 horas
	
	###
	
	Fecha: 2022-09-25
	
	Nota médica: PACIENTE CONSULTA POR PRESENTAR DESDE EL 20 DE SEPTIEMBRE POLAQUIURIA, DOLOR EN INGLE IZQUIERDA NIEGA APP, SE DEJAN INDICACIONES
	
	
	UROCULTIVO
	ORINA COMPLETA
	LEVOFLOXACINA 1 COMP CADA DIA 5 DIAS (ANTIBIOTICO)
	FENAZOPIRIDINA 1 COMP CADA 12H POR 5 DIAS (ANALGESICO)
	LIQUIDOS
	
	Diagnóstico: Prostatitis
	
	Destino final: En domicilio con instrucciones 
	
	Medicación / Prescripción médica: cefalexina SINURIT 1000 mg comp.rec.x 16 Antibiótico / fenazopiridina CISTALGINA 200 mg comp.rec.x 10 Analgésico urinario 
	
	Tratamiento: CEFALEXINA 1 COMP CADA 12H POR 7 DIAS
	CISTALGINA 1 COMP CADA 12H POR 5 DIAS 
	
	Reposo: 48 horas
	
	###
	
	Fecha: 2022-09-28
	
	Nota médica: Paciente refiere comenzo el 25/09 disuria polaquiuria medicado con ATB continua con sintomas control 
	
	Diagnóstico: Infección urinaria
	
	Destino final: En domicilio con instrucciones 
	
	Tratamiento: Cefalexina Duo 1 c /12 hs 
	hidratacion abundante 
	Cistalgina 
	
	Reposo: 48 horas
	
	###
	"""
	    patient_data4 = """Paciente de 41 años, de sexo Femenino.
	
	Fecha: 2022-09-22
	
	Nota médica: ODINOFAGIA
	
	Diagnóstico: Fiebre
	
	Destino final: En domicilio con instrucciones
	
	Motivos de consulta: Dolor de garganta.odinofagia.Tos.Tiene moco.Sin antecedentes coronarios.no refiere antecedentes respiratorios.no refiere antecedentes renales 
	
	Reposo: 24 horas
	
	###
	
	Fecha: 2022-10-17
	
	Nota médica: paciente refiere que ayer en la noche su perrito de dos meses la mordio en la mano derecha . se indica concurrir a una guardia para revision y envio de atb orales. se da reposo por 24 horas . 
	
	Diagnóstico: Dolor en miembro superior
	
	Destino final: Indico concurrir a guardia externa 
	
	Tratamiento: se indica concurrir a una guardia para revision y envio de atb orales. se da reposo por 24 horas . 
	
	Reposo: 24 horas
	
	###
	
	Fecha: 2023-03-06
	
	Nota médica: Paciente con síndrome gripal, se indican pautas de tratamiento y reposo de 24 horas.
	
	Diagnóstico: Gripe
	
	Destino final: En domicilio con instrucciones
	
	Motivos de consulta: Fiebre.Fiebre o escalofríos.Tos.Tiene moco.Menos de 48 horas. .Sin antecedentes coronarios.no refiere antecedentes respiratorios.no refiere antecedentes renales 
	
	Reposo: 24 horas
	
	###
	
	Fecha: 2023-03-13
	
	Nota médica: DIARREA
	
	Diagnóstico: Diarrea
	
	Destino final: En domicilio con instrucciones
	
	Motivos de consulta: Fiebre.Diarrea.Congestión Nasal.Fiebre o escalofríos.diarrea.Tos.Tiene moco.Menos de 48 horas 
	
	Reposo: 24 horas
	
	###
	
	Fecha: 2023-04-03
	
	Nota médica: Paciente quien refiere que presenta cefalea, congestión nasal, tos, mialgia y malestar general 
	
	Diagnóstico: Gripe
	
	Destino final: En domicilio con instrucciones 
	
	Tratamiento: Se indica tratamiento sintomático hidratación oral abundante pautas de alarma control y seguimiento 
	
	Reposo: 72 horas
	
	###
	
	Fecha: 2023-05-09
	
	Nota médica: PACIENTE FEMENINO DE 41 AÑOS
	APP NIEGA
	NIEGA ALERGIA A MEDICAMENTOS
	CONSULTA POR PRESENTAR CUADRO CLINICO CARACTERIZADO POR CONGESTION NASAL, TOS SECA, DISFONIA, TEMP 38.7
	
	Diagnóstico: Infeccion respiratoria aguda del tracto superior
	
	Destino final: En domicilio con instrucciones
	
	Motivos de consulta: Tos.Fiebre.Congestión Nasal.Tos.Fiebre o escalofríos.odinofagia.cefalea.Tiene moco.Tos seca.Tos aguda 
	
	Medicación / Prescripción médica: acetilcisteína ACEMUK 600 mg tab.efer.x 10 Mucolítico / sodio,cloruro+carragenina NASITRAL spray nasal est. x 10ml Fluidificante de las vías aéreas / desloratadina+betametasona FRENALER CORT comp.rec.x 10 Antialérgico Antiinflamatorio 
	
	Tratamiento: SE INDICAN PAUTAS DE ALARMA
	ABUNDANTES LIQUIDOS
	PARACETAMOL 1 GR CADA 8 HORAS SI DOLOR O FIEBRE >37,5°
	NASITRAL SPRAY APLICAR 2 PULSACIONES CADA 8 HRS POR 5 DIAS
	ACEMUK 600 MG DILUIR EN AGUA Y TOMAR 1 COMP CADA 12 HRS POR 5 DIAS
	FRENALER CORT TOMAR 1 COMP CADA 12 HRS POR 5 DIAS
	NC 10/05/23 SEGUIMIENTO CLINICO (ÜMA CARE). 
	
	Reposo: 24 horas
	
	###
	
	Fecha: 2023-05-15
	
	Nota médica: Paciente de 41 años presenta congestion nasal moco amarillo , dolor en senos frontal. cefalea, astenia,disfonia y tos perruna esto inicia hace 7dias.Afebril .fue medicada con acemuk.
	
	Diagnóstico: Laringitis traqueitis aguda
	
	Destino final: En domicilio con instrucciones
	
	Motivos de consulta: Tos.Dolor de garganta.Dolor de cabeza.Congestión Nasal.Tos.odinofagia.cefalea.Fiebre o escalofríos.Tiene moco.Tos seca 
	
	Tratamiento: corteroid 0.6mg cc 30 ( 1 y2 cada 8hs+3 y4 cada 12hs +5 dia por unica vez)+ amoxicilina-acido clavulanico 1gramo cada 12h s por 
	 7 dias+ mucoltic 150 ml ( 10 ml cada 8hs por 3 dias)+reposo de 72 horas 
	
	Reposo: 72 horas
	
	###
	"""
	    patient_data5 = """Paciente de 59 años, de sexo Masculino.

Fecha: 2022-05-18

Nota médica: Masculino presenta catarro, tos, equivalentes febriles, astenia. Sin medicación. Niega otra sintomatología. APP: LINFOMA ACO por postcx aorta ALergias: niega

Diagnóstico: Sospecha COVID19

Destino final: En domicilio con monitoreo

Motivos de consulta: Sospecha de covid 

Tratamiento: Tratamiento sintomático / medidas generales higiénico-dietéticas / pautas de alarma / reposo relativo / control en 72 horas 
 

###

Fecha: 2022-05-23

Nota médica: Paciente refiere concurrió a guardia de forma presencia hace 3 dias donde evaluaron y diagnosticaron neumonía, medicaron.

Diagnóstico: Neumonía

Destino final: En domicilio con instrucciones

Motivos de consulta: Fiebre.Tos.odinofagia.Tiene moco 

Tratamiento: continuar tratamiento indicado. 

Reposo: 48 horas

###

Fecha: 2022-06-23

Nota médica: refiere cuadro clínico de cefalea, sensación febril y mialgia, secundario a aplicación de vacuna anticovid19. niega otros sintomas asociados.

Diagnóstico: Gripe

Destino final: En domicilio con instrucciones

Motivos de consulta: Fiebre.Dolor de cabeza.Fiebre o escalofríos.cefalea.No tiene tos 

Tratamiento: indico reposo en casa 24 hrs 

Reposo: 24 horas

###

Fecha: 2022-08-11

Nota médica: Refiere que tiene marcapasos y válvula cardiaca de reemplazo. se encuentra en estudio por bacteriemia. 

Diagnóstico: Fiebre

Destino final: En domicilio con instrucciones

Motivos de consulta: Fiebre.Fiebre o escalofríos.No tiene tos 

Tratamiento: Reposo de 24 hs 

###

Fecha: 2022-11-18

Nota médica: Refiere cólicos intestinales. Anticoagulado. 

Diagnóstico: Dolor abdominal

Destino final: En domicilio con instrucciones

Motivos de consulta: Colicos 

Tratamiento: Buscapina compuesta N cada 8 hs. 

###

Fecha: 2022-12-05

Nota médica: DOLOR TORAXICO
APP ICC--ENDOCARDITIS MARCAPASO

Diagnóstico: Dolor

Destino final: Indico concurrir a guardia externa

Motivos de consulta: Dolor de pecho.Insuficiencia cardiaca.No refiere dolor torácico 

Tratamiento: RECOMENDACIONES MEDICAS
SI LOS SINTOMAS PERSISTEN ACUDIR A LA GUARDIA PARA ESTUDIOS 

Reposo: 72 horas

###

Fecha: 2022-12-05

Nota médica: DOLOR TORAXICO
APP MARCAPASO

Diagnóstico: Dolor

Destino final: Indico concurrir a guardia externa

Motivos de consulta: Dolor de pecho.Insuficiencia cardiaca.No refiere dolor torácico.No refiere dolor torácico 

Tratamiento: ACUDIR A LA GUARDIA PARA ESTUDIOS 

Reposo: 72 horas

###

Fecha: 2022-12-05

Nota médica: Dolor precordial. Insuficiencia cardíaca crónica. 

Diagnóstico: Insuficiencia cardíaca

Destino final: En domicilio con instrucciones

Motivos de consulta: Dolor de pecho.No refiere dolor torácico 

Tratamiento: Consulta por Cardiólogia el día 07/2/22. Reposo por 72 horas. 

Reposo: 72 horas

###

Fecha: 2023-01-07

Nota médica: Paciente masculino con antecedente de insuficiencia cardiaca cronica en tratamiento, reposo por 72h

Diagnóstico: Insuficiencia cardíaca

Destino final: En domicilio con instrucciones

Motivos de consulta: Dolor de pecho.Dolor torácico 

Reposo: 72 horas

###

"""
	    patient_data = None
	    if st.session_state['patient_uid'] == ['1']:
	        st.session_state.patient_data.append(patient_data1)
	        patient_data = patient_data1
	        
	    if st.session_state['patient_uid'] == ['2']:
	        st.session_state.patient_data.append(patient_data2)
	        patient_data = patient_data2
		    
	    if st.session_state['patient_uid'] == ['3']:
	        st.session_state.patient_data.append(patient_data3)
	        patient_data = patient_data3
		    
	    if st.session_state['patient_uid'] == ['4']:
	        st.session_state.patient_data.append(patient_data4)
	        patient_data = patient_data4
		    
	    if st.session_state['patient_uid'] == ['5']:
	        st.session_state.patient_data.append(patient_data5)
	        patient_data = patient_data5
		    
	    # Display the EHR patient data
	    if patient_data:
	        st.subheader(f"Patient '{st.session_state['patient_uid'][0]}' Information")
	        stx.scrollableTextbox(patient_data,height = 350)
	
	COMMENT_TEMPLATE_MD = """{} - {}
	> {}"""
	
	
	def space(num_lines=1):
	    """Adds empty lines to the Streamlit app."""
	    for _ in range(num_lines):
	        st.write("")
	
	
	
	conn = db.connect()
	comments = db.collect(conn)
	
	with st.expander("💬 Abrir comentarios"):
	        st.write("**Comentarios:**")
	        for index, entry in enumerate(comments.itertuples()):
	            st.markdown(COMMENT_TEMPLATE_MD.format(entry.name, entry.date, entry.comment))
	
	            is_last = index == len(comments) - 1
	            is_new = "just_posted" in st.session_state and is_last
	            if is_new:
	              st.success("☝️ Tu comentario fue guardado exitosamente.")
	 
	        space(2)
	
			# Insert comment
	
	        st.write("**Dejá tu comentario:**")
	        form = st.form("comment")
	        name = form.text_input("Nombre")
	        comment = form.text_area("Comentario")
	        submit = form.form_submit_button("Guardar")
	
	        if submit:
	            #date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
	            db.insert(conn, [[name, today, comment]])
	            if "just_posted" not in st.session_state:
	                st.session_state["just_posted"] = True
	            st.experimental_rerun()
