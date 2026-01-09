import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt

# ---------------- CONFIGURACIÓN ----------------
st.set_page_config(
    page_title="Calculadora de Cálculo Diferencial",
    layout="centered"
)

st.title("🧮 Calculadora de Cálculo Diferencial")
st.markdown("Aplicación académica de análisis real (nivel universitario).")

# ---------------- SÍMBOLOS ----------------
x = sp.symbols("x", real=True)

# ---------------- ENTRADA FUNCIÓN ----------------
func_str = st.text_input("✍️ Ingresa la función f(x):", "sin(x)/x")

try:
    func = sp.sympify(func_str)
except Exception:
    st.error("⚠️ La función ingresada no es válida.")
    st.stop()

# ---------------- SELECCIÓN DE OPERACIÓN ----------------
tipo = st.selectbox(
    "📌 Selecciona el tipo de cálculo:",
    [
        "Límite",
        "Derivada de orden n",
        "Continuidad en un punto",
        "Extremos locales",
        "Extremos globales en un intervalo",
    ]
)

# ---------------- PARÁMETROS ----------------
if tipo in ["Límite", "Continuidad en un punto"]:
    punto = st.number_input("📍 Punto de evaluación", value=0.0)

if tipo == "Límite":
    lado = st.selectbox("👉 Dirección del límite", ["Ambos", "Izquierda", "Derecha"])

if tipo == "Derivada de orden n":
    orden = st.number_input("📏 Orden de la derivada", 1, 10, 2)

if tipo == "Extremos globales en un intervalo":
    a = st.number_input("🔽 Límite inferior", value=-5.0)
    b = st.number_input("🔼 Límite superior", value=5.0)

# ---------------- BOTÓN PRINCIPAL ----------------
if st.button("✅ Calcular"):
    st.subheader("🔍 Resultado")

    try:
        # ---------- LÍMITE ----------
        if tipo == "Límite":
            if lado == "Ambos":
                resultado = sp.limit(func, x, punto)
            elif lado == "Izquierda":
                resultado = sp.limit(func, x, punto, dir="-")
            else:
                resultado = sp.limit(func, x, punto, dir="+")

            st.latex(rf"\lim_{{x \to {punto}}} f(x) = {sp.latex(resultado)}")

        # ---------- DERIVADAS ----------
        elif tipo == "Derivada de orden n":
            derivadas = [func]
            for _ in range(int(orden)):
                derivadas.append(sp.diff(derivadas[-1], x))

            for i in range(1, len(derivadas)):
                st.latex(rf"f^{{({i})}}(x) = {sp.latex(derivadas[i])}")

            f_lambdas = [sp.lambdify(x, d, "numpy") for d in derivadas]
            x_vals = np.linspace(-10, 10, 400)

            fig, ax = plt.subplots()
            for i, f in enumerate(f_lambdas):
                ax.plot(x_vals, f(x_vals), label=f"Orden {i}")

            ax.legend()
            ax.grid()
            st.pyplot(fig)

        # ---------- CONTINUIDAD ----------
        elif tipo == "Continuidad en un punto":
            lim_izq = sp.limit(func, x, punto, dir="-")
            lim_der = sp.limit(func, x, punto, dir="+")
            valor = func.subs(x, punto)

            st.write("Límite por izquierda:", lim_izq)
            st.write("Límite por derecha:", lim_der)
            st.write("Valor de la función:", valor)

            tol = 1e-6
            if (
                sp.N(lim_izq - lim_der) == 0
                and sp.N(lim_izq - valor) == 0
            ):
                st.success("✅ La función es continua en el punto.")
            else:
                st.error("❌ La función NO es continua en el punto.")

        # ---------- EXTREMOS LOCALES ----------
        elif tipo == "Extremos locales":
            d1 = sp.diff(func, x)
            d2 = sp.diff(d1, x)

            criticos = sp.solve(d1, x)
            criticos = [c for c in criticos if c.is_real]

            st.write("📍 Puntos críticos:")
            for c in criticos:
                val2 = d2.subs(x, c)
                if val2 > 0:
                    tipo_ext = "Mínimo local"
                elif val2 < 0:
                    tipo_ext = "Máximo local"
                else:
                    tipo_ext = "Indeterminado"

                st.write(f"x = {c} → {tipo_ext}")

            f_l = sp.lambdify(x, func, "numpy")
            x_vals = np.linspace(-10, 10, 400)

            fig, ax = plt.subplots()
            ax.plot(x_vals, f_l(x_vals), label="f(x)")

            for c in criticos:
                ax.scatter(float(c), float(func.subs(x, c)), color="red")

            ax.legend()
            ax.grid()
            st.pyplot(fig)

        # ---------- EXTREMOS GLOBALES ----------
        elif tipo == "Extremos globales en un intervalo":
            d1 = sp.diff(func, x)
            criticos = sp.solve(d1, x)
            criticos = [c for c in criticos if c.is_real and a <= c <= b]

            candidatos = criticos + [a, b]

            valores = [(c, func.subs(x, c)) for c in candidatos]

            minimo = min(valores, key=lambda t: t[1])
            maximo = max(valores, key=lambda t: t[1])

            st.success(f"🔻 Mínimo global: f({minimo[0]}) = {minimo[1]}")
            st.success(f"🔺 Máximo global: f({maximo[0]}) = {maximo[1]}")

            f_l = sp.lambdify(x, func, "numpy")
            x_vals = np.linspace(a, b, 400)

            fig, ax = plt.subplots()
            ax.plot(x_vals, f_l(x_vals))
            ax.scatter([float(minimo[0])], [float(minimo[1])], color="green")
            ax.scatter([float(maximo[0])], [float(maximo[1])], color="red")
            ax.grid()
            st.pyplot(fig)

    except Exception as e:
        st.error(f"Error en el cálculo: {e}")
