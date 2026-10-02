# Historia Clínica de Ortodoncia

Aplicación web (Streamlit + Supabase) para gestionar la historia clínica de
ortodoncia, tomando como modelo el formato en papel del consultorio.

## Qué incluye

| Menú | Contenido |
|---|---|
| **Pacientes** | Registro, búsqueda por nombre o documento, edición y apertura de historias |
| **Historia clínica** | Fecha de apertura, estado, motivo de consulta, anamnesis (familiar, personal, odontológica), examen estomatológico y estado periodontal |
| **Anexo de ortodoncia** | Análisis facial, cefalométrico, de oclusión y funcional; resumen diagnóstico y objetivos; plan de tratamiento |
| **Presupuesto y pagos** | Presupuesto del formato, registro de abonos, total pagado y saldo pendiente |
| **Consentimiento** | Datos del consentimiento informado con el texto legal completo del formato |
| **Evolución** | Controles y procedimientos por fecha; controles realizados vs. proyectados |
| **Imprimir** | PDF para firmar: historia + anexo, consentimiento, hoja de evolución y estado de cuenta |

## Celular y tablet

La app funciona en el navegador del celular o la tablet, sin instalar nada:
el menú aparece arriba de cada pantalla junto con el paciente abierto.
Para tenerla como un ícono más en la pantalla de inicio:

- **Android (Chrome):** abrir la app → menú ⋮ → *Agregar a pantalla principal*.
- **iPhone / iPad (Safari):** abrir la app → botón Compartir → *Agregar a inicio*.

## Instalación

1. **Base de datos.** En Supabase, abrir *SQL Editor* y ejecutar
   `sql/schema.sql`.
2. **Usuarios.** En *Authentication > Users* crear el usuario de cada persona
   que usará la app (correo y contraseña). En *Authentication > Sign In /
   Providers* **desactivar "Allow new users to sign up"** para que nadie más
   pueda crear cuenta.
3. **Credenciales.** Copiar `.streamlit/secrets.toml.example` como
   `.streamlit/secrets.toml` y completar los datos (o pegarlos en *Secrets* de
   Streamlit Cloud).
4. **Ejecutar.**

   ```bash
   pip install -r requirements.txt
   streamlit run app.py
   ```

## Cambiar el formato

Todas las preguntas del formulario están en `formulario.py`. Para agregar,
quitar o cambiar una pregunta basta con editar ese archivo: la pantalla y el
PDF se generan a partir de él y no hace falta tocar la base de datos.
Los textos legales (certificaciones, riesgos y compromisos del
consentimiento) están en `textos.py`.

## Seguridad de los datos

- Las tablas tienen RLS activado **sin políticas**, así la API pública de
  Supabase no puede leer datos clínicos; la app usa la conexión directa a
  Postgres.
- Cada registro guarda quién lo creó y quién lo modificó por última vez.
- `secrets.toml` está en `.gitignore`: nunca debe subirse al repositorio.

## Pruebas

```bash
DATABASE_URL=postgresql://usuario@host:puerto/base_de_pruebas pytest
```

Usar una base de **pruebas** con `sql/schema.sql` aplicado (la prueba crea y
borra registros). Para revisar la interfaz sin Supabase Auth:
`DEV_SIN_LOGIN=1 DATABASE_URL=... streamlit run app.py`.
