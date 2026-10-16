-- ============================================================
-- Historia Clínica de Ortodoncia - esquema de base de datos
-- Ejecutar en el SQL Editor de Neon. Se puede volver a ejecutar sin
-- perder datos.
-- ============================================================

-- ------------------------------------------------------------
-- Pacientes (sección 1. IDENTIFICACIÓN)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.pacientes (
    id                BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tipo_documento    TEXT NOT NULL DEFAULT 'CC',
    documento         TEXT NOT NULL UNIQUE,
    apellidos         TEXT NOT NULL,
    nombres           TEXT NOT NULL,
    fecha_nacimiento  DATE,
    genero            TEXT,
    telefono_fijo     TEXT,
    celular           TEXT,
    direccion         TEXT,
    correo            TEXT,
    acudiente         TEXT,
    documento_acudiente TEXT,
    creado_en         TIMESTAMPTZ NOT NULL DEFAULT now(),
    creado_por        TEXT,
    actualizado_en    TIMESTAMPTZ NOT NULL DEFAULT now(),
    actualizado_por   TEXT
);

CREATE INDEX IF NOT EXISTS idx_pacientes_nombre
    ON public.pacientes (lower(apellidos), lower(nombres));

-- ------------------------------------------------------------
-- Historias clínicas
-- Cada sección del formato se guarda como JSONB: el formato
-- puede cambiar sin migraciones y la estructura vive en
-- formulario.py.
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.historias (
    id                 BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    paciente_id        BIGINT NOT NULL REFERENCES public.pacientes(id) ON DELETE RESTRICT,
    fecha_apertura     DATE NOT NULL DEFAULT current_date,
    estado             TEXT NOT NULL DEFAULT 'ACTIVA'
                       CHECK (estado IN ('ACTIVA', 'FINALIZADA', 'SUSPENDIDA')),
    motivo_consulta    TEXT,
    anamnesis          JSONB NOT NULL DEFAULT '{}'::jsonb,
    examen_intraoral   JSONB NOT NULL DEFAULT '{}'::jsonb,
    periodontal        JSONB NOT NULL DEFAULT '{}'::jsonb,
    analisis_facial    JSONB NOT NULL DEFAULT '{}'::jsonb,
    cefalometrico      JSONB NOT NULL DEFAULT '{}'::jsonb,
    oclusion           JSONB NOT NULL DEFAULT '{}'::jsonb,
    funcional          JSONB NOT NULL DEFAULT '{}'::jsonb,
    diagnostico        JSONB NOT NULL DEFAULT '{}'::jsonb,
    plan_tratamiento   JSONB NOT NULL DEFAULT '{}'::jsonb,
    presupuesto        JSONB NOT NULL DEFAULT '{}'::jsonb,
    consentimiento     JSONB NOT NULL DEFAULT '{}'::jsonb,
    creado_en          TIMESTAMPTZ NOT NULL DEFAULT now(),
    creado_por         TEXT,
    actualizado_en     TIMESTAMPTZ NOT NULL DEFAULT now(),
    actualizado_por    TEXT
);

CREATE INDEX IF NOT EXISTS idx_historias_paciente
    ON public.historias (paciente_id);

-- ------------------------------------------------------------
-- Evolución del tratamiento (controles)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.evoluciones (
    id             BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    historia_id    BIGINT NOT NULL REFERENCES public.historias(id) ON DELETE CASCADE,
    fecha          DATE NOT NULL DEFAULT current_date,
    procedimiento  TEXT NOT NULL,
    es_control     BOOLEAN NOT NULL DEFAULT true,
    ortodoncista   TEXT,
    creado_en      TIMESTAMPTZ NOT NULL DEFAULT now(),
    creado_por     TEXT
);

CREATE INDEX IF NOT EXISTS idx_evoluciones_historia
    ON public.evoluciones (historia_id, fecha);

-- ------------------------------------------------------------
-- Pagos (abonos contra el presupuesto)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.pagos (
    id             BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    historia_id    BIGINT NOT NULL REFERENCES public.historias(id) ON DELETE CASCADE,
    fecha          DATE NOT NULL DEFAULT current_date,
    valor          NUMERIC(14, 2) NOT NULL CHECK (valor > 0),
    concepto       TEXT NOT NULL,
    medio_pago     TEXT,
    observaciones  TEXT,
    creado_en      TIMESTAMPTZ NOT NULL DEFAULT now(),
    creado_por     TEXT
);

CREATE INDEX IF NOT EXISTS idx_pagos_historia
    ON public.pagos (historia_id, fecha);

-- ------------------------------------------------------------
-- Usuarios que pueden ingresar. Se administran en la app
-- (Administración → Usuarios). La contraseña va cifrada con
-- bcrypt (pgcrypto). Perfiles: Administrador (también administra
-- los usuarios) y Usuario.
-- ------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS public.usuarios (
    email           TEXT PRIMARY KEY,
    nombre          TEXT,
    clave           TEXT NOT NULL,
    activo          BOOLEAN NOT NULL DEFAULT TRUE,
    creado          TIMESTAMPTZ NOT NULL DEFAULT now(),
    ultimo_ingreso  TIMESTAMPTZ
);
CREATE UNIQUE INDEX IF NOT EXISTS usuarios_email_minusculas ON public.usuarios (lower(email));

-- Código de usuario, perfil y última modificación (bases creadas antes
-- del módulo de usuarios: se agregan sin perder datos).
ALTER TABLE public.usuarios ADD COLUMN IF NOT EXISTS usuario     TEXT;
ALTER TABLE public.usuarios ADD COLUMN IF NOT EXISTS perfil      TEXT NOT NULL DEFAULT 'Usuario';
ALTER TABLE public.usuarios ADD COLUMN IF NOT EXISTS actualizado TIMESTAMPTZ;
UPDATE public.usuarios
   SET usuario = upper(regexp_replace(split_part(email, '@', 1), '[^A-Za-z0-9_.-]', '', 'g'))
 WHERE usuario IS NULL;
CREATE UNIQUE INDEX IF NOT EXISTS usuarios_usuario ON public.usuarios (usuario);
ALTER TABLE public.usuarios DROP CONSTRAINT IF EXISTS usuarios_perfil;
ALTER TABLE public.usuarios ADD CONSTRAINT usuarios_perfil CHECK (perfil IN ('Administrador', 'Usuario'));
-- Siempre debe haber un administrador: si no hay ninguno, lo es el usuario más antiguo.
UPDATE public.usuarios SET perfil = 'Administrador'
 WHERE email = (SELECT email FROM public.usuarios ORDER BY creado LIMIT 1)
   AND NOT EXISTS (SELECT 1 FROM public.usuarios WHERE perfil = 'Administrador');

-- ------------------------------------------------------------
-- Seguridad
-- La aplicación se conecta con el usuario dueño de las tablas
-- (no sujeto a RLS). Activar RLS SIN políticas impide que otros
-- roles o una API pública lean los datos clínicos.
-- ------------------------------------------------------------
ALTER TABLE public.pacientes   ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.historias   ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.evoluciones ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.pagos       ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.usuarios    ENABLE ROW LEVEL SECURITY;
