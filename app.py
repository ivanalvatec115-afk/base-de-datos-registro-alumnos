import streamlit as st
import psycopg2
import pandas as pd

# ---------------- CONFIGURACIÓN BD ----------------
DB_CONFIG = {
    "host": "localhost",
    "database": "controlescolar",
    "user": "postgres",
    "password": "tu_password",
    "port": "5432"
}

CARRERAS = [
    "Ingenieria Sistemas Computacionales",
    "Ingenieria Civil",
    "Ingenieria en Mecatronica",
    "Ingenieria Quimica",
    "Administracion"
]

# ---------------- CONEXIÓN ----------------
def get_connection():
    return psycopg2.connect(**DB_CONFIG)

# ---------------- VALIDACIÓN MATRÍCULA ----------------
def validar_matricula(matricula):
    if not matricula.isdigit():
        return False, "La matrícula debe contener solo números"
    if len(matricula) != 8:
        return False, "La matrícula debe tener exactamente 8 dígitos"
    return True, ""

# ---------------- REGISTRAR ----------------
def registrar_alumno(matricula, nombre, ap_pat, ap_mat, carrera):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO alumnos
            (matricula, nombre, apellidopaterno, apellidomaterno, carrera)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (int(matricula), nombre, ap_pat, ap_mat, carrera)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True, "Alumno registrado correctamente"
    except psycopg2.errors.UniqueViolation:
        return False, "La matrícula ya existe"
    except Exception as e:
        return False, str(e)

# ---------------- CONSULTAR ----------------
def obtener_alumnos():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM alumnos ORDER BY matricula", conn)
    conn.close()
    return df

# ---------------- INTERFAZ ----------------
st.set_page_config(page_title="Control Escolar", page_icon="🎓")
st.title("🎓 Sistema de Control Escolar (PostgreSQL)")

menu = st.sidebar.selectbox(
    "Selecciona una opción",
    ["Registrar Alumno", "Consultar Alumnos"]
)

if menu == "Registrar Alumno":
    st.subheader("Registro de Alumno")

    matricula = st.text_input("Matrícula (8 dígitos)")
    nombre = st.text_input("Nombre")
    ap_pat = st.text_input("Apellido Paterno")
    ap_mat = st.text_input("Apellido Materno")
    carrera = st.selectbox("Carrera", CARRERAS)

    if st.button("Registrar"):
        if not matricula or not nombre or not ap_pat or not ap_mat:
            st.warning("Todos los campos son obligatorios")
        else:
            valida, mensaje = validar_matricula(matricula)
            if not valida:
                st.error(mensaje)
            else:
                ok, mensaje = registrar_alumno(
                    matricula, nombre, ap_pat, ap_mat, carrera
                )
                if ok:
                    st.success(mensaje)
                else:
                    st.error(mensaje)

elif menu == "Consultar Alumnos":
    st.subheader("Listado de Alumnos")

    try:
        df = obtener_alumnos()
        if df.empty:
            st.info("No hay alumnos registrados")
        else:
            st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Error al consultar: {e}")