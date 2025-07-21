import streamlit as st
import sympy as sp
import matplotlib.pyplot as plt
import numpy as np
from sympy import nsolve

# Configuración
st.set_page_config(page_title="Calculadora de Cálculo", layout="centered")
st.title("🧮 Calculadora de Cálculo Diferencial")
st.markdown("Ingresa tu función y selecciona el tipo de ejercicio que deseas resolver.")

# Variable simbólica
x = sp.symbols('x')

# Entrada de función
func_str = st.text_input("✍️ Ingresa la función f(x):", value="sin(x)/x")
try:
    func = sp.sympify(func_str)
except:
    st.error("⚠️ La función no es válida.")
    st.stop()

# Tipos de cálculo
tipo = st.selectbox("📌 ¿Qué quieres calcular?", [
    "Límite",
    "Derivada de orden n",
    "Continuidad en un punto",
    "Puntos críticos y extremos locales",
    "Extremos globales en un intervalo"
])

# Parámetros según tipo
if tipo in ["Límite", "Continuidad en un punto"]:
    punto = st.number_input("📍 Ingresa el valor de x:", value=0.0)

if tipo == "Límite":
    lado = st.selectbox("👉 Lado del límite", ["Ambos lados", "Por la izquierda", "Por la derecha"])

if tipo == "Derivada de orden n":
    orden = st.number_input("📏 Orden de la derivada", min_value=1, max_value=100, value=1, step=1)

if tipo == "Extremos globales en un intervalo":
    a = st.number_input("🔽 Límite inferior del intervalo", value=-5)
    b = st.number_input("🔼 Límite superior del intervalo", value=5)

# Cálculo
if st.button("✅ Calcular"):
    try:
        st.subheader("🔍 Resultado")

        if tipo == "Límite":
            if lado == "Ambos lados":
                resultado = sp.limit(func, x, punto)
            elif lado == "Por la izquierda":
                resultado = sp.limit(func, x, punto, dir='-')
            else:
                resultado = sp.limit(func, x, punto, dir='+')
            st.latex(f"\\lim_{{x \\to {punto}}} f(x) = {sp.latex(resultado)}")

        elif tipo == "Derivada de orden n":
            derivada_n = sp.diff(func, x, int(orden))
            st.latex(f"f^{{({int(orden)})}}(x) = {sp.latex(derivada_n)}")

        elif tipo == "Continuidad en un punto":
            lim_izq = sp.limit(func, x, punto, dir='-')
            lim_der = sp.limit(func, x, punto, dir='+')
            valor_funcion = func.subs(x, punto)
            st.write(f"Límite por la izquierda: {lim_izq}")
            st.write(f"Límite por la derecha: {lim_der}")
            st.write(f"Valor de la función f({punto}) = {valor_funcion}")
            if lim_izq == lim_der == valor_funcion:
                st.success("✅ La función es continua en ese punto.")
            else:
                st.error("❌ La función NO es continua en ese punto.")

        elif tipo == "Puntos críticos y extremos locales":
            derivada_1 = sp.diff(func, x)
            derivada_2 = sp.diff(derivada_1, x)
            puntos_criticos = []

            try:
                puntos_criticos = sp.solve(derivada_1, x)
            except:
                st.warning("⚠️ No se pudieron encontrar soluciones simbólicas. Buscando raíces numéricas...")

                # Intentar encontrar raíces numéricas con nsolve
                iniciales = np.linspace(-10, 10, 20)
                soluciones_aprox = []
                for xi in iniciales:
                    try:
                        raiz = nsolve(derivada_1, x, xi)
                        soluciones_aprox.append(float(raiz.evalf()))
                    except:
                        continue

                # Eliminar duplicados por cercanía
                tolerancia = 1e-3
                unicas = []
                for r in soluciones_aprox:
                    if not any(abs(r - u) < tolerancia for u in unicas):
                        unicas.append(r)
                puntos_criticos = unicas

            st.write("📍 Puntos críticos:")
            for pc in puntos_criticos:
                try:
                    valor = func.subs(x, pc).evalf()
                    segunda_eval = derivada_2.subs(x, pc).evalf()
                    if segunda_eval.is_real:
                        if segunda_eval > 0:
                            tipo_ext = "mínimo local"
                        elif segunda_eval < 0:
                            tipo_ext = "máximo local"
                        else:
                            tipo_ext = "punto de inflexión"
                        st.write(f"x = {round(float(pc), 4)}, f(x) = {round(float(valor), 4)} → {tipo_ext}")
                    else:
                        st.write(f"x = {round(float(pc), 4)} → No se puede determinar la naturaleza.")
                except Exception as e:
                    st.write(f"x = {pc} → Error al evaluar: {e}")

        elif tipo == "Extremos globales en un intervalo":
            derivada = sp.diff(func, x)
            try:
                puntos_criticos = sp.solve(derivada, x)
            except:
                puntos_criticos = []

            extremos = []
            for pc in puntos_criticos:
                if pc.is_real and a <= float(pc.evalf()) <= b:
                    extremos.append(pc)

            extremos += [a, b]
            extremos = list(set(extremos))
            evaluaciones = [(float(p), float(func.subs(x, p).evalf())) for p in extremos]

            minimo = min(evaluaciones, key=lambda t: t[1])
            maximo = max(evaluaciones, key=lambda t: t[1])

            st.success(f"🔻 Mínimo global: f({minimo[0]}) = {minimo[1]}")
            st.success(f"🔺 Máximo global: f({maximo[0]}) = {maximo[1]}")

        # Gráfico
        st.subheader("📊 Gráfico de la función")
        f_lambdified = sp.lambdify(x, func, modules=["numpy"])
        x_vals = np.linspace(-10, 10, 400)
        try:
            y_vals = f_lambdified(x_vals)
            fig, ax = plt.subplots()
            ax.plot(x_vals, y_vals, label=f"f(x) = {func_str}")
            ax.axhline(0, color='gray', linewidth=1)
            ax.axvline(0, color='gray', linewidth=1)
            ax.set_title("Gráfico de f(x)")
            ax.legend()
            ax.grid(True)
            st.pyplot(fig)
        except:
            st.warning("⚠️ No se pudo graficar esta función numéricamente.")

        # Resumen
        st.subheader("📝 Resumen explicativo")
        if tipo == "Límite":
            st.markdown(f"Se calculó el **límite** de **f(x) = {func_str}** cuando x tiende a {punto}.")
        elif tipo == "Derivada de orden n":
            st.markdown(f"Se calculó la **derivada de orden {orden}** de la función **f(x) = {func_str}**.")
        elif tipo == "Continuidad en un punto":
            st.markdown(f"Se evaluó la **continuidad** de **f(x) = {func_str}** en x = {punto}.")
        elif tipo == "Puntos críticos y extremos locales":
            st.markdown(f"Se calcularon los **puntos críticos** y se clasificaron como máximos/mínimos locales.")
        elif tipo == "Extremos globales en un intervalo":
            st.markdown(f"Se evaluaron los extremos de la función **f(x) = {func_str}** en el intervalo [{a}, {b}].")

    except Exception as e:
        st.error(f"Ocurrió un error: {e}")
