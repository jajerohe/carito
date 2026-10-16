# Historia Clínica de Ortodoncia

Aplicación web (Streamlit + PostgreSQL en Neon) para gestionar la historia clínica de
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

1. **Base de datos.** En Neon (proyecto *carito*), abrir *SQL Editor* y
   ejecutar `sql/schema.sql`.
2. **Usuarios.** Cada persona que usará la app se crea en la tabla
   `usuarios` (la contraseña queda cifrada con bcrypt):

   ```sql
   INSERT INTO public.usuarios (email, nombre, clave)
   VALUES ('correo@dominio.com', 'Nombre', crypt('Contraseña', gen_salt('bf')));
   ```

   Para desactivar a alguien: `UPDATE public.usuarios SET activo = false WHERE email = '...';`
3. **Credenciales.** Copiar `.streamlit/secrets.toml.example` como
   `.streamlit/secrets.toml` y completar los datos (o pegarlos en *Secrets* de
   Streamlit Cloud).
4. **Ejecutar.**

   ```bash
   pip install -r requirements.txt
   streamlit run app.py
   ```

## Logo y fondo del inicio de sesión

- **Logo:** `logo.png` en la raíz del repositorio (se usa en la app y en el PDF).
- **Foto de fondo del inicio de sesión (opcional):** subir `fondo_login.jpg`
  (o `.png` / `.webp`) a la raíz. Se muestra detrás del logo con una capa
  clara encima. Recomendado: horizontal, menos de 500 KB.

## Cambiar el formato

Todas las preguntas del formulario están en `formulario.py`. Para agregar,
quitar o cambiar una pregunta basta con editar ese archivo: la pantalla y el
PDF se generan a partir de él y no hace falta tocar la base de datos.
Los textos legales (certificaciones, riesgos y compromisos del
consentimiento) están en `textos.py`.

## Seguridad de los datos

- Las tablas tienen RLS activado **sin políticas**, así ningún otro rol puede
  leer datos clínicos; la app usa la conexión directa a Postgres.
- Las contraseñas se guardan cifradas con bcrypt (pgcrypto), nunca en texto.
- Cada registro guarda quién lo creó y quién lo modificó por última vez.
- `secrets.toml` está en `.gitignore`: nunca debe subirse al repositorio.

## Pruebas

```bash
DATABASE_URL=postgresql://usuario@host:puerto/base_de_pruebas pytest
```

Usar una base de **pruebas** con `sql/schema.sql` aplicado (la prueba crea y
borra registros). Para revisar la interfaz sin iniciar sesión:
`DEV_SIN_LOGIN=1 DATABASE_URL=... streamlit run app.py`.
