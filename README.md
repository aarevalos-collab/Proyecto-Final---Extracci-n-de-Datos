# Análisis de Tendencias en la Agenda Ambiental Periodística de Mongabay Latam (2026)

## 📌 Pregunta de investigación
**¿Qué patrones emergen de los datos ambientales presentados en Mongabay Latam y qué significan para la región?**

---

## 📰 Fuente de datos
Los datos analizados provienen de **Mongabay Latam** (https://es.mongabay.com), medio periodístico especializado en temas ambientales y derechos humanos en América Latina.  
La información fue recolectada mediante **web scraping** a partir del feed RSS oficial del sitio.

---

## 🧪 Metodología
El proyecto aplica técnicas de ciencia de datos al periodismo ambiental y se desarrolló en las siguientes etapas:

1. **Extracción de datos**  
   Se realizó web scraping de artículos publicados en Mongabay Latam durante enero de 2026 utilizando Python y las librerías `requests`, `BeautifulSoup` y `pandas`.

2. **Construcción del dataset**  
   Se recopiló una muestra de **30 artículos**, extrayendo las siguientes variables:
   - título  
   - fecha de publicación  
   - autor  
   - texto completo  
   - país mencionado  
   - temática principal  
   - longitud del artículo (palabras y caracteres)

3. **Análisis de contenido**  
   Se aplicó análisis textual para identificar patrones temáticos, geográficos y narrativos, así como la frecuencia de palabras clave vinculadas a conflictos socioambientales.

---

## 🔍 Hallazgos  
### Tendencias Críticas en la Agenda Ambiental de Mongabay Latam (2026)

El análisis de los artículos permite identificar una radiografía de las tensiones actuales entre desarrollo industrial, política pública y conservación ambiental en América Latina.

### 1️⃣ ¿Qué significan los datos?
El hallazgo más relevante es la centralidad del eje **“Agua y contaminación”**, presente en **13 de los 30 artículos analizados**. Además, la palabra *“agua”* registra **144 menciones**, lo que indica que el recurso hídrico se ha convertido en un factor transversal del conflicto ambiental en la región.

Desde el punto de vista geográfico, **Argentina (9 artículos)** y **Bolivia (7 artículos)** concentran la cobertura periodística. Ambos países enfrentan crisis vinculadas a la gobernanza hídrica, la expansión del extractivismo y los conflictos territoriales, como los casos del Parque Nacional Aguaragüe o el pueblo indígena Ese Ejja.

La alta frecuencia de términos como *“indígenas”* (108 menciones) y *“comunidades”* (92 menciones) demuestra que la narrativa de Mongabay Latam no es exclusivamente ecológica, sino profundamente **sociopolítica**, vinculando la protección ambiental con los derechos humanos y la tenencia de la tierra.

---

### 2️⃣ Patrones identificados
Del cruce entre temáticas, países y palabras clave emergen tres patrones principales:

- **Bancarrota hídrica y extractivismo**  
  Existe una correlación directa entre la minería (litio, oro) y la crisis del agua. El análisis de texto muestra que términos como *“proyecto”*, *“inversiones”* y *“mercurio”* aparecen frecuentemente asociados a conflictos hídricos, evidenciando una doble presión: cambio climático y actividad industrial.

- **Judicialización de la conservación**  
  La recurrencia de términos como *“tratado”*, *“decreto”*, *“corte”* y *“sanciones”* indica un giro del periodismo ambiental hacia la cobertura de procesos judiciales y políticas públicas, como el Tratado de Altamar o el juicio por el asesinato del defensor ambiental Quinto Inuma.

- **Desplazamiento geográfico de la crisis ambiental**  
  Aunque la Amazonía sigue siendo relevante, se observa un desplazamiento de la atención periodística hacia el Cono Sur (Chile y Argentina), impulsado por incendios forestales de gran magnitud y la expansión de industrias como la salmonicultura.

---

## 📣 Relevancia para la comunicación y la sociedad
Desde el campo de la comunicación, los datos evidencian que la crisis ambiental ya no puede narrarse de manera aislada. La alta frecuencia de la palabra *“años”* (113 menciones) refleja un enfoque longitudinal que compara el presente con décadas pasadas, aportando contexto histórico y combatiendo la amnesia generacional en la comunicación científica.

Para la sociedad, la relevancia es de carácter estructural y existencial: el **43 % de la muestra se enfoca en el agua**, un recurso vital para la supervivencia humana. Un hallazgo destacado señala que por cada dólar invertido en proteger la naturaleza, se gastan 30 en actividades que la degradan, lo que traduce una abstracción científica en una urgencia económica y política.

---

## 📌 Conclusión
El análisis mediante web scraping muestra que el periodismo ambiental en 2026 cumple un rol fiscalizador de los sistemas políticos y económicos. La degradación ambiental no aparece como un accidente, sino como el resultado de decisiones estructurales que afectan de manera desproporcionada a los recursos hídricos y a las poblaciones indígenas de América Latina.

---

## ⚙️ Tecnologías utilizadas
- Python  
- Requests  
- BeautifulSoup  
- Pandas  

---

## 📁 Estructura del proyecto
